from fastapi import APIRouter

from routes.health.index import health_router
from routes.search.index import search_router
from routes.session.index import session_router


router = APIRouter()

router.include_router( health_router, prefix="/health", tags=[ "Health" ] )
router.include_router( search_router, prefix="/search", tags=[ "Search" ] )
router.include_router( session_router, prefix="/session", tags=[ "Session" ] )
