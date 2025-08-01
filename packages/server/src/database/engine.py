import os
import logging
from typing import Optional

from sqlmodel import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Engine

from configs.index import app_config

_engine: Optional[ Engine ] = None

def build_postgres_url() -> str:
    host = app_config.DB_HOST
    port = app_config.DB_PORT
    user = app_config.DB_USERNAME
    password = app_config.DB_PASSWORD
    database = app_config.DB_DATABASE
    
    # Format: postgresql+psycopg://username:password@host:port/database_name
    url = f"postgresql+psycopg://{ user }:{ password }@{ host }:{ port }/{ database }"
    return url

def init():

    global _engine

    if _engine is not None:
        logging.warning( "Engine already initialized, skipping re-initialization" )
        return
    
    database_type = app_config.DB_TYPE.lower()
    logging.info( f"Initializing database engine for type: { database_type }" )
    
    database_url = build_postgres_url()
    
    _engine = create_engine(
        database_url,
        
        # Connection pool configuration
        poolclass=QueuePool,
        pool_size=app_config.SQLALCHEMY_POOL_SIZE,
        pool_recycle=app_config.SQLALCHEMY_POOL_RECYCLE,
        
        
        # PostgreSQL specific settings
        connect_args={
            "connect_timeout": 10,

            # Combine settings from .env
            "options": f"-c statement_timeout=30000 "
        },
        
        # Logging configuration
        echo=app_config.SQLALCHEMY_ECHO
    )
    
    logging.info( "PostgreSQL engine created successfully" )
            

def get_engine() -> Engine:

    if _engine is None:
        init()

    return _engine
