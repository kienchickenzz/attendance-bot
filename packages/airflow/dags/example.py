# -*- coding: utf-8 -*-
# ========= IMPORTS =========


from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import execute_values
from pendulum import datetime, timezone

# các module ETL hiện có của bạn
from etl_dhnk import extract_and_compare as extract_dhnk, update_and_insert as update_dhnk
from etl_pnmh import extract_and_compare as extract_pnmh, update_and_insert as update_pnmh
from etl_ncvt import extract_and_compare as extract_ncvt, update_and_insert as update_ncvt

from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import execute_values

def _coerce_pairs(items):
    if not items: return []
    out = []
    for it in items:
        a=b=None
        if isinstance(it,(list,tuple)) and len(it)>=2:
            a,b = it[0], it[1]
        elif isinstance(it,dict):
            a = it.get("stt_rec") or it.get("nc_stt_rec") or it.get("dh_stt_rec") or it.get("pn_stt_rec")
            b = it.get("stt_rec0") or it.get("nc_stt_rec0") or it.get("dh_stt_rec0") or it.get("pn_stt_rec0")
        if a is None or b is None: continue
        out.append((str(a).strip(), str(b).strip()))
    return list({(a,b) for a,b in out})

def _pull_task_keys(ti, task_id: str):
    new_all, chg_all = [], []
    for k in ["new_keys", "changed_keys", "new_keys_ncvt", "changed_keys_ncvt",
              "new_keys_dhnk", "changed_keys_dhnk", "new_keys_pnmh", "changed_keys_pnmh"]:
        val = ti.xcom_pull(task_ids=task_id, key=k)
        if not val: continue
        if k.startswith("new_"):   new_all += _coerce_pairs(val)
        else:                      chg_all += _coerce_pairs(val)
    return new_all, chg_all

