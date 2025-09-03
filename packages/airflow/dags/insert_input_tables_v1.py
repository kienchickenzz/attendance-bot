from airflow.providers.standard.operators.python import PythonOperator
from airflow import DAG

import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.extensions import connection
import asyncio
import logging


# ----------
# CONFIGURATION
# ----------

# TODO: Thêm điều kiện để sử dụng hook lẫn connection string (ưu tiên hook nếu có) để có thể gộp 2 file DAG lại
CONNECTION_URL = "postgresql://postgres:Pa55w.rd@localhost:5432/attendance"
TARGET_MONTH = '2025-08-01'


async def insert_data_async():
    conn = psycopg2.connect( CONNECTION_URL )
    logging.info( "✅ Kết nối thành công!" )
    
    try:
        cur = conn.cursor( cursor_factory=DictCursor )

        insert_query = """
            INSERT INTO monthly_free_usage (employee_id, year_month)
            SELECT 
                employee_id,
                %s::DATE as year_month
            FROM employees 
            WHERE is_active = TRUE
            ON CONFLICT (employee_id, year_month) 
            DO NOTHING;
        """
        cur.execute( insert_query, ( TARGET_MONTH, ) )
        rows_affected = cur.rowcount

        conn.commit()
        logging.info( f"✅ Finished inserting { rows_affected } records for month { TARGET_MONTH }" )

    except Exception as e:
        logging.info( f"❌ Error: { e }" )
        raise e
    finally:
        conn.close()

def insert_data():
    return asyncio.run( insert_data_async() )

with DAG(
    dag_id='insert_input_tables',
    description='',
    catchup=False,
    max_active_runs=1,
) as dag:

    insert_input_tables_task = PythonOperator(
        task_id="insert_input_tables",
        python_callable=insert_data,
    )

    insert_input_tables_task # type: ignore
