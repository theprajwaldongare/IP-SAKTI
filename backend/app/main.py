"""
Main FastAPI Application Entry Point for IP Sakti.
Serves static frontend files and API routes.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings
from app.routes import router as api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multilingual AI Assistant for Intellectual Property & Regulatory Guidance in Ayurveda (FastAPI + RAG + LLM)"
)

# Enable CORS for cross-origin requests during dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/health")
def health_check():
    return {
        "status": "online",
        "system": "IP Sakti - Ayurvedic IP & Regulatory Assistant",
        "gemini_api_configured": bool(settings.GEMINI_API_KEY)
    }

# Mount static frontend directory
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))

if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "IP Sakti Backend API is running. Frontend directory not found at " + frontend_dir}
