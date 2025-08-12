import logging

from models.session import SessionContext, GetSessionResponse, TimePeriod

from utils.index import RedisDep

from configs.index import app_config

from errors.internal_error import InternalError

import json


async def upsert_session(
    redis: RedisDep,
    session_id: str,
    data: SessionContext,
) -> None: 
    try:
        exists = await redis.exists( session_id )
        action = "updated" if exists else "created"
        
        session_data = data.model_dump( exclude_none=True )

        # Tách time_query ra khỏi các field thường
        time_query = session_data.pop( 'time_query', None )

        hash_data = {}
        
        # Chuyển đổi các field còn lại thành string cho hash storage
        for field, value in session_data.items():
            if field != 'time_query':  # Đảm bảo không xử lý time_query ở đây
                hash_data[ field ] = str( value ) if not isinstance( value, str ) else value
        
        # Xử lý time_query đặc biệt - serialize thành JSON string
        if time_query is not None:
            # Chuyển đổi list của TimePeriod objects thành JSON string
            time_query_json = json.dumps( time_query )
            hash_data[ 'time_query' ] = time_query_json

        await redis.hmset( session_id, hash_data )
        await redis.expire( session_id, app_config.REDIS_TTL )
        
        logging.info( f"Successfully { action } session '{ session_id }' with TTL { app_config.REDIS_TTL }s" )

    except Exception as e:
        logging.error( f"Error upserting session '{ session_id }': { str( e ) }" )
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
        
        processed_fields = {}
        
        # Xử lý từng field một cách cẩn thận
        for field in [ 'time_query', 'topic', 'prev_question', 'user_name', 'user_email', 'current_time' ]:
            if field in session_data and session_data[ field ]:
                
                # Xử lý đặc biệt cho time_query vì nó được lưu dưới dạng JSON string
                if field == 'time_query':
                    try:
                        # Parse JSON string thành Python list/dict
                        time_query_data = json.loads( session_data[ field ] )
                        
                        # Chuyển đổi từng element trong list thành TimePeriod object
                        # Điều này quan trọng vì chúng ta cần đảm bảo kiểu dữ liệu đúng
                        if isinstance( time_query_data, list ):
                            time_periods = []
                            for period_data in time_query_data:
                                # Tạo TimePeriod object từ dictionary
                                # Pydantic sẽ tự động validate dữ liệu
                                time_period = TimePeriod( **period_data )
                                time_periods.append( time_period )
                            
                            processed_fields[ field ] = time_periods
                        else:
                            # Log warning nếu dữ liệu không đúng format mong đợi
                            logging.warning( f"time_query in session '{ session_id }' is not a list, skipping" )

                    except json.JSONDecodeError as json_error:
                        logging.error( f"Invalid JSON in time_query for session '{ session_id }': { str( json_error ) }" )
                        
                else:
                    # Với các field khác, chỉ cần lưu trực tiếp
                    processed_fields[field] = session_data[field]
        
        session_context = SessionContext( **processed_fields )

        logging.debug( session_context )
        
        logging.info( f"Retrieved session '{ session_id }', TTL: { ttl }s" )
        return GetSessionResponse(
            session_id=session_id,
            data=session_context,
            expires_in=ttl if ttl > 0 else 0
        )
        
    except Exception as e:
        logging.error( f"Error retrieving session '{ session_id }': { str( e ) }" )
        raise e
