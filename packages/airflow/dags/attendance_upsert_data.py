from airflow.operators.python import PythonOperator
from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook, DictCursor

import requests
from datetime import datetime, date
import time
import os
import logging
import asyncio
from collections import defaultdict

import json


import sys
import os

current_dir = os.path.dirname( os.path.abspath( __file__ ) )
if current_dir not in sys.path:
    sys.path.append( current_dir )


from utils import process_daily_attendance
from constants import SHIFT_CONFIG, FREE_PER_MONTH


API_URL = 'https://ctsfaceid.cmcts.com.vn/api/timekeeping/short/tshn'
START_DATE = '2025-08-01T00:00:00Z'
END_DATE = '2025-08-31T23:59:59Z'
FREE_PER_MONTH = 5
CONNECTION_ID = "attendance"


def _call_api() -> list[ dict[ str, str ] ]:
    try:
        logging.info( f"Calling API: { API_URL }" )
        
        response = requests.get(
            f'{ API_URL }/{ START_DATE }/{ END_DATE }',
            timeout=30,
            headers={ 'Content-Type': 'application/json' }
        )
        
        # Check if request was successful
        response.raise_for_status()
        logging.info( f"✅ API call successful!" )

        data = response.json()
        return data

        # current_dir = os.path.dirname( os.path.abspath( __file__ ) )
        # json_path = os.path.join( current_dir, 'data.json' )
        # with open( json_path, 'r', encoding='utf-8' ) as f:
        #     data = json.load( f )
        # events = data[ 'return_events' ]
            
    except Exception as e:
        logging.info(f"❌ Error: {e}")
        raise e

async def _get_existing_data(
    conn, 
    employee_ids: list[ str ], 
    target_date: date
) -> dict[ str, dict ]:
    
    cur = conn.cursor( cursor_factory=DictCursor )
    
    if not employee_ids:
        return {}
    
    try:
        query = """SELECT employee_id, first_in, last_out 
            FROM attendance_raw 
            WHERE employee_id = ANY(%s) AND date = %s
        """
        params = [ employee_ids, target_date ]
        cur.execute( query, params )
        rows = cur.fetchall()
        if not rows:
            return {}
        
        existing_data = {}
        for row in rows:
            existing_data[ row[ "employee_id" ] ] = {
                "first_in": row[ "first_in" ],
                "last_out": row[ "last_out" ]
            }

        return existing_data
    finally:
        cur.close()
    
async def _get_employee_ids_by_emails(
    conn, 
    emails: list[ str ]
) -> dict[ str, str ]:
    
    cur = conn.cursor( cursor_factory=DictCursor )

    if not emails:
        return {}

    query = """
        SELECT email, employee_id 
        FROM employees 
        WHERE email = ANY(%s)
    """
    params = [ emails ]

    cur.execute( query, params )
    rows = cur.fetchall()
    if not rows:
        return {}

    email_to_id = {}
    for row in rows:
        email_to_id[ row[ "email" ] ] = row[ "employee_id" ]

    return email_to_id

async def _get_all_leaves_info(
    conn,
    employee_ids: list[str],
    target_date: date
) -> dict[str, tuple[bool, bool, str]]:
    
    cur = conn.cursor( cursor_factory=DictCursor )
    
    if not employee_ids:
        return {}
    
    leave_query = """SELECT employee_id, time_type, leave_reason 
FROM leaves 
WHERE employee_id = ANY(%s) AND date = %s
"""
    cur.execute(
        leave_query, [employee_ids, target_date]
    )
    rows = cur.fetchall()

    leaves_info = {}
    
    # Initialize all employees with default values
    for employee_id in employee_ids:
        leaves_info[employee_id] = (False, False, "normal")
    
    # Update with actual leave data
    for row in rows:
        employee_id = row["employee_id"]
        time_type = row["time_type"]
        
        is_leave_morning = False
        is_leave_afternoon = False
        shift_type = "normal"
        
        if time_type == "fullday":
            shift_type = "leave_full_day"
            is_leave_morning = True
            is_leave_afternoon = True
        elif time_type == "morning":
            shift_type = "leave_morning"
            is_leave_morning = True
        elif time_type == "afternoon":
            shift_type = "leave_afternoon"
            is_leave_afternoon = True
            
        leaves_info[employee_id] = (is_leave_morning, is_leave_afternoon, shift_type)
    
    return leaves_info