def apply_view_deltas(**kwargs):
    """
    INSERT ONLY NEW + UPDATE ONLY CHANGED từ materialized view sang master,
    không cần bk1/bk2 trong view. So khớp theo bất kỳ cặp khóa (NC hoặc DH hoặc PN).
    """
    ti = kwargs["ti"]
    # Lấy keys từ 3 nhánh
    new_nc, chg_nc = _pull_task_keys(ti, "update_and_insert_ncvt")
    new_dh, chg_dh = _pull_task_keys(ti, "update_and_insert_dhnk")
    new_pn, chg_pn = _pull_task_keys(ti, "update_and_insert_pnmh")

    new_keys = _coerce_pairs(new_nc + new_dh + new_pn)
    changed_keys = _coerce_pairs(chg_nc + chg_dh + chg_pn)

    pg = PostgresHook(postgres_conn_id="dwh_raw")
    conn = pg.get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT pg_advisory_xact_lock(hashtext('apply_view_deltas_v2'));")

        # Temp keys
        cur.execute("DROP TABLE IF EXISTS tmp_new_keys; CREATE TEMP TABLE tmp_new_keys(stt_rec text, stt_rec0 text) ON COMMIT DROP;")
        cur.execute("DROP TABLE IF EXISTS tmp_chg_keys; CREATE TEMP TABLE tmp_chg_keys(stt_rec text, stt_rec0 text) ON COMMIT DROP;")
        if new_keys:     execute_values(cur, "INSERT INTO tmp_new_keys VALUES %s", new_keys)
        if changed_keys: execute_values(cur, "INSERT INTO tmp_chg_keys VALUES %s", changed_keys)

        # INSERT ONLY NEW: lấy từ view theo keys (NC/DH/PN), chỉ insert khi chưa tồn tại dòng khớp theo ANY(NC/DH/PN)
        cur.execute("""
        WITH k_new AS (  -- chuẩn hoá keys mới (từ XCom)
          SELECT DISTINCT TRIM(stt_rec) AS k1, LPAD(TRIM(stt_rec0),3,'0') AS k2
          FROM tmp_new_keys
        ),
        v AS (           -- chuẩn hoá keys 6 cột phía view
          SELECT mv.*,
                 TRIM(mv.stt_rec_nc::text)              AS nc_1,
                 LPAD(TRIM(mv.stt_rec0_nc::text),   3,'0') AS nc_2,
                 TRIM(mv.stt_rec_dhnk::text)            AS dh_1,
                 LPAD(TRIM(mv.stt_rec0_dhnk::text), 3,'0') AS dh_2,
                 TRIM(mv.stt_rec_pnm::text)             AS pn_1,
                 LPAD(TRIM(mv.stt_rec0_pnm::text),  3,'0') AS pn_2,
                 COALESCE(mv.ngay_tt_hang_ve_kho, mv.ngay_dat_hang_theo_po, mv.ngay_nhan_ycnh) AS ts
          FROM mvw_masterdata_purchasing1 mv
        ),
        v_pick AS (      
          SELECT *
          FROM (
            SELECT v.*,
                   ROW_NUMBER() OVER (
                     PARTITION BY nc_1,nc_2,dh_1,dh_2,pn_1,pn_2
                     ORDER BY ts DESC,
                              so_phieu_nhap_mua DESC NULLS LAST,
                              so_ct_dhnk DESC NULLS LAST,
                              so_ycnh DESC NULLS LAST
                   ) AS rn
            FROM v
            WHERE
              -- chỉ lấy các dòng trong view có mặt trong tmp_new_keys theo bất kỳ cặp key
              EXISTS (SELECT 1 FROM k_new k WHERE v.nc_1 = k.k1 AND v.nc_2 = k.k2)
              OR EXISTS (SELECT 1 FROM k_new k WHERE v.dh_1 = k.k1 AND v.dh_2 = k.k2)
              OR EXISTS (SELECT 1 FROM k_new k WHERE v.pn_1 = k.k1 AND v.pn_2 = k.k2)
          ) s
          WHERE rn = 1
        )
        INSERT INTO masterdata_purchasing (stt,
          bo_chinh, stt_rec_nc, stt_rec0_nc, so_ycnh, ngay_nhan_ycnh, status_nc,
          ma_bp, cbkd, cust_id, ma_vv, so_luong_nc,
          don_gia_yc_usd, thanh_tien_yc_usd, don_gia_yc_vnd, thanh_tien_yc_vnd,
          ghi_chu_nc, ma_nt_nc, ty_gia_nc, mo_ta_hang_hoa, thoi_gian_bao_hanh,
          xuat_xu, stt_rec_dhnk, stt_rec0_dhnk, so_ct_dhnk, ma_kh,
          ngay_dat_hang_theo_po, ngay_du_kien_giao_hang_theo_po, status_dhnk,
          cb_dat_hang, so_po_dh, trang_thai_po, tinh_trang_po, ma_nt_dh, ty_gia_dh,
          type, ghi_chu_dh, so_luong_dh,
          don_gia_thuc_te_usd, thanh_tien_thuc_te_usd, don_gia_thuc_te_vnd, thanh_tien_thuc_te_vnd,
          ten_thiet_bi_dh, ma_hang_chinh_pi, nh_sp1, nh_sp2,
          stt_rec_pnm, stt_rec0_pnm, so_phieu_nhap_mua, ngay_tt_hang_ve_kho,
          stt_rec_dh, stt_rec0dh, so_luong_pnm, sl_hd, status_pnm,
          up_yn, thuc_giam
        )
        SELECT p.stt,
          p.bo_chinh, p.stt_rec_nc, p.stt_rec0_nc, p.so_ycnh, p.ngay_nhan_ycnh, p.status_nc,
          p.ma_bp, p.cbkd, p.cust_id, p.ma_vv, p.so_luong_nc,
          p.don_gia_yc_usd, p.thanh_tien_yc_usd, p.don_gia_yc_vnd, p.thanh_tien_yc_vnd,
          p.ghi_chu_nc, p.ma_nt_nc, p.ty_gia_nc, p.mo_ta_hang_hoa, p.thoi_gian_bao_hanh,
          p.xuat_xu_nc,
          p.stt_rec_dhnk, p.stt_rec0_dhnk, p.so_ct_dhnk, p.ma_kh,
          p.ngay_dat_hang_theo_po, p.ngay_du_kien_giao_hang_theo_po, p.status_dhnk,
          p.cb_dat_hang, p.so_po_hd, p.trang_thai_po, p.tinh_trang_po, p.ma_nt_dh, p.ty_gia_dh,
          p.type, p.ghi_chu_dh, p.so_luong_dh,
          p.don_gia_thuc_te_usd, p.thanh_tien_thuc_te_usd, p.don_gia_thuc_te_vnd, p.thanh_tien_thuc_te_vnd,
          p.ten_thiet_bi_dh, p.ma_hang_chinh_pi, p.nh_sp1, p.nh_sp2,
          p.stt_rec_pnm, p.stt_rec0_pnm, p.so_phieu_nhap_mua, p.ngay_tt_hang_ve_kho,
          p.stt_rec_dh, p.stt_rec0dh, p.so_luong_pnm, p.sl_hd, p.status_pnm,
          p.up_yn, p.thuc_giam
        FROM v_pick p
        WHERE
         
          NOT EXISTS (
            SELECT 1
            FROM masterdata_purchasing m
            WHERE (m.stt_rec_nc    IS NOT DISTINCT FROM p.nc_1)
              AND (m.stt_rec0_nc   IS NOT DISTINCT FROM p.nc_2)
              AND (m.stt_rec_dhnk  IS NOT DISTINCT FROM p.dh_1)
              AND (m.stt_rec0_dhnk IS NOT DISTINCT FROM p.dh_2)
              AND (m.stt_rec_pnm   IS NOT DISTINCT FROM p.pn_1)
              AND (m.stt_rec0_pnm  IS NOT DISTINCT FROM p.pn_2)
          );
        """)

        
        cur.execute("""
        WITH k_upd AS (
          SELECT DISTINCT TRIM(stt_rec) k1, LPAD(TRIM(stt_rec0),3,'0') k2 FROM tmp_chg_keys
        ),
        v AS (
          SELECT mv.*,
                 TRIM(mv.stt_rec_pnm::text)  AS pn_1,
                 LPAD(TRIM(mv.stt_rec0_pnm::text),3,'0') AS pn_2
          FROM mvw_masterdata_purchasing1 mv
        )
        UPDATE masterdata_purchasing m
        SET
          bo_chinh                  = v.bo_chinh,
          so_ycnh                   = v.so_ycnh,
          ngay_nhan_ycnh            = v.ngay_nhan_ycnh,
          status_nc                 = v.status_nc,
          ma_bp                     = v.ma_bp,
          cbkd                      = v.cbkd,
          cust_id                   = v.cust_id,
          ma_vv                     = v.ma_vv,
          so_luong_nc               = v.so_luong_nc,
          don_gia_yc_usd            = v.don_gia_yc_usd,
          thanh_tien_yc_usd         = v.thanh_tien_yc_usd,
          don_gia_yc_vnd            = v.don_gia_yc_vnd,
          thanh_tien_yc_vnd         = v.thanh_tien_yc_vnd,
          ghi_chu_nc                = v.ghi_chu_nc,
          ma_nt_nc                  = v.ma_nt_nc,
          ty_gia_nc                 = v.ty_gia_nc,
          mo_ta_hang_hoa            = v.mo_ta_hang_hoa,
          thoi_gian_bao_hanh        = v.thoi_gian_bao_hanh,
          xuat_xu                   = v.xuat_xu_nc,

          stt_rec_dhnk              = v.stt_rec_dhnk,
          stt_rec0_dhnk             = v.stt_rec0_dhnk,
          so_ct_dhnk                = v.so_ct_dhnk,
          ma_kh                     = v.ma_kh,
          ngay_dat_hang_theo_po     = v.ngay_dat_hang_theo_po,
          ngay_du_kien_giao_hang_theo_po = v.ngay_du_kien_giao_hang_theo_po,
          status_dhnk               = v.status_dhnk,
          cb_dat_hang               = v.cb_dat_hang,
          so_po_dh                  = v.so_po_hd,
          trang_thai_po             = v.trang_thai_po,
          tinh_trang_po             = v.tinh_trang_po,
          ma_nt_dh                  = v.ma_nt_dh,
          ty_gia_dh                 = v.ty_gia_dh,
          type                      = v.type,
          ghi_chu_dh                = v.ghi_chu_dh,
          so_luong_dh               = v.so_luong_dh,
          don_gia_thuc_te_usd       = v.don_gia_thuc_te_usd,
          thanh_tien_thuc_te_usd    = v.thanh_tien_thuc_te_usd,
          don_gia_thuc_te_vnd       = v.don_gia_thuc_te_vnd,
          thanh_tien_thuc_te_vnd    = v.thanh_tien_thuc_te_vnd,
          ten_thiet_bi_dh           = v.ten_thiet_bi_dh,
          ma_hang_chinh_pi          = v.ma_hang_chinh_pi,
          nh_sp1                    = v.nh_sp1,
          nh_sp2                    = v.nh_sp2,

          stt_rec_pnm               = v.stt_rec_pnm,
          stt_rec0_pnm              = v.stt_rec0_pnm,
          so_phieu_nhap_mua         = v.so_phieu_nhap_mua,
          ngay_tt_hang_ve_kho       = v.ngay_tt_hang_ve_kho,
          stt_rec_dh                = v.stt_rec_dh,
          stt_rec0dh                = v.stt_rec0dh,
          so_luong_pnm              = v.so_luong_pnm,
          sl_hd                     = v.sl_hd,
          status_pnm                = v.status_pnm,

          up_yn                     = v.up_yn,
          thuc_giam                 = v.thuc_giam
        FROM v
        JOIN k_upd k ON v.pn_1 = k.k1 AND v.pn_2 = k.k2
        WHERE m.stt_rec_pnm = v.pn_1 AND m.stt_rec0_pnm = v.pn_2;
        """)

        # 2) UPDATE theo DH (chỉ các dòng KHÔNG có PN trong view)
        cur.execute("""
        WITH k_upd AS (
          SELECT DISTINCT TRIM(stt_rec) k1, LPAD(TRIM(stt_rec0),3,'0') k2 FROM tmp_chg_keys
        ),
        v AS (
          SELECT mv.*,
                 TRIM(mv.stt_rec_dhnk::text) AS dh_1,
                 LPAD(TRIM(mv.stt_rec0_dhnk::text),3,'0') AS dh_2,
                 TRIM(mv.stt_rec_pnm::text)  AS pn_1
          FROM mvw_masterdata_purchasing1 mv
        )
        UPDATE masterdata_purchasing m
        SET
          bo_chinh                  = v.bo_chinh,
          so_ycnh                   = v.so_ycnh,
          ngay_nhan_ycnh            = v.ngay_nhan_ycnh,
          status_nc                 = v.status_nc,
          ma_bp                     = v.ma_bp,
          cbkd                      = v.cbkd,
          cust_id                   = v.cust_id,
          ma_vv                     = v.ma_vv,
          so_luong_nc               = v.so_luong_nc,
          don_gia_yc_usd            = v.don_gia_yc_usd,
          thanh_tien_yc_usd         = v.thanh_tien_yc_usd,
          don_gia_yc_vnd            = v.don_gia_yc_vnd,
          thanh_tien_yc_vnd         = v.thanh_tien_yc_vnd,
          ghi_chu_nc                = v.ghi_chu_nc,
          ma_nt_nc                  = v.ma_nt_nc,
          ty_gia_nc                 = v.ty_gia_nc,
          mo_ta_hang_hoa            = v.mo_ta_hang_hoa,
          thoi_gian_bao_hanh        = v.thoi_gian_bao_hanh,
          xuat_xu                   = v.xuat_xu_nc,

          stt_rec_dhnk              = v.stt_rec_dhnk,
          stt_rec0_dhnk             = v.stt_rec0_dhnk,
          so_ct_dhnk                = v.so_ct_dhnk,
          ma_kh                     = v.ma_kh,
          ngay_dat_hang_theo_po     = v.ngay_dat_hang_theo_po,
          ngay_du_kien_giao_hang_theo_po = v.ngay_du_kien_giao_hang_theo_po,
          status_dhnk               = v.status_dhnk,
          cb_dat_hang               = v.cb_dat_hang,
          so_po_dh                  = v.so_po_hd,
          trang_thai_po             = v.trang_thai_po,
          tinh_trang_po             = v.tinh_trang_po,
          ma_nt_dh                  = v.ma_nt_dh,
          ty_gia_dh                 = v.ty_gia_dh,
          type                      = v.type,
          ghi_chu_dh                = v.ghi_chu_dh,
          so_luong_dh               = v.so_luong_dh,
          don_gia_thuc_te_usd       = v.don_gia_thuc_te_usd,
          thanh_tien_thuc_te_usd    = v.thanh_tien_thuc_te_usd,
          don_gia_thuc_te_vnd       = v.don_gia_thuc_te_vnd,
          thanh_tien_thuc_te_vnd    = v.thanh_tien_thuc_te_vnd,
          ten_thiet_bi_dh           = v.ten_thiet_bi_dh,
          ma_hang_chinh_pi          = v.ma_hang_chinh_pi,
          nh_sp1                    = v.nh_sp1,
          nh_sp2                    = v.nh_sp2,

          stt_rec_pnm               = v.stt_rec_pnm,
          stt_rec0_pnm              = v.stt_rec0_pnm,
          so_phieu_nhap_mua         = v.so_phieu_nhap_mua,
          ngay_tt_hang_ve_kho       = v.ngay_tt_hang_ve_kho,
          stt_rec_dh                = v.stt_rec_dh,
          stt_rec0dh                = v.stt_rec0dh,
          so_luong_pnm              = v.so_luong_pnm,
          sl_hd                     = v.sl_hd,
          status_pnm                = v.status_pnm,

          up_yn                     = v.up_yn,
          thuc_giam                 = v.thuc_giam
        FROM v
        JOIN k_upd k ON v.dh_1 = k.k1 AND v.dh_2 = k.k2
        WHERE v.pn_1 IS NULL
          AND m.stt_rec_dhnk = v.dh_1 AND m.stt_rec0_dhnk = v.dh_2;
        """)

        # 3) UPDATE theo NC (chỉ các dòng KHÔNG có PN/DH trong view)
        cur.execute("""
        WITH k_upd AS (
          SELECT DISTINCT TRIM(stt_rec) k1, LPAD(TRIM(stt_rec0),3,'0') k2 FROM tmp_chg_keys
        ),
        v AS (
          SELECT mv.*,
                 TRIM(mv.stt_rec_nc::text)  AS nc_1,
                 LPAD(TRIM(mv.stt_rec0_nc::text),3,'0') AS nc_2,
                 TRIM(mv.stt_rec_dhnk::text) AS dh_1,
                 TRIM(mv.stt_rec_pnm::text)  AS pn_1
          FROM mvw_masterdata_purchasing1 mv
        )
        UPDATE masterdata_purchasing m
        SET
          bo_chinh                  = v.bo_chinh,
          so_ycnh                   = v.so_ycnh,
          ngay_nhan_ycnh            = v.ngay_nhan_ycnh,
          status_nc                 = v.status_nc,
          ma_bp                     = v.ma_bp,
          cbkd                      = v.cbkd,
          cust_id                   = v.cust_id,
          ma_vv                     = v.ma_vv,
          so_luong_nc               = v.so_luong_nc,
          don_gia_yc_usd            = v.don_gia_yc_usd,
          thanh_tien_yc_usd         = v.thanh_tien_yc_usd,
          don_gia_yc_vnd            = v.don_gia_yc_vnd,
          thanh_tien_yc_vnd         = v.thanh_tien_yc_vnd,
          ghi_chu_nc                = v.ghi_chu_nc,
          ma_nt_nc                  = v.ma_nt_nc,
          ty_gia_nc                 = v.ty_gia_nc,
          mo_ta_hang_hoa            = v.mo_ta_hang_hoa,
          thoi_gian_bao_hanh        = v.thoi_gian_bao_hanh,
          xuat_xu                   = v.xuat_xu_nc,

          stt_rec_dhnk              = v.stt_rec_dhnk,
          stt_rec0_dhnk             = v.stt_rec0_dhnk,
          so_ct_dhnk                = v.so_ct_dhnk,
          ma_kh                     = v.ma_kh,
          ngay_dat_hang_theo_po     = v.ngay_dat_hang_theo_po,
          ngay_du_kien_giao_hang_theo_po = v.ngay_du_kien_giao_hang_theo_po,
          status_dhnk               = v.status_dhnk,
          cb_dat_hang               = v.cb_dat_hang,
          so_po_dh                  = v.so_po_hd,
          trang_thai_po             = v.trang_thai_po,
          tinh_trang_po             = v.tinh_trang_po,
          ma_nt_dh                  = v.ma_nt_dh,
          ty_gia_dh                 = v.ty_gia_dh,
          type                      = v.type,
          ghi_chu_dh                = v.ghi_chu_dh,
          so_luong_dh               = v.so_luong_dh,
          don_gia_thuc_te_usd       = v.don_gia_thuc_te_usd,
          thanh_tien_thuc_te_usd    = v.thanh_tien_thuc_te_usd,
          don_gia_thuc_te_vnd       = v.don_gia_thuc_te_vnd,
          thanh_tien_thuc_te_vnd    = v.thanh_tien_thuc_te_vnd,
          ten_thiet_bi_dh           = v.ten_thiet_bi_dh,
          ma_hang_chinh_pi          = v.ma_hang_chinh_pi,
          nh_sp1                    = v.nh_sp1,
          nh_sp2                    = v.nh_sp2,

          stt_rec_pnm               = v.stt_rec_pnm,
          stt_rec0_pnm              = v.stt_rec0_pnm,
          so_phieu_nhap_mua         = v.so_phieu_nhap_mua,
          ngay_tt_hang_ve_kho       = v.ngay_tt_hang_ve_kho,
          stt_rec_dh                = v.stt_rec_dh,
          stt_rec0dh                = v.stt_rec0dh,
          so_luong_pnm              = v.so_luong_pnm,
          sl_hd                     = v.sl_hd,
          status_pnm                = v.status_pnm,

          up_yn                     = v.up_yn,
          thuc_giam                 = v.thuc_giam
        FROM v
        JOIN k_upd k ON v.nc_1 = k.k1 AND v.nc_2 = k.k2
        WHERE v.pn_1 IS NULL AND v.dh_1 IS NULL
          AND m.stt_rec_nc = v.nc_1 AND m.stt_rec0_nc = v.nc_2;
        """)

        conn.commit()
        print(f"[apply_view_deltas_v2] new={len(new_keys)} changed={len(changed_keys)}")
    finally:
        try: cur.close()
        except Exception: pass
        try: conn.close()
        except Exception: pass


