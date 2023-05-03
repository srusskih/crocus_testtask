from fastapi import FastAPI, HTTPException, responses
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from app import exc, exception_handlers

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_exception_handler(exc.Conflict, exception_handlers.handle_conflict)
app.add_exception_handler(exc.NotFound, exception_handlers.handle_not_found)

app.include_router(api_router, prefix=settings.API_V1_STR)