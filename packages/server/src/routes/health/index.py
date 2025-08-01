from fastapi import APIRouter

from controllers.health import index as health_controller

from models.health import HealthCheckResponse, DbHealthCheckResponse

health_router = APIRouter()

@health_router.get( 
    path="/", 
    responses={
        200: { "model": HealthCheckResponse, },
    },
)
def health_check():
    return health_controller.health_check()

@health_router.get( 
    path="/db",
    responses={
        200: { "model": DbHealthCheckResponse, },
    },
)
def weaviate_health_check():
    return health_controller.weaviate_health_check()
