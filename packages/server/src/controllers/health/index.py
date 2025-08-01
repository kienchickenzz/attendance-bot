import logging

from fastapi import status

import requests

from datetime import datetime, timezone


from models.health import HealthCheckResponse, DbHealthCheckResponse

from configs.index import app_config


def health_check():
    """
    Simple health check endpoint to verify API server is running.
    """
    current_time = datetime.now( timezone.utc )

    logging.info( "Hello" )

    return HealthCheckResponse(
        status_code=status.HTTP_200_OK,
        message="Server is running",
        timestamp=current_time.isoformat(),
    )


def weaviate_health_check():
    """
    Check connection status to the Weaviate database.
    """

    current_timestamp = datetime.now( timezone.utc ).isoformat()
    message = ""
    
    # Default values
    database_info = {
        "is_live": False,
        "is_ready": False,
        "version": "unknown",
    }
    
    try:
        # Check if Weaviate is live
        live_response = requests.get( f"{ app_config.WEAVIATE_URL }/v1/.well-known/live" )
        is_live = live_response.status_code == 200
        
        # Check if Weaviate is ready
        ready_response = requests.get( f"{ app_config.WEAVIATE_URL }/v1/.well-known/ready" )
        # logging.info()
        is_ready = ready_response.status_code == 200

        # Get Weaviate version from meta endpoint
        meta_response = requests.get( f"{ app_config.WEAVIATE_URL }/v1/meta" )
        if meta_response.status_code == 200:
            meta_data = meta_response.json()
            version = meta_data.get( "version", "unknown" )

        database_info.update( {
            "is_live": is_live,
            "is_ready": is_ready,
            "version": version
        } )

    except Exception as e:
        message = f"Error connecting to database: { str( e ) }"

    message = "Database health check successfully"

    return DbHealthCheckResponse(
        status_code=status.HTTP_200_OK,
        message=message,
        timestamp=current_timestamp,
        database_info=database_info,
    )
