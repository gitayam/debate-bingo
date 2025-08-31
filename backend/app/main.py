from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from slowapi.errors import RateLimitExceeded

from app.api.bingo import router as bingo_router
from app.api.privacy_auth import router as privacy_auth_router  # Privacy-focused auth
from app.api.websocket import router as websocket_router
# from app.api.auth import router as auth_router  # DEPRECATED - email/password auth removed
# from app.api.socketio_server import socket_app  # Temporarily disabled
from app.core.config import settings
from app.middleware.security import (
    SecurityHeadersMiddleware,
    SecurityEventMiddleware,
    limiter,
    rate_limit_exceeded_handler
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Security middleware (order matters!)
if settings.ALLOWED_HOSTS:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

if settings.ENABLE_SECURITY_HEADERS:
    app.add_middleware(SecurityHeadersMiddleware)
    
app.add_middleware(SecurityEventMiddleware)

# CORS middleware - Hardened configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],  # Specific methods
    allow_headers=["Authorization", "Content-Type", "Accept"],  # Specific headers
    expose_headers=["X-Total-Count"],
)

# Include routers
app.include_router(privacy_auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["privacy-authentication"])
app.include_router(bingo_router, prefix=f"{settings.API_V1_STR}/bingo", tags=["bingo"])
app.include_router(websocket_router, tags=["websocket"])


@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Debate Bingo API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Mount Socket.IO app - temporarily disabled
# app.mount("/", socket_app)