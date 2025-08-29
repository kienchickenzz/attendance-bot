from airflow.providers.standard.operators.python import PythonOperator
from airflow import DAG

import requests
from datetime import datetime, date
import os
import logging
import asyncio
from collections import defaultdict
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.extensions import connection


import sys
import os

current_dir = os.path.dirname( os.path.abspath( __file__ ) )
if current_dir not in sys.path:
    sys.path.append( current_dir )


from utils import process_daily_attendance
from constants import SHIFT_CONFIG, FREE_PER_MONTH


API_URL = "http://localhost:3978/api/airflow/data"
CONNECTION_URL = "postgresql://postgres:Pa55w.rd@localhost:5432/attendance"
FREE_PER_MONTH = 5


def _call_api() -> list[ dict[ str, str ] ]:
    try:
        logging.info( f"Calling API: { API_URL }" )
        
        response = requests.post(
            API_URL,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        # Check if request was successful
        response.raise_for_status()
        logging.info(f"✓ API call successful!")
        
        # Try to parse JSON response
        try:
            data = response.json()
            logging.info(f"Response Data (JSON): {data}")
            return data[ 'data' ]
        except ValueError as e:
            logging.info( f"✗ Error: { e }" )
            raise e
            
    except Exception as e:
        logging.info(f"✗ Error: {e}")
        raise e
    
async def _get_employee_email( conn: connection, employee_id: str ) -> str | None:

    cur = conn.cursor( cursor_factory=DictCursor )

    query = "SELECT email FROM employees WHERE employee_id = %s"
    params = [ employee_id ]
    cur.execute( query, params )
    rows = cur.fetchall()
    if not rows:
        return None
    return rows[ 0 ][ "email" ]

async def _get_existing_data(
    conn: connection, 
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
    conn: connection, 
    emails: list[str]
) -> dict[str, str]:
    
    cur = conn.cursor( cursor_factory=DictCursor )

    if not emails:
        return {}

    query = """
        SELECT email, employee_id 
        FROM employees 
        WHERE email = ANY(%s)
    """
    params = [emails]

    cur.execute( query, params )
    rows = cur.fetchall()
    if not rows:
        return {}

    email_to_id = {}
    row = rows[ 0 ]
    email_to_id[ row[ "email" ] ] = row[ "employee_id" ]

    return email_to_id

async def _get_leave_info(
    conn: connection,
    employee_id: str,
    target_date: date
) -> tuple[ bool, bool, str ]:
    
    cur = conn.cursor( cursor_factory=DictCursor )
    
    leave_query = """SELECT time_type, leave_reason 
FROM leaves 
WHERE employee_id = %s AND date = %s
"""
    cur.execute(
        leave_query, [employee_id, target_date]
    )
    rows = cur.fetchall()

    is_leave_morning = False
    is_leave_afternoon = False
    shift_type = "normal"

    if rows:
        row = rows[ 0 ]
        time_type = row[ "time_type" ]
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
    
    return is_leave_morning, is_leave_afternoon, shift_type

async def _update_free_allowance_usage(
    conn: connection,
    employee_id: str,
    year_month: date
) -> None:
    
    cur = conn.cursor( cursor_factory=DictCursor )
    
    update_query = """
        UPDATE monthly_free_usage 
        SET used_count = used_count + 1 
        WHERE employee_id = %s AND year_month = %s
    """
    try:
        cur.execute( update_query, [ employee_id, year_month ] )
        print(f"✅ Cập nhật used_count +1 cho employee {employee_id} tháng {year_month}")
    except Exception as e:
        print( f"❌ Error: { e }" )
        raise

async def _get_free_allowance(
    conn: connection,
    employee_id: str,
    target_date: date,
    free_per_month: int
) -> int:
    
    cur = conn.cursor( cursor_factory=DictCursor )
    
    year_month = target_date.replace( day=1 ) # First day of month
    
    free_query = """
        SELECT used_count 
        FROM monthly_free_usage 
        WHERE employee_id = %s AND year_month = %s
    """
    cur.execute( free_query, [ employee_id, year_month ] )
    rows = cur.fetchall()

    used_count = 0
    if rows:
        used_count = rows[ 0 ][ "used_count" ]

    free_allowance = max( 0, free_per_month - used_count )
    return free_allowance

async def _upsert_data(
    conn: connection,
    attendance_info: tuple[ str, datetime, datetime, datetime ]
):
    employee_id, target_date, new_first_in, new_last_out = attendance_info
    logging.info( f"👉 Record cần upsert: "
            f"{{'employee_id': {employee_id}, 'date': {target_date}, "
            f"'first_in': {new_first_in}, 'last_out': {new_last_out}}}")
    
    is_leave_morning, is_leave_afternoon, shift_type = await _get_leave_info(
        conn, employee_id, target_date
    )
    
    # Lấy số lần miễn trừ còn lại trong tháng
    free_allowance = await _get_free_allowance(
        conn, employee_id, target_date, FREE_PER_MONTH
    )
    year_month = target_date.replace( day=1 )  # First day of month
    
    # Chuẩn bị daily_record cho hàm process_daily_attendance
    daily_record = {
        "check_in": new_first_in.strftime( "%H:%M" ),
        "check_out": new_last_out.strftime( "%H:%M" ),
        "is_leave_morning": is_leave_morning,
        "is_leave_afternoon": is_leave_afternoon
    }
    
    logging.info(f"📋 Dữ liệu chuẩn bị cho process_daily_attendance:")
    logging.info(f"   - daily_record: {daily_record}")
    logging.info(f"   - free_allowance: {free_allowance}")
    
    processed_record = process_daily_attendance( daily_record, free_allowance )
    logging.info( processed_record )
    
    # Check if free allowance was used and update used_count
    initial_free_allowance = processed_record.get( "initial_free_allowance", 0 )
    final_free_allowance = processed_record.get( "free_allowance", 0 )
    
    if initial_free_allowance != final_free_allowance:
        logging.info( f"🔄 Free allowance used: { initial_free_allowance } -> { final_free_allowance }" )
        await _update_free_allowance_usage( conn, employee_id, year_month )
    
    # Insert/Update attendance table with processed results
    attendance_upsert_query = """
        INSERT INTO attendance (
            employee_id, date, raw_check_in, raw_check_out, raw_data_version,
            shift_start, shift_end, late_minutes, penalty_hours,
            is_holiday, is_leave, is_free_used, calculated_by, business_rules_version
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (employee_id, date) DO UPDATE SET
            raw_check_in = EXCLUDED.raw_check_in,
            raw_check_out = EXCLUDED.raw_check_out,
            raw_data_version = EXCLUDED.raw_data_version,
            shift_start = EXCLUDED.shift_start,
            shift_end = EXCLUDED.shift_end,
            late_minutes = EXCLUDED.late_minutes,
            penalty_hours = EXCLUDED.penalty_hours,
            is_holiday = EXCLUDED.is_holiday,
            is_leave = EXCLUDED.is_leave,
            is_free_used = EXCLUDED.is_free_used,
            calculated_by = EXCLUDED.calculated_by,
            calculated_at = CURRENT_TIMESTAMP,
            business_rules_version = EXCLUDED.business_rules_version
    """
    
    # Prepare attendance data
    shift_start_str = SHIFT_CONFIG[ shift_type ][ "check_in_reference" ]
    shift_end_str = SHIFT_CONFIG[ shift_type ][ "check_out_reference" ]
    
    total_violation_minutes = processed_record.get( "violation_minutes", 0 )
    penalty_hours = processed_record.get( "deduction_hours", 0 )
    is_free_used = initial_free_allowance != final_free_allowance
    
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
        False,                      # is_holiday (TODO: check holiday table)
        shift_type != "normal",     # is_leave
        is_free_used,               # is_free_used
        "airflow-dag",              # calculated_by (TODO: get actual PID)
        "v1.0"                      # business_rules_version (TODO: get actual rule version)
    ]
    
    cur = conn.cursor( cursor_factory=DictCursor )
    cur.execute( attendance_upsert_query, attendance_params )
    logging.info(f"✅ Upsert attendance cho employee {employee_id} ngày {target_date}")
    
    # Also update attendance_raw table
    raw_upsert_query = """
        INSERT INTO attendance_raw (
            employee_id, date, first_in, last_out, processed_at
        ) VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (employee_id, date) DO UPDATE SET
            first_in = EXCLUDED.first_in,
            last_out = EXCLUDED.last_out,
            data_version = attendance_raw.data_version + 1,
            last_updated = CURRENT_TIMESTAMP,
            processed_at = CURRENT_TIMESTAMP,
            process_attempts = attendance_raw.process_attempts + 1
    """
    
    cur.execute(
        raw_upsert_query,
        [ employee_id, target_date, new_first_in, new_last_out, datetime.now() ]
    )
    logging.info( f"✅ Upsert attendance_raw cho employee { employee_id } ngày { target_date }" )

