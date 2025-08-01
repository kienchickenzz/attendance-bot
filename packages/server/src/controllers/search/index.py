from fastapi import status

from typing import Optional
import logging
import re
from datetime import datetime

from utils.index import SessionDep

from models.search import SearchRequest, SearchTimeResponse
from models.search import SearchLateStatusRequest, SearchLateStatusResponse
from models.search import SearchLateCountsRequest, SearchLateCountsResponse 
from models.search import SearchAttendanceCountsRequest, SearchAttendanceCountsResponse
from models.search import SearchAttendanceStatusRequest, SearchAttendanceStatusResponse

from errors.internal_error import InternalError

from services.search import index as search_service
    
# TODO: Validate không được query quá xa trong quá khứ hoặc tương lai
# TODO: Kiểm tra xem khi truy vấn 1 ngày thì ngày đó có phải cuối tuần không vì lúc này không có dữ liệu trả về

def _validate_date_format( date_str: str, field_name: str ) -> str:
    # Kiểm tra length tối thiểu - cần ít nhất 10 ký tự cho date part
    if len( date_str ) < 10:
        raise InternalError(
            status_code=400,
            message=f"{ field_name } format is invalid. Expected format: 'YYYY-MM-DD HH:MM:SS.microseconds' (e.g., '2025-07-11 02:38:03.112052')"
        )
    
    try:
        from datetime import datetime
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
        
    except ValueError as e:
        raise InternalError(
            status_code=400,
            message=f"{field_name} has invalid date format. Expected YYYY-MM-DD format, got: '{ date_str }'. Original error: {str(e)}"
        )

def search_time( request: SearchRequest, db: SessionDep ) -> Optional[ SearchTimeResponse ]:
    try:
        if not request.filter:
            raise InternalError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Filter dictionary cannot be empty"
            )
        
        logging.debug( "hello" )
        logging.debug( request.filter )
        
        # Chúng ta cần đảm bảo có đủ thông tin để thực hiện datetime range search
        required_fields = [ 'user_email', 'start_date', 'end_date' ]
        missing_fields = []
        
        for field in required_fields:
            # Kiểm tra xem field có tồn tại và không empty không
            if field not in request.filter or not request.filter[ field ]:
                missing_fields.append( field )
        
        # Nếu thiếu bất kỳ field nào, tạo error message chi tiết
        if missing_fields:
            missing_fields_str = ", ".join( missing_fields )
            raise InternalError(
                status_code=400,
                message=f"Missing required fields: { missing_fields_str }. All three fields (user_email, start_date, end_date) are mandatory for search operation."
            )
        
        # Đảm bảo user_email có format hợp lệ và không chỉ là whitespace
        user_email = request.filter[ 'user_email' ].strip()
        if not user_email:
            raise InternalError(
                status_code=400,
                message="user_email cannot be empty or contain only whitespace."
            )
        
        # Đây là phần validation quan trọng nhất vì datetime parsing có thể fail
        start_date_str = request.filter[ 'start_date' ].strip()
        end_date_str = request.filter[ 'end_date' ].strip()
        
        # Validate both datetime fields
        start_date_part = _validate_date_format(start_date_str, "start_date")
        end_date_part = _validate_date_format(end_date_str, "end_date")
        
        # Ensure start_date phải <= end_date
        from datetime import datetime
        start_date_obj = datetime.strptime(start_date_part, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date_part, "%Y-%m-%d")
        
        if start_date_obj > end_date_obj:
            raise InternalError(
                status_code=400,
                message=f"start_date ({start_date_part}) cannot be later than end_date ({end_date_part}). Please check your date range."
            )
        
        attendance_records = search_service.search_time( request, db )
        return SearchTimeResponse(
            data=attendance_records,
        )
        
    except Exception as e:
        logging.error( f"Error in metadata search: { str( e ) }" )
        raise e
    
def _validate_month_format(month_str: str, field_name: str) -> str:
    # Loại bỏ whitespace ở đầu và cuối
    month_str = month_str.strip()
    
    # Kiểm tra format cơ bản YYYY-MM
    if not re.match(r'^\d{4}-\d{2}$', month_str):
        raise InternalError(
            status_code=400,
            message=f"{field_name} must be in YYYY-MM format (e.g., 2025-06). Received: {month_str}"
        )
    
    # Tách năm và tháng để validate chi tiết
    try:
        year, month = month_str.split('-')
        year_int = int(year)
        month_int = int(month)
        
        # Kiểm tra năm hợp lệ (không quá xa trong quá khứ hoặc tương lai)
        current_year = datetime.now().year
        if year_int < 2020 or year_int > current_year + 10:
            raise InternalError(
                status_code=400,
                message=f"{field_name} year must be between 2020 and {current_year + 10}. Received: {year_int}"
            )
        
        # Kiểm tra tháng hợp lệ (01-12)
        if month_int < 1 or month_int > 12:
            raise InternalError(
                status_code=400,
                message=f"{field_name} month must be between 01 and 12. Received: {month_int:02d}"
            )
            
    except ValueError as e:
        raise InternalError(
            status_code=400,
            message=f"Invalid {field_name} format. Cannot parse year and month from: {month_str}"
        )
    
    return month_str

