"""FastAPI main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


from src.api.routes import documents, health, query

app = FastAPI(
    title="RAG System API",
    description="A general-purpose RAG system with Docling, Weaviate, FastAPI, ZenML, and MLflow",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(documents.router)
app.include_router(query.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RAG System API",
        "version": "0.1.0",
        "docs": "/docs",
    }

