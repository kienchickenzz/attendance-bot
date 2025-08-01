from fastapi import APIRouter

from utils.index import SessionDep

from controllers.search import index as search_controller

from models.search import SearchRequest, SearchTimeResponse
from models.search import SearchLateCountsRequest, SearchLateCountsResponse
from models.search import SearchLateStatusRequest, SearchLateStatusResponse
from models.search import SearchAttendanceStatusRequest, SearchAttendanceStatusResponse
from models.search import SearchAttendanceCountsRequest, SearchAttendanceCountsResponse

search_router = APIRouter()

@search_router.post( 
    path="/time", 
    responses={
        200: { "model": SearchTimeResponse, },
    },
)
def search_time( request: SearchRequest, db: SessionDep ):
    return search_controller.search_time( request, db )


# @search_router.post( 
#     path="/late_status", 
#     responses={
#         200: { "model": SearchLateStatusResponse, },
#     },
# )
# def search_late_status( request: SearchLateStatusRequest ):
#     return search_controller.search_late_status( request )



@search_router.post( 
    path="/late", 
    responses={
        200: { "model": SearchLateCountsResponse, },
    },
)
def search_late( request: SearchLateCountsRequest, db: SessionDep ):
    return search_controller.search_late( request, db )


# @search_router.post( 
#     path="/attendance_status", 
#     responses={
#         200: { "model": SearchAttendanceStatusResponse, },
#     },
# )
# def search_attendance_status( request: SearchAttendanceStatusRequest ):
#     return search_controller.search_attendance_status( request )


@search_router.post( 
    path="/attendance", 
    responses={
        200: { "model": SearchAttendanceCountsResponse, },
    },
)
def search_attendance( request: SearchAttendanceCountsRequest, db: SessionDep ):
    return search_controller.search_attendance( request, db )