def _determine_time_range_type( filter_data: dict ) -> str:
    # Kiểm tra các trường date
    has_start_date = 'start_date' in filter_data and filter_data['start_date']
    has_end_date = 'end_date' in filter_data and filter_data['end_date']
    
    # Kiểm tra các trường month
    has_start_month = 'start_month' in filter_data and filter_data['start_month']
    has_end_month = 'end_month' in filter_data and filter_data['end_month']
    
    # Logic validation cho date range
    if has_start_date or has_end_date:
        if not (has_start_date and has_end_date):
            raise InternalError(
                status_code=400,
                message="Both start_date and end_date must be provided together. Missing: " + 
                       ("start_date" if not has_start_date else "end_date")
            )
        
        # Kiểm tra không được mix date và month
        if has_start_month or has_end_month:
            raise InternalError(
                status_code=400,
                message="Cannot mix date and month filters. Please use either (start_date, end_date) or (start_month, end_month), not both."
            )
        
        return "date"
    
    # Logic validation cho month range
    if has_start_month or has_end_month:
        if not (has_start_month and has_end_month):
            raise InternalError(
                status_code=400,
                message="Both start_month and end_month must be provided together. Missing: " + 
                       ("start_month" if not has_start_month else "end_month")
            )
        
        return "month"
    
    
    return "invalid" # No time range provided

def _validate_and_process_date_range(filter_data: dict) -> None:
    start_date_str = filter_data['start_date'].strip()
    end_date_str = filter_data['end_date'].strip()
    
    # Validate format date
    start_date_obj = _validate_date_format(start_date_str, "start_date")
    end_date_obj = _validate_date_format(end_date_str, "end_date")
    
    # Validate business logic - start_date phải <= end_date
    if start_date_obj > end_date_obj:
        raise InternalError(
            status_code=400,
            message=f"start_date ({start_date_str}) cannot be later than end_date ({end_date_str}). Please check your date range."
        )
    
def _validate_and_process_month_range(filter_data: dict) -> None:
    start_month_str = filter_data['start_month'].strip()
    end_month_str = filter_data['end_month'].strip()
    
    # Validate format month
    start_month_part = _validate_month_format(start_month_str, "start_month")
    end_month_part = _validate_month_format(end_month_str, "end_month")
    
    # Business logic validation - start_month phải <= end_month
    start_date_obj = datetime.strptime(start_month_part + '-01', "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_month_part + '-01', "%Y-%m-%d")
    
    if start_date_obj > end_date_obj:
        raise InternalError(
            status_code=400,
            message=f"start_month ({start_month_part}) cannot be later than end_month ({end_month_part}). Please check your month range."
        )
    
def search_late( request: SearchLateCountsRequest, db: SessionDep ) -> Optional[ SearchLateCountsResponse ]:
    try:
        # Bước 1.1: Kiểm tra filter dictionary không được empty
        # Tương tự như validation đầu tiên trong code gốc của bạn
        if not request.filter:
            raise InternalError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Filter dictionary cannot be empty"
            )
        
        # Log debug để tracking - giống như trong code gốc
        logging.debug(f"Received filter data: {request.filter}")

        # user_email
        if 'user_email' not in request.filter or not request.filter['user_email']:
            raise InternalError(
                status_code=400,
                message="user_email is required and cannot be empty"
            )
        
        user_email = request.filter['user_email'].strip()
        if not user_email:
            raise InternalError(
                status_code=400,
                message="user_email cannot be empty or contain only whitespace."
            )
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, user_email):
            raise InternalError(
                status_code=400,
                message=f"user_email format is invalid. Please provide a valid email address. Received: {user_email}"
            )
        
        time_range_type = _determine_time_range_type( request.filter )

        if time_range_type == "date":
            # Xử lý date range
            _validate_and_process_date_range(request.filter)
        elif time_range_type == "month":
            # Xử lý month range
            _validate_and_process_month_range(request.filter)
        else:
            # Không có time range hợp lệ
            raise InternalError(
                status_code=400,
                message="Invalid time range specification. Please provide either (start_date, end_date) or (start_month, end_month). Mixed types are not allowed."
            )
        
        late_dates = search_service.search_late( request, db )
        return SearchLateCountsResponse(
            data=late_dates,
        )
        
    except Exception as e:
        logging.error( f"Error in searching: { str( e ) }" )
        raise e

def search_attendance( request: SearchAttendanceCountsRequest, db: SessionDep ) -> SearchAttendanceCountsResponse:
    try:
        if not request.filter:
            raise InternalError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Filter dictionary cannot be empty"
            )
        
        logging.debug( request.filter )
        
        # user_email
        if 'user_email' not in request.filter or not request.filter['user_email']:
            raise InternalError(
                status_code=400,
                message="user_email is required and cannot be empty"
            )
        
        user_email = request.filter['user_email'].strip()
        if not user_email:
            raise InternalError(
                status_code=400,
                message="user_email cannot be empty or contain only whitespace."
            )
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, user_email):
            raise InternalError(
                status_code=400,
                message=f"user_email format is invalid. Please provide a valid email address. Received: {user_email}"
            )
        
        time_range_type = _determine_time_range_type( request.filter )

        if time_range_type == "date":
            # Xử lý date range
            _validate_and_process_date_range(request.filter)
        elif time_range_type == "month":
            # Xử lý month range
            _validate_and_process_month_range(request.filter)
        else:
            # Không có time range hợp lệ
            raise InternalError(
                status_code=400,
                message="Invalid time range specification. Please provide either (start_date, end_date) or (start_month, end_month). Mixed types are not allowed."
            )
        
        attend_dates = search_service.search_attendance( request, db )
        return SearchAttendanceCountsResponse(
            data=attend_dates,
        )
        
    except Exception as e:
        logging.error( f"Error in searching: { str( e ) }" )
        raise e
