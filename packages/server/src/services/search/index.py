from fastapi import status

import logging
from datetime import datetime, timedelta
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
                checkin_time,
                checkout_time,
                DATE(checkin_time) as attendance_date
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

        result = db.execute(sql_query, query_params)
        raw_records = result.fetchall()

        attendance_data = []
        
        for record in raw_records:
            # record là SQLAlchemy Row object, có thể access bằng column name
            checkin_time = record.checkin_time  # datetime object từ PostgreSQL
            checkout_time = record.checkout_time  # có thể là None nếu chưa checkout
            attendance_date = record.attendance_date  # date object từ DATE() function

            # Bước 6a: Tính toán attendance value dựa trên business logic
            attendance_value = calculate_attendance_value(checkin_time, checkout_time)
            
            # Bước 6b: Format date thành string theo format YYYY-MM-DD
            date_str = attendance_date.strftime('%Y-%m-%d')
            
            # Bước 6c: Tạo AttendanceData object với calculated values
            attendance_item = AttendanceData(
                date=date_str,
                attendance=attendance_value
            )
            attendance_data.append(attendance_item)

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


def calculate_attendance_value( checkin_time, checkout_time ) -> float:
    """
    Tính toán giá trị attendance dựa trên thời gian checkin và checkout
    
    Business logic:
    - Không có checkin: 0.0 (không thể xảy ra vì query filter theo checkin_time)
    - Chỉ có checkin, không có checkout: 0.5 (nửa ngày công)
    - Có cả checkin và checkout: tính dựa trên giờ checkout
        * Trước 14:00 (2:00 PM): 0.5 ngày
        * Từ 17:30 (5:30 PM) trở lên: 1.0 ngày đầy đủ  
        * Trong khoảng 14:00-17:30: 0.5 ngày
    
    Args:
        checkin_time: datetime object từ PostgreSQL (không thể None vì có WHERE clause)
        checkout_time: datetime object từ PostgreSQL (có thể None)
    
    Returns:
        float: Giá trị attendance (0.5 hoặc 1.0)
    """
    
    # Case 1: Chỉ có checkin, không có checkout -> nửa ngày
    # Đây là trường hợp employee quên checkout hoặc đang trong ca làm việc
    if not checkout_time:
        logging.debug(f"No checkout time found, assigning 0.5 attendance")
        return 0.5
    
    # Case 2: Có cả checkin và checkout -> tính toán dựa trên giờ checkout
    try:
        # checkout_time đã là datetime object từ PostgreSQL, không cần parsing
        # Tính toán thời gian checkout dưới dạng decimal hours
        # Ví dụ: 14:30 = 14.5, 17:45 = 17.75
        checkout_hour = checkout_time.hour
        checkout_minute = checkout_time.minute
        checkout_time_decimal = checkout_hour + checkout_minute / 60.0
        
        # Áp dụng business rules cho attendance calculation
        if checkout_time_decimal < 14.0:  # Checkout trước 2:00 PM
            logging.debug(f"Early checkout at {checkout_time_decimal:.2f}, assigning 0.5 attendance")
            return 0.5  # Nửa ngày - có thể là nghỉ sớm hoặc làm ca sáng
        elif checkout_time_decimal >= 17.5:  # Checkout từ 5:30 PM trở lên
            logging.debug(f"Full day checkout at {checkout_time_decimal:.2f}, assigning 1.0 attendance")
            return 1.0  # Ngày đầy đủ - làm việc full-time
        else:  # Checkout trong khoảng 2:00 PM - 5:30 PM
            logging.debug(f"Partial day checkout at {checkout_time_decimal:.2f}, assigning 0.5 attendance")
            return 0.5  # Nửa ngày - có thể là làm ca chiều hoặc nghỉ sớm
            
    except Exception as e:
        # Fallback case nếu có lỗi trong quá trình tính toán
        # Log warning nhưng không raise exception để không break toàn bộ process
        logging.warning(f"Error calculating attendance for checkout_time {checkout_time}: {str(e)}")
        return 0.5  
