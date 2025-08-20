from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.bingo import router as bingo_router
from app.api.auth import router as auth_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"])
app.include_router(bingo_router, prefix=f"{settings.API_V1_STR}/bingo", tags=["bingo"])


@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Debate Bingo API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}