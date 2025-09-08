from airflow.providers.standard.operators.python import PythonOperator
from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook, DictCursor
from pendulum import timezone
 
import asyncio
import logging
from datetime import datetime


# ----------
# CONFIGURATION
# ----------

# Cách 1: Trigger MANUALLY 
TARGET_MONTHS = [ '2025-04-01', '2025-05-01', '2025-06-01', '2025-07-01', '2025-08-01', '2025-09-01' ] # yyyy-mm-01
# Cách 2: Trigger AUTOMATICALLY
TARGET_MONTHS = None # Để None nếu muốn tự động lấy tháng hiện tại

CONNECTION_ID = 'attendance'

local_tz = timezone( "Asia/Ho_Chi_Minh" )
 

async def insert_data_async():
    pg = PostgresHook( postgres_conn_id=CONNECTION_ID )
    conn = pg.get_conn()
    logging.info( "✅ Kết nối thành công!" )

    try:
        cur = conn.cursor( cursor_factory=DictCursor )

        months_to_insert = TARGET_MONTHS
        if months_to_insert is None:
            today = datetime.now( local_tz )
            months_to_insert = [ today.strftime( "%Y-%m-01" ) ]

        values_clause = ", ".join( [ f"(%s::DATE)" for _ in months_to_insert ] ) # ('2025-07-01'::DATE), ('2025-08-01'::DATE)

        insert_query = f"""
            INSERT INTO monthly_free_usage (employee_id, year_month)
            SELECT e.employee_id, m.year_month
            FROM employees e
            CROSS JOIN (VALUES { values_clause }) AS m(year_month)
            WHERE e.is_active = TRUE
            ON CONFLICT (employee_id, year_month) DO NOTHING;
        """
        cur.execute( insert_query, months_to_insert )
        rows_affected = cur.rowcount
 
        conn.commit()
        logging.info( f"✅ Finished inserting { rows_affected } records for months { months_to_insert }" )

    except Exception as e:
        logging.info( f"❌ Error: { e }" )
        raise e
    finally:
        conn.close()

def insert_data():
    return asyncio.run( insert_data_async() )

with DAG(
    dag_id='attendance_insert_input_tables',
    description='',
    schedule='0 0 20,22,24,26 * *', # chạy lúc 00:00 ngày 20, 22, 24, 26 hàng tháng
    start_date=datetime( 2025, 1, 1, tzinfo=local_tz ),
    catchup=False,
    max_active_runs=1,
) as dag:
 
    insert_input_tables_task = PythonOperator(
        task_id="insert_input_tables_task",
        python_callable=insert_data,
    )

    insert_input_tables_task # type: ignore
