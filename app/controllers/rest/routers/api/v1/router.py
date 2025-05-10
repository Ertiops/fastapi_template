from fastapi import APIRouter

from app.controllers.rest.routers.api.v1.endpoints.book import (
    router as book_router,
)
from app.controllers.rest.routers.api.v1.endpoints.user import (
    router as user_router,
)

router = APIRouter(prefix="/v1")
router.include_router(user_router)
router.include_router(book_router)