def refresh_mview():
    hook = PostgresHook(postgres_conn_id="dwh_raw")
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute("REFRESH MATERIALIZED VIEW mvw_masterdata_purchasing1")
    conn.commit()
    cursor.close()
    conn.close()

# ========= DAG =========
from airflow import DAG
from pendulum import datetime, timezone

with (DAG(
    dag_id="etl_fast_all_hash",
    start_date=datetime(2024, 1, 1, 6, 45, tz=timezone("Asia/Ho_Chi_Minh")),
    schedule="45 6,9,11,14,16,17 * * *",
    catchup=False,
    tags=["etl", "compare"],
) as dag):

    # 1) Extract & update
    t1_dhnk = PythonOperator(
        task_id="extract_and_compare_dhnk",
        python_callable=extract_dhnk,
        op_kwargs={"start_yyyymm": 202404, "hook_driver": "ODBC Driver 18 for SQL Server"},
    )
    t2_dhnk = PythonOperator(
        task_id="update_and_insert_dhnk",
        python_callable=update_dhnk,
        op_kwargs={"task_ids_prefix": "extract_and_compare_dhnk"},
        provide_context=True,
    )

    t1_pnmh = PythonOperator(
        task_id="extract_and_compare_pnmh",
        python_callable=extract_pnmh,
        op_kwargs={"start_yyyymm": 202404, "hook_driver": "ODBC Driver 18 for SQL Server"},
    )
    t2_pnmh = PythonOperator(
        task_id="update_and_insert_pnmh",
        python_callable=update_pnmh,
        op_kwargs={"task_ids_prefix": "extract_and_compare_pnmh"},
        provide_context=True,
    )

    t1_ncvt = PythonOperator(
        task_id="extract_and_compare_ncvt",
        python_callable=extract_ncvt,
        op_kwargs={"start_yyyymm": 202404, "hook_driver": "ODBC Driver 18 for SQL Server"},
    )
    t2_ncvt = PythonOperator(
        task_id="update_and_insert_ncvt",
        python_callable=update_ncvt,
        op_kwargs={"task_ids_prefix": "extract_and_compare_ncvt"},
        provide_context=True,
    )

    # 2) Refresh mview
    t_refresh_view = PythonOperator(
        task_id="refresh_mview",
        python_callable=refresh_mview,
    )

    # 3) Apply deltas từ view -> master
    t_apply_view = PythonOperator(
        task_id="apply_view_deltas",
        python_callable=apply_view_deltas,
        provide_context=True,
    )

    # Flow
    t1_dhnk >> t2_dhnk >> t1_pnmh >> t2_pnmh >> t1_ncvt >> t2_ncvt  >>t_refresh_view >> t_apply_view
