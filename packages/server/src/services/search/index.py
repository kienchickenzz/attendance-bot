from fastapi import status

import logging
from typing import List

from models.search import SearchRequest, TimeData
from models.search import SearchLateStatusRequest
from models.search import SearchLateCountsRequest, LateData
from models.search import SearchAttendanceCountsRequest, AttendanceData
from models.search import SearchAttendanceStatusRequest
from errors.internal_error import InternalError

from utils.index import SessionDep

from sqlalchemy import text

def search_time( request: SearchRequest, db: SessionDep ) -> List[ TimeData ]:
    try:
        filter_data = request.filter
        user_email = filter_data[ 'user_email' ]
        start_date = filter_data[ 'start_date' ] 
        end_date = filter_data[ 'end_date' ]

        start_datetime_iso = f"{ start_date } 00:00:00" # YYYY-MM-DD HH:MM:SS
        end_datetime_iso = f"{ end_date } 23:59:59" # YYYY-MM-DD HH:MM:SS

        sql_query = text( """
            SELECT 
                checkin_time,
                checkout_time
            FROM employee_attendance 
            WHERE 
                user_email = :user_email
                AND checkin_time >= :start_datetime
                AND checkin_time <= :end_datetime
            ORDER BY checkin_time ASC
        """ )

        query_params = {
            'user_email': user_email,
            'start_datetime': start_datetime_iso,
            'end_datetime': end_datetime_iso
        }

        result = db.execute( sql_query, query_params )
        raw_records = result.fetchall()
        
        attendance_records = []
        for record in raw_records:
            # record là một Row object, có thể access bằng column name hoặc index
            checkin_time = record.checkin_time
            checkout_time = record.checkout_time

            # Convert datetime objects thành ISO format string với timezone
            # Việc thêm 'Z' suffix cho biết đây là UTC timezone
            checkin_iso = checkin_time.isoformat() + 'Z' 
            checkout_iso = checkout_time.isoformat() + 'Z'
            
            date = checkin_iso[ :10 ]
            
            # Tạo TimeData object với data đã được transform
            time_data = TimeData(
                date=date,
                checkin_time=checkin_iso,
                checkout_time=checkout_iso
            )
            attendance_records.append(time_data)

        # Bước 8: Log kết quả cuối cùng để tracking
        logging.info(f"Successfully transformed {len(attendance_records)} records to TimeData format")
        return attendance_records
        
    except Exception as e:
        logging.error( f"Error searching by metadata: { str( e ) }" )
        raise InternalError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Error searching by metadata: { str( e ) }"
        )


def search_late( request: SearchLateCountsRequest, db: SessionDep ) -> List[ LateData ]:
    try:
        filter_data = request.filter
        user_email = filter_data[ 'user_email' ]
        start_date = filter_data[ 'start_date' ] 
        end_date = filter_data[ 'end_date' ]

        start_datetime_iso = f"{ start_date } 00:00:00" # YYYY-MM-DD HH:MM:SS
        end_datetime_iso = f"{ end_date } 23:59:59" # YYYY-MM-DD HH:MM:SS

        sql_query = text( """
            SELECT DISTINCT 
                DATE(checkin_time) as attendance_date,
                bool_or(is_late) as is_late
            FROM employee_attendance 
            WHERE 
                user_email = :user_email
                AND checkin_time >= :start_datetime
                AND checkin_time <= :end_datetime
            GROUP BY DATE(checkin_time)
            ORDER BY attendance_date ASC
        """ )

        # Bước 4: Chuẩn bị parameters cho query
        query_params = {
            'user_email': user_email,
            'start_datetime': start_datetime_iso,
            'end_datetime': end_datetime_iso
        }

        result = db.execute( sql_query, query_params )
        raw_records = result.fetchall()

        # Bước 6: Transform database results thành list of date strings
        # PostgreSQL DATE() function trả về date objects, cần convert thành strings
        late_data_list = []
        for record in raw_records:
            # record.attendance_date là một date object từ PostgreSQL
            # Convert sang string format YYYY-MM-DD như requirement
            date_str = record.attendance_date.strftime( '%Y-%m-%d' )

            late_data = LateData(
                date=date_str,
                is_late=record.is_late  # bool_or() trả về boolean
            )
            late_data_list.append( late_data )

            logging.debug( late_data )
            
        # Bước 7: Logging để monitoring và debugging
        logging.info( f"Found { len( late_data_list ) } late days for user { user_email }" )
        
        return late_data_list
        
    except Exception as e:
        logging.error( f"Error searching by metadata: { str( e ) }" )
        raise InternalError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Error searching by metadata: { str( e ) }"
        )


def search_attendance( request: SearchAttendanceCountsRequest, db: SessionDep ) -> List[ AttendanceData ]:
    try:
        filter_data = request.filter
        user_email = filter_data[ 'user_email' ]
        start_date = filter_data[ 'start_date' ] 
        end_date = filter_data[ 'end_date' ]

        start_datetime_iso = f"{ start_date } 00:00:00" # YYYY-MM-DD HH:MM:SS
        end_datetime_iso = f"{ end_date } 23:59:59" # YYYY-MM-DD HH:MM:SS

        sql_query = text( """
            SELECT 
                DATE(checkin_time) as attendance_date,
                attendance_count
            FROM employee_attendance 
            WHERE 
                user_email = :user_email
                AND checkin_time >= :start_datetime
                AND checkin_time <= :end_datetime
            ORDER BY attendance_date ASC
        """ )

        query_params = {
            'user_email': user_email,
            'start_datetime': start_datetime_iso,
            'end_datetime': end_datetime_iso
        }

        result = db.execute(sql_query, query_params)
        raw_records = result.fetchall()

        attendance_data = []
        
        for record in raw_records:
            # record là SQLAlchemy Row object, có thể access bằng column name
            attendance_date = record.attendance_date  # date object từ DATE() function
            attendance_count = record.attendance_count  # datetime object từ PostgreSQL

            date_str = attendance_date.strftime('%Y-%m-%d')
            
            attendance_item = AttendanceData(
                date=date_str,
                attendance=attendance_count
            )
            attendance_data.append( attendance_item )

        # Bước 7: Logging để monitoring và debugging
        logging.info(f"Successfully processed {len(attendance_data)} attendance records for user {user_email}")
        if attendance_data:
            # Log sample data để verify tính toán có đúng không
            logging.debug(f"Sample attendance data: {attendance_data[0].__dict__ if attendance_data else 'No data'}")
        
        return attendance_data
        
    except Exception as e:
        logging.error( f"Error searching by metadata: { str( e ) }" )
        raise InternalError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Error searching by metadata: { str( e ) }"
        )
