from fastapi import status

import logging

from models.session import UpsertSessionRequest

from utils.index import RedisDep

from services.session import index as session_service

from errors.internal_error import InternalError


async def upsert_session(
    request: UpsertSessionRequest,
    redis: RedisDep,
) -> None:
    try:
        logging.debug( request.data )

        # Validation 1: Kiểm tra session_id có tồn tại không
        if not request.session_id or request.session_id.strip() == "":
            raise InternalError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Session ID is required"
            )
        
        # Validation 2: Kiểm tra data có tồn tại không
        if not request.data:
            raise InternalError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Session data is required"
            )
        
        # Validation 3: Kiểm tra có ít nhất 1 trường để insert vào Redis
        # Sử dụng exclude_none=True để lọc ra các field có giá trị
        session_data = request.data.model_dump( exclude_none=True )
        
        if not session_data:
            raise InternalError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="At least one data field must be provided"
            )
        
        logging.debug( request.data )

        await session_service.upsert_session( redis, request.session_id, request.data )

    except Exception as e:
        logging.error( f"Error upserting session '{ request.session_id }': { str( e ) }" )
        raise e

async def get_session(
    session_id: str,
    redis: RedisDep
):
    try:
        if not session_id or session_id.strip() == "":
            raise InternalError(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Session ID is required"
            )
        
        response = await session_service.get_session( session_id, redis )
        return response

    except Exception as e:
        logging.error( f"Error retrieving session '{ session_id }': { str( e ) }" )
        raise e
