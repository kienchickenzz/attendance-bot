from airflow.providers.standard.operators.python import PythonOperator
from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook, DictCursor
 
import asyncio
import logging


# ----------
# CONFIGURATION
# ----------

# Cách 1: Gán cụ thể ngày đầu tháng (theo định dạng yyyy-mm-01)
# TARGET_MONTH = '2025-07-01'
# Cách 2: Tự động lấy ngày đầu tháng hiện tại
TARGET_MONTH = None  # Để None nếu muốn tự động lấy tháng hiện tại

CONNECTION_ID = 'attendance'
 

async def insert_data_async():
    pg = PostgresHook( postgres_conn_id=CONNECTION_ID )
    conn = pg.get_conn()
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
