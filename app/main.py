from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import engine, Base
from app.routers import url, auth, bookmarks


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: Clean up resources if needed
    pass


app = FastAPI(
    title="URL Shortener API",
    description="A simple URL shortener built with FastAPI",
    version="1.0.0",
    lifespan=lifespan
)

# Set up CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for now (can restrict in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers (url router LAST — it has a catch-all /{short_code} route)
app.include_router(auth.router)
app.include_router(bookmarks.router)
app.include_router(url.router)


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"message": "Welcome to the URL Shortener API. Visit /docs for documentation."}
