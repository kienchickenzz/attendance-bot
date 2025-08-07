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

def search_time( request: SearchRequest, db: SessionDep ) -> Optional[ SearchTimeResponse ]:
    try:
        logging.debug( request )

        if not request.user_email or not request.user_email.strip():
            raise InternalError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="User email is required"
            )
        
        if not request.time_query:
            raise InternalError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Time query is required. Please provide at least one date range"
            )
        
        if len( request.time_query ) == 0:
            raise InternalError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Time query cannot be empty. Please provide at least one date range"
            )
        
        for i, date_range in enumerate( request.time_query ):
            range_index = i + 1  # Human-readable index (1-based)
            
            # Check missing fields trong từng range
            missing_fields = []
            
            if not date_range.start_date or not date_range.start_date.strip():
                missing_fields.append( "start_date" )
                
            if not date_range.end_date or not date_range.end_date.strip():
                missing_fields.append( "end_date" )
            
            if missing_fields:
                missing_fields_str = ", ".join( missing_fields )
                raise InternalError(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message=f"Date range { range_index } is missing required fields: { missing_fields_str }. Both start_date and end_date are required"
                )
            
            # Validate date format cho từng range
            start_date = date_range.start_date.strip()
            end_date = date_range.end_date.strip()
            
            try:
                # Parse để kiểm tra logic consistency
                start_date_obj = datetime.strptime( start_date, "%Y-%m-%d")
                end_date_obj = datetime.strptime( end_date, "%Y-%m-%d")
                
                # Kiểm tra start_date <= end_date cho từng range
                if start_date_obj > end_date_obj:
                    raise InternalError(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message=f"Date range { range_index }: start_date ({ start_date }) cannot be later than end_date ({ end_date })"
                    )
                
            except Exception as e:
                raise e

        attendance_records = search_service.search_time( request, db )
        return SearchTimeResponse(
            data=attendance_records,
        )
        
    except Exception as e:
        logging.error( f"Error in metadata search: { str( e ) }" )
        raise e

def search_late( request: SearchLateCountsRequest, db: SessionDep ) -> Optional[ SearchLateCountsResponse ]:
    try:
        # Bước 1.1: Kiểm tra filter dictionary không được empty
        # Tương tự như validation đầu tiên trong code gốc của bạn
        if not request.user_email or not request.user_email.strip():
            raise InternalError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="User email is required"
            )
        
        if not request.time_query:
            raise InternalError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Time query is required. Please provide at least one date range"
            )
        
        if len( request.time_query ) == 0:
            raise InternalError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Time query cannot be empty. Please provide at least one date range"
            )
        
        for i, date_range in enumerate( request.time_query ):
            range_index = i + 1  # Human-readable index (1-based)
            
            # Check missing fields trong từng range
            missing_fields = []
            
            if not date_range.start_date or not date_range.start_date.strip():
                missing_fields.append( "start_date" )
                
            if not date_range.end_date or not date_range.end_date.strip():
                missing_fields.append( "end_date" )
            
            if missing_fields:
                missing_fields_str = ", ".join( missing_fields )
                raise InternalError(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message=f"Date range { range_index } is missing required fields: { missing_fields_str }. Both start_date and end_date are required"
                )
            
            # Validate date format cho từng range
            start_date = date_range.start_date.strip()
            end_date = date_range.end_date.strip()
            
            try:
                # Parse để kiểm tra logic consistency
                start_date_obj = datetime.strptime( start_date, "%Y-%m-%d")
                end_date_obj = datetime.strptime( end_date, "%Y-%m-%d")
                
                # Kiểm tra start_date <= end_date cho từng range
                if start_date_obj > end_date_obj:
                    raise InternalError(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message=f"Date range { range_index }: start_date ({ start_date }) cannot be later than end_date ({ end_date })"
                    )
                
            except Exception as e:
                raise e
        
        late_dates = search_service.search_late( request, db )
        return SearchLateCountsResponse(
            data=late_dates,
        )
        
    except Exception as e:
        logging.error( f"Error in searching: { str( e ) }" )
        raise e

def search_attendance( request: SearchAttendanceCountsRequest, db: SessionDep ) -> SearchAttendanceCountsResponse:
    try:
        if not request.user_email or not request.user_email.strip():
            raise InternalError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="User email is required"
            )
        
        if not request.time_query:
            raise InternalError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Time query is required. Please provide at least one date range"
            )
        
        if len( request.time_query ) == 0:
            raise InternalError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Time query cannot be empty. Please provide at least one date range"
            )
        
        for i, date_range in enumerate( request.time_query ):
            range_index = i + 1  # Human-readable index (1-based)
            
            # Check missing fields trong từng range
            missing_fields = []
            
            if not date_range.start_date or not date_range.start_date.strip():
                missing_fields.append( "start_date" )
                
            if not date_range.end_date or not date_range.end_date.strip():
                missing_fields.append( "end_date" )
            
            if missing_fields:
                missing_fields_str = ", ".join( missing_fields )
                raise InternalError(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message=f"Date range { range_index } is missing required fields: { missing_fields_str }. Both start_date and end_date are required"
                )
            
            # Validate date format cho từng range
            start_date = date_range.start_date.strip()
            end_date = date_range.end_date.strip()
            
            try:
                # Parse để kiểm tra logic consistency
                start_date_obj = datetime.strptime( start_date, "%Y-%m-%d")
                end_date_obj = datetime.strptime( end_date, "%Y-%m-%d")
                
                # Kiểm tra start_date <= end_date cho từng range
                if start_date_obj > end_date_obj:
                    raise InternalError(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message=f"Date range { range_index }: start_date ({ start_date }) cannot be later than end_date ({ end_date })"
                    )
                
            except Exception as e:
                raise e
        
        attend_dates = search_service.search_attendance( request, db )
        return SearchAttendanceCountsResponse(
            data=attend_dates,
        )
        
    except Exception as e:
        logging.error( f"Error in searching: { str( e ) }" )
        raise e