async def _get_all_free_allowances(
    conn,
    employee_ids: list[str],
    target_date: date,
    free_per_month: int
) -> dict[str, int]:
    
    cur = conn.cursor( cursor_factory=DictCursor )
    
    if not employee_ids:
        return {}
    
    # Determine canonical year_month according to business rule:
    # - A logical "month" runs from the 26th of the previous calendar month
    #   through the 25th of the calendar month.
    # - Any date with day >= 26 belongs to the next canonical month.
    if target_date.day >= 26:
        # move to first day of next month
        if target_date.month == 12:
            year_month = target_date.replace( year=target_date.year + 1, month=1, day=1 )
        else:
            year_month = target_date.replace( month=target_date.month + 1, day=1 )
    else:
        # canonical month is current calendar month
        year_month = target_date.replace( day=1 )

    free_query = """
        SELECT employee_id, used_count 
        FROM monthly_free_usage 
        WHERE employee_id = ANY(%s) AND year_month = %s
    """
    cur.execute( free_query, [ employee_ids, year_month ] )
    rows = cur.fetchall()

    free_allowances = {}
    
    # Initialize all employees with full free allowance
    for employee_id in employee_ids:
        free_allowances[ employee_id ] = free_per_month
    
    # Update with actual used counts
    for row in rows:
        employee_id = row[ "employee_id" ]
        used_count = row[ "used_count" ]
        free_allowance = max( 0, free_per_month - used_count )
        free_allowances[ employee_id ] = free_allowance

    return free_allowances

async def _batch_upsert_data(
    conn,
    batch_data: dict,
    target_date: date
) -> None:

    cur = conn.cursor( cursor_factory=DictCursor )

    try:
        # 1. Batch insert/update attendance table
        if batch_data[ "attendance_params" ]:
            attendance_upsert_query = """
                INSERT INTO attendance (
                    employee_id, date, raw_check_in, raw_check_out, raw_data_version, shift_start, shift_end, late_minutes, early_minutes,
                    penalty_hours, is_leave, is_free_used, calculated_by, calculation_duration_ms, business_rules_version
                ) VALUES %s
                ON CONFLICT (employee_id, date) DO UPDATE SET
                    raw_check_in = EXCLUDED.raw_check_in,
                    raw_check_out = EXCLUDED.raw_check_out,
                    raw_data_version = COALESCE(attendance.raw_data_version, 0) + 1,
                    shift_start = EXCLUDED.shift_start,
                    shift_end = EXCLUDED.shift_end,
                    late_minutes = EXCLUDED.late_minutes,
                    early_minutes = EXCLUDED.early_minutes,
                    penalty_hours = EXCLUDED.penalty_hours,
                    is_holiday = EXCLUDED.is_holiday,
                    is_leave = EXCLUDED.is_leave,
                    is_free_used = EXCLUDED.is_free_used,
                    calculated_by = EXCLUDED.calculated_by,
                    calculation_duration_ms = EXCLUDED.calculation_duration_ms,
                    calculated_at = CURRENT_TIMESTAMP,
                    business_rules_version = EXCLUDED.business_rules_version
            """
            
            from psycopg2.extras import execute_values
            execute_values(
                cur,
                attendance_upsert_query,
                batch_data["attendance_params"],
                template=None,
                page_size=1000
            )
            logging.info(f"✅ Batch upsert {len(batch_data['attendance_params'])} records vào attendance table ngày {target_date}")
        
        # 2. Batch insert/update attendance_raw table  
        if batch_data["attendance_raw_params"]:
            raw_upsert_query = """
                INSERT INTO attendance_raw (
                    employee_id, date, first_in, last_out, processed_at
                ) VALUES %s
                ON CONFLICT (employee_id, date) DO UPDATE SET
                    first_in = EXCLUDED.first_in,
                    last_out = EXCLUDED.last_out,
                    data_version = attendance_raw.data_version + 1,
                    last_updated = CURRENT_TIMESTAMP,
                    processed_at = CURRENT_TIMESTAMP,
                    process_attempts = attendance_raw.process_attempts + 1
            """
            
            execute_values(
                cur,
                raw_upsert_query,
                batch_data["attendance_raw_params"],
                template=None,
                page_size=1000
            )
            logging.info(f"✅ Batch upsert {len(batch_data['attendance_raw_params'])} records vào attendance_raw table ngày {target_date}")
        
        # 3. Batch update monthly_free_usage
        if batch_data["free_usage_updates"]:
            for employee_id, year_month in batch_data["free_usage_updates"]:
                update_query = """
                    UPDATE monthly_free_usage 
                    SET used_count = used_count + 1 
                    WHERE employee_id = %s AND year_month = %s
                """
                cur.execute( update_query, [ employee_id, year_month ] )
            
            logging.info(f"✅ Batch update {len(batch_data['free_usage_updates'])} records trong monthly_free_usage")
        
        # Commit transaction
        conn.commit()
        logging.info(f"✅ Batch transaction committed cho ngày {target_date}")
        
    except Exception as e:
        # Rollback transaction on error
        conn.rollback()
        logging.error(f"❌ Batch transaction rollback cho ngày {target_date}: {e}")
        raise
    finally:
        cur.close()

