from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow import DAG

import requests
from datetime import timedelta
import subprocess
import os
import time

import logging
from utils import process_daily_attendance


API_URL = "http://localhost:3978/api/airflow/data"


def call_api():
    try:
        print( f"Calling API: { API_URL }" )
        
        response = requests.post(
            API_URL,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        # Check if request was successful
        response.raise_for_status()
        print(f"✓ API call successful!")
        
        # Try to parse JSON response
        try:
            data = response.json()
            print(f"Response Data (JSON): {data}")
            return data
        except ValueError:
            # If not JSON, print as text
            print(f"Response Data (Text): {response.text}")
            return response.text
            
    except Exception as e:
        print(f"✗ Error: {e}")
        logging.error(f"Error: {e}")
        raise e

def transform_attendance_data( raw_data, free_allowance=0 ):
    """
    Transform raw attendance data by applying business logic to each record
    
    Args:
        raw_data: Response from API call (list of attendance records)
        free_allowance: Number of free violations allowed for each employee
    
    Returns:
        List of transformed attendance records with violation calculations
    """
    try:
        if not isinstance( raw_data, list ):
            print( f"Warning: Expected list but got { type( raw_data ) }. Converting to list." )
            raw_data = [raw_data] if raw_data else []
        
        transformed_data = []
        
        for record in raw_data:
            if not isinstance(record, dict):
                print(f"Warning: Skipping invalid record: {record}")
                continue
            
            # Apply transformation logic to each daily record
            transformed_record = record.copy()  # Keep original data
            
            # Process attendance data using the business logic
            processed_data = process_daily_attendance(record, free_allowance)
            
            # Add processed results to the record
            transformed_record.update(processed_data)
            
            transformed_data.append(transformed_record)
            
            # Log the transformation for debugging
            print(f"Processed record: {record.get('date', 'unknown date')} - "
                  f"Violations: {processed_data['violation_minutes']} minutes, "
                  f"Deduction: {processed_data['deduction_hours']} hours")
        
        print(f"✓ Successfully transformed {len(transformed_data)} attendance records")
        return transformed_data
        
    except Exception as e:
        print(f"✗ Error transforming attendance data: {e}")
        raise e


def get_attendance_data():
    try:
        print("Starting attendance data collection...")
        
        # Call API to get raw data
        raw_data = call_api()
        
        # Transform the data using business logic
        transformed_data = transform_attendance_data(raw_data, free_allowance=2)
        
        print("✓ Attendance data collection and transformation completed successfully!")
        return transformed_data
        
    except Exception as e:
        print(f"✗ Failed to get attendance data: {e}")
        raise e


with DAG(
    dag_id='get_attendance_data',
    description='ETL pipeline for attendance data',
    catchup=False,
    max_active_runs=1,
) as dag:

    get_data = PythonOperator(
        task_id="get_attendance_data",
        python_callable=get_attendance_data,
    )

    get_data # type: ignore
