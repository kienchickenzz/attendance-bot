import logging
from typing import Optional

from redis.asyncio import Redis
import redis

from configs.index import app_config

_redis_client: Optional[ Redis ] = None

def _build_redis_url() -> str:
    host = app_config.REDIS_HOST
    port = app_config.REDIS_PORT
    database = app_config.REDIS_DB
    password = app_config.REDIS_PASSWORD
    
    # Format: redis://[password@]host:port/database
    url = f"redis://:{ password }@{ host }:{ port }/{ database }"
    
    return url

async def init():

    global _redis_client
    
    if _redis_client is not None:
        logging.warning( "Redis client already initialized, skipping re-initialization" )
        return
    
    logging.info( "Initializing Redis client..." )
    
    redis_url = _build_redis_url()
    
    _redis_client = await Redis.from_url(
        redis_url,
        encoding="utf-8",
        decode_responses=True,
        
        retry_on_timeout=True,
        retry_on_error=[ ConnectionError, TimeoutError ],
        
        # Connection settings
        socket_timeout=10,
        socket_connect_timeout=10,
        socket_keepalive=True,
        socket_keepalive_options={},
        
        health_check_interval=30, # Seconds
    )
    
    logging.info( "Redis client created successfully" )

async def close_redis_client():

    global _redis_client
    
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
        logging.info( "Redis client connection closed" )
        
async def get_redis_client() -> Redis:

    if _redis_client is None:
        await init()
    
    return _redis_client