async def upsert_data_async():
    pg = PostgresHook( postgres_conn_id=CONNECTION_ID )
    conn = pg.get_conn()
    logging.info( "✅ Kết nối thành công!" )

    try:
        # TODO: Add comments mô tả về định dạng dữ liệu trả về từ API
        raw_data = _call_api()

        # Gom record theo ngày
        date_to_records = defaultdict( list )
        for record in raw_data:
            date_obj = datetime.strptime( record[ "first_in" ], "%Y-%m-%d %H:%M" ).date()
            date_to_records[ date_obj ].append( record )

        # Xử lý từng ngày một
        for date_obj, records in date_to_records.items():
            target_date = date_obj
            logging.info( f"====== { target_date } ======" )

            # Lấy danh sách email trong ngày này
            emails = [ r[ "email" ] for r in records if r.get( "email" ) ]
            email_to_id = await _get_employee_ids_by_emails( conn, emails )
            logging.info( f"Found { len( email_to_id ) } employee_ids for { len( emails ) } emails" )
            employee_ids = list( email_to_id.values() )

            if not employee_ids:
                logging.info("⚠️ Không tìm thấy employee_id nào trong DB cho ngày này.")
                continue

            # Lấy dữ liệu cũ trong DB cho ngày này
            existing_data_map = await _get_existing_data( conn, employee_ids, target_date )
            
            # Lấy toàn bộ thông tin cho các employee_ids ngay từ đầu
            leaves_data = await _get_all_leaves_info( conn, employee_ids, target_date )
            free_allowances_data = await _get_all_free_allowances( conn, employee_ids, target_date, FREE_PER_MONTH )
            
            # Cấu trúc dữ liệu batch cho 3 bảng
            batch_data = {
                "attendance_params": [],
                "attendance_raw_params": [],
                "free_usage_updates": []
            }

            for record in records: # Chỉ duyệt record cho ngày này
                email = record[ "email" ]
                employee_id = email_to_id.get( email )
                if not employee_id:
                    # logging.info( f"⚠️ Dữ liệu không đầy đủ cho { employee_id } vào ngày { target_date }" )
                    continue

                # Parse dữ liệu mới từ API
                new_first_in_str = record.get( "first_in" )
                new_last_out_str = record.get( "last_out" )
                if not new_first_in_str or not new_last_out_str:
                    logging.info( f"⚠️ Dữ liệu không đầy đủ cho { employee_id } vào ngày { target_date }" )
                    continue

                new_first_in = datetime.strptime( new_first_in_str, "%Y-%m-%d %H:%M" )
                new_last_out = datetime.strptime( new_last_out_str, "%Y-%m-%d %H:%M" )

                # Lấy dữ liệu của user cho ngày này
                existing_data = existing_data_map.get( employee_id )
                needs_upsert = True

                # So sánh dữ liệu mới với dữ liệu cũ
                if existing_data:
                    existing_first_in = existing_data[ "first_in" ]
                    existing_last_out = existing_data[ "last_out" ]

                    if new_first_in == existing_first_in and new_last_out == existing_last_out:
                        needs_upsert = False

                if needs_upsert:
                    # Start timing processing for this record
                    start_ns = time.perf_counter_ns()
                    # Prepare data for batch operations
                    is_leave_morning, is_leave_afternoon, shift_type = leaves_data.get(
                        employee_id, ( False, False, "normal" )
                    )
                    
                    # Lấy số lần miễn trừ còn lại trong tháng
                    free_allowance = free_allowances_data.get( employee_id, FREE_PER_MONTH )

                    # Xác định "year_month" theo business rule:
                    # - Một tháng logic chạy từ 26 của tháng trước tới 25 của tháng hiện tại.
                    # - Nếu ngày >= 26 thì nó thuộc về tháng kế tiếp (ta lấy ngày 1 của tháng kế tiếp)
                    if target_date.day >= 26:
                        # move to first day of next month
                        if target_date.month == 12:
                            year_month = target_date.replace( year=target_date.year + 1, month=1, day=1 )
                        else:
                            year_month = target_date.replace( month=target_date.month + 1, day=1 )
                    else:
                        # canonical month is current calendar month (first day)
                        year_month = target_date.replace( day=1 )
                    
                    # Chuẩn bị daily_record cho hàm process_daily_attendance
                    daily_record = {
                        "check_in": new_first_in.strftime( "%H:%M" ),
                        "check_out": new_last_out.strftime( "%H:%M" ),
                        "is_leave_morning": is_leave_morning,
                        "is_leave_afternoon": is_leave_afternoon
                    }
                    
                    processed_record = process_daily_attendance( daily_record, free_allowance )
                    
                    # Check if free allowance was used
                    initial_free_allowance = processed_record.get( "initial_free_allowance", 0 )
                    final_free_allowance = processed_record.get( "free_allowance", 0 )
                    is_free_used = initial_free_allowance != final_free_allowance
                    
                    # Prepare attendance data
                    shift_start_str = SHIFT_CONFIG[ shift_type ][ "check_in_reference" ]
                    shift_end_str = SHIFT_CONFIG[ shift_type ][ "check_out_reference" ]
                    
                    total_violation_minutes = processed_record.get( "violation_minutes", 0 )
                    penalty_hours = processed_record.get( "deduction_hours", 0 )
                    
                    # End timing and compute duration in milliseconds
                    end_ns = time.perf_counter_ns()
                    duration_ns = end_ns - start_ns
                    duration_ms = int( duration_ns / 1_000_000 )
                    logging.info( f"Duration (ns): { duration_ns }" )
                    logging.info( f"Duration (ms): { duration_ms }" )

                    # 1. Collect attendance params
                    attendance_params = [
                        employee_id,                # employee_id
                        target_date,                # date
                        new_first_in,               # raw_check_in
                        new_last_out,               # raw_check_out
                        1,                          # raw_data_version
                        shift_start_str,            # shift_start
                        shift_end_str,              # shift_end
                        total_violation_minutes,    # late_minutes
                        penalty_hours,              # penalty_hours
                        shift_type != "normal",     # is_leave
                        is_free_used,               # is_free_used
                        str( os.getpid() ),         # calculated_by (current process id)
                        duration_ms,                # calculation_duration_ms
                        "v1.0"                      # business_rules_version
                    ]
                    batch_data[ "attendance_params" ].append( attendance_params )
                    
                    # 2. Collect attendance_raw params
                    raw_params = [
                        employee_id, target_date, new_first_in, new_last_out, datetime.now()
                    ]
                    batch_data[ "attendance_raw_params" ].append( raw_params )
                    
                    # 3. Collect free usage update if needed
                    if is_free_used:
                        batch_data[ "free_usage_updates" ].append( [ employee_id, year_month ] )
            
            # Batch insert/update all data for this date
            if batch_data[ "attendance_params" ] or batch_data[ "attendance_raw_params" ] or batch_data[ "free_usage_updates" ]:
                await _batch_upsert_data( conn, batch_data, target_date )

    except Exception as e:
        logging.info( f"❌ Failed to get attendance data: { e }" )
        raise e
    finally:
        conn.close()

def upsert_data():
    return asyncio.run( upsert_data_async() )


with DAG(
    dag_id='attendance_upsert_data',
    description='ETL pipeline for attendance data',
    catchup=False,
    max_active_runs=1,
) as dag:

    upsert_data_task = PythonOperator(
        task_id="upsert_data_task",
        python_callable=upsert_data,
    )

    upsert_data_task # type: ignore
