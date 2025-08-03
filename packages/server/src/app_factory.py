import logging
import time

from configs.index import app_config

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from routes.index import router
from errors.internal_error import InternalError


def create_app() -> FastAPI:

    start_time = time.perf_counter()

    tags_metadata = [ # Metadata for API documentation
        {
            "name": "Health",
            "description": "Endpoints for health checking"
        },
        {
            "name": "Search",
            "description": "Endpoints for regular searching with Weaviate database"
        },
    ]

    app = FastAPI( 
        title="Chat bot API",
        description="API for Chat Bot system implementing RAG",
        version="1.0.0",
        openapi_tags=tags_metadata,
        openapi_url="/openapi.json",
    )

    @app.exception_handler( InternalError )
    async def custom_api_exception_handler( request: Request, exc: InternalError ):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.message,
                "status_code": exc.status_code,
                "stack_trace": exc.stack_trace,
            }
        )

    app.include_router( router, prefix="/api", )

    initialize_extensions( app )
    end_time = time.perf_counter()

    if app_config.DEBUG:
        logging.info( f"Finished create_app ({ round( ( end_time - start_time ) * 1000, 2 ) } ms)" )

    return app


def initialize_extensions( app: FastAPI ):
    from extensions import (
        ext_logging,
        ext_database,
        ext_session,
    )

    extensions = [
        ext_logging,
        ext_database,
        ext_session,
    ]
    for ext in extensions:
        short_name = ext.__name__.split( "." )[ -1 ]
        is_enabled = ext.is_enabled() if hasattr( ext, "is_enabled" ) else True
        if not is_enabled:
            if app_config.DEBUG:
                logging.info( f"Skipped { short_name }" )
            continue

        start_time = time.perf_counter()
        ext.init_app( app )
        end_time = time.perf_counter()
        
        if app_config.DEBUG:
            logging.info( f"Loaded { short_name } ({ round( ( end_time - start_time ) * 1000, 2 ) } ms)" )
