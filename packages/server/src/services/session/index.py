import logging

from models.session import UpsertSessionRequest, SessionContext, GetSessionResponse

from utils.index import RedisDep

from configs.index import app_config

from errors.internal_error import InternalError


async def upsert_session(
    redis: RedisDep,
    request: UpsertSessionRequest,
) -> None: 
    try:
        redis_key = request.session_id
        logging.debug( request.data )

        exists = await redis.exists( redis_key )
        action = "updated" if exists else "created"
        
        session_data = request.data.model_dump( exclude_none=True )

        session_data_str = {
            field: str( value ) if not isinstance( value, str ) else value 
            for field, value in session_data.items()
        }
        
        await redis.hmset( redis_key, session_data_str )
        await redis.expire( redis_key, app_config.REDIS_TTL )
        
        logging.info( f"Successfully { action } session '{ redis_key }' with TTL { app_config.REDIS_TTL }s" )
        logging.debug( request.data )

    except Exception as e:
        logging.error( f"Error upserting session '{ request.session_id }': { str( e ) }" )
        raise e

async def get_session(
    session_id: str,
    redis: RedisDep
) -> GetSessionResponse:
    try:
        session_data = await redis.hgetall( session_id )
        
        # Session không tồn tại hoặc đã hết hạn
        if session_data is None:
            raise InternalError(
                status_code=404,
                message=f"Session '{ session_id }' not found or expired"
            )
        
        ttl = await redis.ttl( session_id )
        
        valid_fields = {
            field: session_data.get(field) 
            for field in ['start_date', 'end_date', 'topic'] 
            if field in session_data and session_data[field]
        }
        
        session_context = SessionContext(**valid_fields)
        
        logging.info( f"Retrieved session '{ session_id }', TTL: { ttl }s" )
        return GetSessionResponse(
            session_id=session_id,
            data=session_context,
            expires_in=ttl if ttl > 0 else 0
        )
        
    except Exception as e:
        logging.error( f"Error retrieving session '{ session_id }': { str( e ) }" )
        raise e
