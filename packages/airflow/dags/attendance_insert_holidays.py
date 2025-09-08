from airflow.operators.python import PythonOperator
from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook, DictCursor
from psycopg2.extras import execute_values

import logging
import json
import os


current_dir = os.path.dirname( os.path.abspath( __file__ ) )
FILE_PATH = os.path.join( current_dir, "holidays.json" )
CONNECTION_ID = 'attendance'

def insert_data():
    pg = PostgresHook( postgres_conn_id=CONNECTION_ID )
    conn = pg.get_conn()
    logging.info( "✅ Kết nối thành công!" )

    cur = conn.cursor( cursor_factory=DictCursor )

    try:

        with open( FILE_PATH, "r", encoding="utf-8" ) as f:
            holidays = json.load( f ) # [{"date": "...", "name": "..."}, ...]

        values = [ ( h[ "date" ], h[ "name" ] ) for h in holidays ]
        insert_sql = """
            INSERT INTO holidays ("date", "name")
            VALUES %s
            ON CONFLICT (date) DO NOTHING
        """

        execute_values( cur, insert_sql, values )

        conn.commit()
        logging.info( f"Đã insert { len( values ) } bản ghi" )

    except Exception as e:
        # Rollback transaction on error
        conn.rollback()
        logging.info( f"❌ Failed to get attendance data: { e }" )
        raise e
    finally:
        conn.close()

with DAG(
    dag_id='attendance_insert_holidays',
    description='',
    catchup=False,
    max_active_runs=1,
) as dag:

    insert_data_task = PythonOperator(
        task_id="insert_data_task",
        python_callable=insert_data,
    )

    insert_data_task # type: ignore
