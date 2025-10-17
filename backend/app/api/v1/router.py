"""Main API router for v1."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, posts, templates

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
