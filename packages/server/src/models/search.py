from pydantic import BaseModel, Field

from typing import List, Dict, Any, Optional


# ----------
# Attendance time
# ----------


class SearchRequest( BaseModel ):
    filter: Dict[ str, Any ] = Field(
        description="Dictionary containing metadata field-value pairs to filter by",
        examples=[
            {
                "user_email": "duckien@gmail.com", 
                "start_date": "2025-07-01",
                "end_date": "2025-07-01",
            },
        ]
    )

class TimeData( BaseModel ):
    date: str = Field()
    checkin_time: str = Field()
    checkout_time: str = Field()

class SearchTimeResponse( BaseModel ):
    data: List[ TimeData ] = Field()


# ----------
# Late status
# ----------


class LateData( BaseModel ):
    date: str = Field()
    is_late: bool = Field()

class SearchLateStatusRequest( BaseModel ):
    filter: Dict[ str, Any ] = Field(
        description="Dictionary containing metadata field-value pairs to filter by",
        examples=[
            {
                "user_email": "duckien@gmail.com", 
                "start_date": "2025-07-01",
                "end_date": "2025-07-01",
            },
        ]
    )

class SearchLateStatusResponse( BaseModel ):
    data: bool = Field()


# ----------
# Late count
# ----------


class SearchLateCountsRequest( BaseModel ):
    filter: Dict[ str, Any ] = Field(
        description="Dictionary containing metadata field-value pairs to filter by",
        examples=[
            {
                "user_email": "duckien@gmail.com", 
                "start_date": "2025-07-01",
                "end_date": "2025-07-01",
            },
        ]
    )

class SearchLateCountsResponse( BaseModel ):
    data: List[ LateData ] = Field()


# ----------
# Attendance count
# ----------


class SearchAttendanceCountsRequest( BaseModel ):
    filter: Dict[ str, Any ] = Field(
        description="Dictionary containing metadata field-value pairs to filter by",
        examples=[
            {
                "user_email": "duckien@gmail.com", 
                "start_date": "2025-07-01",
                "end_date": "2025-07-01",
            },
        ]
    )

class AttendanceData( BaseModel ):
    date: str = Field()
    attendance: float = Field()

class SearchAttendanceCountsResponse( BaseModel ):
    data: List[ AttendanceData ] = Field()


# ----------
# Attendance status
# ----------


class SearchAttendanceStatusRequest( BaseModel ):
    filter: Dict[ str, Any ] = Field(
        description="Dictionary containing metadata field-value pairs to filter by",
        examples=[
            {
                "user_email": "duckien@gmail.com", 
                "start_date": "2025-07-01",
                "end_date": "2025-07-01",
            },
        ]
    )

class SearchAttendanceStatusResponse( BaseModel ):
    data: List[ AttendanceData ] = Field()
