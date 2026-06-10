from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import init_db
from .routers import auth, scanner, history

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run startup events
    await init_db()
    yield
    # Run shutdown events (if any)

app = FastAPI(
    title="Instagram Fake Account Detector API",
    description="Backend API for predicting fake Instagram accounts with history and authentication.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for React Frontend (supports local development and wildcard production urls)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production to frontend url
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(scanner.router)
app.include_router(history.router)

@app.get("/api/health", tags=["health"])
async def health_check():
    """Health check endpoint to keep Render backend warm."""
    return {"status": "healthy", "service": "fake-account-detector-api"}

@app.get("/", tags=["health"])
async def root():
    return {"message": "Welcome to the Instagram Fake Account Detector API. Visit /docs for documentation."}
