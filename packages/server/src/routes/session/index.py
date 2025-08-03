from fastapi import APIRouter
from errors.internal_error import InternalError

from utils.index import RedisDep

from configs.index import app_config

from models.session import CreateSessionRequest
from models.session import GetSessionResponse, SessionContext

import logging

session_router = APIRouter()


@session_router.post( 
    path="/create" 
)
async def create_session(
    request: CreateSessionRequest,
    redis: RedisDep,
):
    try:
        redis_key = request.session_id
        exists = await redis.exists( redis_key )
        if exists:
            raise InternalError(
                status_code=409,  # Conflict
                message=f"Session with ID '{ request.session_id }' already exists."
            )
        
        session_json = request.model_dump_json()
        
        await redis.setex(
            redis_key,
            app_config.REDIS_TTL,
            session_json
        )
        
        logging.info( f"Successfully created session '{ redis_key }' with TTL { app_config.REDIS_TTL }s" )
        
    except Exception as e:
        logging.error(f"Error creating session '{request.session_id}': {str(e)}")
        raise InternalError(
            status_code=500,
            message=f"Failed to create session: { str( e ) }"
        )

@session_router.get( "/{session_id}", response_model=GetSessionResponse )
async def get_session(
    session_id: str,
    redis: RedisDep
):
    try:
        session_data = await redis.get( session_id )
        
        if session_data is None:
            # Session không tồn tại hoặc đã hết hạn
            raise InternalError(
                status_code=404,
                message=f"Session '{ session_id }' not found or expired"
            )
        
        ttl = await redis.ttl( session_id )
        
        session_context = SessionContext.model_validate_json( session_data )
        
        logging.info( f"Retrieved session '{ session_id }', TTL: { ttl }s" )
        
        return GetSessionResponse(
            session_id=session_id,
            data=session_context,
            expires_in=ttl if ttl > 0 else None
        )
        
    except InternalError:
        # Re-raise InternalError để giữ nguyên status code
        raise
    except Exception as e:
        logging.error(f"Error retrieving session '{session_id}': {str(e)}")
        raise InternalError(
            status_code=500,
            message=f"Failed to retrieve session: {str(e)}"
        )

# @session_router.put("/{session_id}", response_model=SessionResponse)
# async def update_session(
#     session_id: str,
#     session_data: SessionContext,
#     redis: RedisDep,
#     extend_ttl_seconds: Optional[int] = None
# ):
#     """
#     Cập nhật session hiện có với session ID do client cung cấp.
    
#     Endpoint này sẽ:
#     1. Validate session ID từ client
#     2. Kiểm tra session có tồn tại không
#     3. Cập nhật dữ liệu session
#     4. Có thể gia hạn TTL nếu được yêu cầu
#     """
#     try:
#         # Validate session ID từ URL parameter
#         try:
#             validated_session_id = _validate_session_id(session_id)
#         except ValueError as e:
#             raise InternalError(
#                 status_code=400,
#                 detail=f"Invalid session ID: {str(e)}"
#             )
        
#         redis_key = _build_session_key(validated_session_id)
        
#         # Kiểm tra session có tồn tại không
#         exists = await redis.exists(redis_key)
#         if not exists:
#             raise InternalError(
#                 status_code=404,
#                 detail=f"Session '{validated_session_id}' not found or expired"
#             )
        
#         # Cập nhật dữ liệu session
#         session_json = session_data.model_dump_json()
        
#         if extend_ttl_seconds:
#             # Cập nhật với TTL mới
#             await redis.setex(redis_key, extend_ttl_seconds, session_json)
#             new_ttl = extend_ttl_seconds
#         else:
#             # Giữ nguyên TTL hiện tại
#             current_ttl = await redis.ttl(redis_key)
#             if current_ttl > 0:
#                 await redis.setex(redis_key, current_ttl, session_json)
#                 new_ttl = current_ttl
#             else:
#                 # TTL không xác định, set lại với default
#                 await redis.setex(redis_key, DEFAULT_TTL, session_json)
#                 new_ttl = DEFAULT_TTL
        
#         logging.info(f"Updated session '{validated_session_id}'")
        
#         return SessionResponse(
#             session_id=validated_session_id,
#             data=session_data,
#             expires_in=new_ttl
#         )
        
#     except InternalError:
#         raise
#     except Exception as e:
#         logging.error(f"Error updating session '{session_id}': {str(e)}")
#         raise InternalError(
#             status_code=500,
#             detail=f"Failed to update session: {str(e)}"
#         )

# @session_router.delete("/{session_id}")
# async def delete_session(
#     session_id: str,
#     redis: RedisDep
# ):
#     """
#     Xóa session khỏi Redis với session ID do client cung cấp.
    
#     Thường được sử dụng khi user logout hoặc muốn hủy session trước khi hết hạn.
#     """
#     try:
#         # Validate session ID từ URL parameter
#         try:
#             validated_session_id = _validate_session_id(session_id)
#         except ValueError as e:
#             raise InternalError(
#                 status_code=400,
#                 detail=f"Invalid session ID: {str(e)}"
#             )
        
#         redis_key = _build_session_key(validated_session_id)
        
#         # Xóa session khỏi Redis
#         deleted_count = await redis.delete(redis_key)
        
#         if deleted_count == 0:
#             raise InternalError(
#                 status_code=404,
#                 detail=f"Session '{validated_session_id}' not found"
#             )
        
#         logging.info(f"Deleted session '{validated_session_id}'")
        
#         return JSONResponse(
#             content={"message": f"Session '{validated_session_id}' deleted successfully"},
#             status_code=200
#         )
        
#     except InternalError:
#         raise
#     except Exception as e:
#         logging.error(f"Error deleting session '{session_id}': {str(e)}")
#         raise InternalError(
#             status_code=500,
#             detail=f"Failed to delete session: {str(e)}"
#         )

# @session_router.get("/", response_model=Dict[str, Any])
# async def list_active_sessions(
#     redis: RedisDep,
#     limit: int = 100
# ):
#     """
#     Liệt kê các session đang hoạt động (chỉ dành cho admin/debug).
    
#     Chú ý: Endpoint này có thể tốn hiệu năng nếu có nhiều session.
#     Trong production, nên có authentication và phân quyền.
#     """
#     try:
#         # Tìm tất cả keys với pattern session:*
#         pattern = f"{SESSION_KEY_PREFIX}*"
#         session_keys = []
        
#         # Sử dụng SCAN thay vì KEYS để tránh block Redis
#         cursor = 0
#         while True:
#             cursor, keys = await redis.scan(cursor, match=pattern, count=100)
#             session_keys.extend(keys)
#             if cursor == 0 or len(session_keys) >= limit:
#                 break
        
#         # Giới hạn số lượng trả về
#         session_keys = session_keys[:limit]
        
#         sessions_info = []
#         for key in session_keys:
#             # Extract session ID từ Redis key
#             session_id = key.replace(SESSION_KEY_PREFIX, "")
            
#             # Lấy TTL của session
#             ttl = await redis.ttl(key)
            
#             sessions_info.append({
#                 "session_id": session_id,
#                 "expires_in": ttl if ttl > 0 else None
#             })
        
#         return {
#             "total_found": len(sessions_info),
#             "limit_applied": limit,
#             "sessions": sessions_info
#         }
        
#     except Exception as e:
#         logging.error(f"Error listing sessions: {str(e)}")
#         raise InternalError(
#             status_code=500,
#             detail=f"Failed to list sessions: {str(e)}"
#         )
