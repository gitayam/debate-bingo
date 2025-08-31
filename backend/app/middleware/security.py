"""Security middleware for FastAPI application."""
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

# Rate limiter instance
limiter = Limiter(key_func=get_remote_address)

# Security logger
security_logger = logging.getLogger("security")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Add CSP header
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' ws: wss:; "
            "font-src 'self'"
        )
        
        # Add HSTS in production
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class SecurityEventMiddleware(BaseHTTPMiddleware):
    """Log security events and suspicious activity."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log security-relevant requests
        if any(suspicious in str(request.url).lower() for suspicious in [
            "admin", "api/v1/auth", ".env", "config", "secret"
        ]):
            security_logger.info(
                "Security-relevant request",
                extra={
                    "method": request.method,
                    "path": str(request.url.path),
                    "client_ip": request.client.host if request.client else "unknown",
                    "user_agent": request.headers.get("user-agent", "unknown")
                }
            )
        
        try:
            response = await call_next(request)
            
            # Log failed authentication attempts
            if response.status_code == 401:
                security_logger.warning(
                    "Authentication failure",
                    extra={
                        "method": request.method,
                        "path": str(request.url.path), 
                        "client_ip": request.client.host if request.client else "unknown",
                        "status_code": response.status_code
                    }
                )
            
            return response
            
        except Exception as e:
            security_logger.error(
                "Request processing error",
                extra={
                    "method": request.method,
                    "path": str(request.url.path),
                    "client_ip": request.client.host if request.client else "unknown",
                    "error": str(e)
                }
            )
            raise


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom rate limit exceeded handler with security logging."""
    security_logger.warning(
        "Rate limit exceeded",
        extra={
            "client_ip": request.client.host if request.client else "unknown",
            "path": str(request.url.path),
            "retry_after": exc.retry_after
        }
    )
    
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "detail": f"Too many requests. Try again in {exc.retry_after} seconds.",
            "retry_after": exc.retry_after
        }
    )


# Rate limiting decorators for endpoints
def auth_rate_limit():
    """Rate limit for authentication endpoints: 5 attempts per minute."""
    return limiter.limit("5/minute")


def api_rate_limit():
    """Rate limit for API endpoints: 100 requests per minute."""
    return limiter.limit("100/minute")


def websocket_rate_limit():
    """Rate limit for WebSocket connections: 10 connections per minute."""
    return limiter.limit("10/minute")