async def upsert_attendance_data_async():
    conn = psycopg2.connect( CONNECTION_URL )

    try:
        logging.info( "✅ Kết nối thành công!" )

        raw_data = _call_api()

        # Gom record theo ngày
        date_to_records = defaultdict( list )
        for record in raw_data:
            date_str = datetime.strptime( record[ "first_in" ], "%Y-%m-%d %H:%M" ).date()
            date_to_records[ date_str ].append( record )

        for date_str, records in date_to_records.items():
            target_date = date_str
            logging.info( f"\n====== { target_date } ======" )

            # Lấy danh sách email trong ngày này
            emails = [ r[ "email" ] for r in records if r.get( "email" ) ]
            email_to_id = await _get_employee_ids_by_emails( conn, emails )
            employee_ids = list( email_to_id.values() )

            if not employee_ids:
                logging.info("⚠️ Không tìm thấy employee_id nào trong DB cho ngày này.")
                continue

            # Lấy dữ liệu cũ trong DB cho ngày này
            existing_data_map = await _get_existing_data( conn, employee_ids, target_date )

            for record in records: # chỉ duyệt record của ngày hiện tại
                email = record[ "email" ]
                employee_id = email_to_id.get(email)
                if not employee_id:
                    # logging.info(f"⚠️ Không tìm thấy employee_id cho {email}")
                    continue

                # Parse dữ liệu mới từ API
                new_first_in_str = record.get("first_in")
                new_last_out_str = record.get("last_out")
                if not new_first_in_str or not new_last_out_str:
                    continue

                new_first_in = datetime.strptime(new_first_in_str, "%Y-%m-%d %H:%M")
                new_last_out = datetime.strptime(new_last_out_str, "%Y-%m-%d %H:%M")

                # Lấy dữ liệu cũ của user trong đúng ngày đó
                existing_data = existing_data_map.get(employee_id)
                needs_upsert = True

                if existing_data:
                    existing_first_in = existing_data[ "first_in" ]
                    existing_last_out = existing_data[ "last_out" ]

                    if new_first_in == existing_first_in and new_last_out == existing_last_out:
                        needs_upsert = False

                if needs_upsert:
                    attendance_data = ( employee_id, target_date, new_first_in, new_last_out )
                    await _upsert_data( conn, attendance_data )


    except Exception as e:
        logging.info( f"✗ Failed to get attendance data: { e }" )
        raise e

def upsert_attendance_data():
    return asyncio.run( upsert_attendance_data_async() )


with DAG(
    dag_id='get_attendance_data',
    description='ETL pipeline for attendance data',
    catchup=False,
    max_active_runs=1,
) as dag:

    upsert_data = PythonOperator(
        task_id="upsert_attendance_data",
        python_callable=upsert_attendance_data,
    )

    upsert_data # type: ignore
