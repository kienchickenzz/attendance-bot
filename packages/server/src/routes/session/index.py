from fastapi import APIRouter

from utils.index import RedisDep

from models.session import UpsertSessionRequest
from models.session import GetSessionResponse

import logging

from controllers.session import index as session_controller

session_router = APIRouter()


@session_router.post( 
    path="/upsert" 
)
async def upsert_session(
    request: UpsertSessionRequest,
    redis: RedisDep,
):
    try:
        await session_controller.upsert_session( request, redis )

    except Exception as e:
        logging.error( f"Error upserting session '{ request.session_id }': { str( e ) }" )
        raise e


@session_router.get( 
    path="/{session_id}", 
    response_model=GetSessionResponse 
)
async def get_session(
    session_id: str,
    redis: RedisDep
):
    try:
        response = await session_controller.get_session( session_id, redis )
        return response
        
    except Exception as e:
        logging.error( f"Error retrieving session '{ session_id }': { str( e ) }" )
        raise e
