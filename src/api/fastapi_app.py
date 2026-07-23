import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.tools_router import router as tools_router
from .routes.sessions_router import router as sessions_router
from .routes.voice_ws_router import router as voice_ws_router
from config.settings import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("FastAPIVoiceApp")

app = FastAPI(
    title="Universal GCP Voice AI Framework API",
    description="API-first Enterprise Voice AI Framework powered by Google Gemini Live API & GCP Ecosystem.",
    version="2.0.0"
)

# Enable CORS for web audio client connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(tools_router)
app.include_router(sessions_router)
app.include_router(voice_ws_router)

@app.get("/health", tags=["System Health"])
async def health_check():
    """Service health check endpoint."""
    return {
        "status": "HEALTHY",
        "project_id": settings.gcp_project_id,
        "provider": settings.provider_type,
        "model": settings.model_name,
        "voice": settings.voice_name
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.fastapi_app:app", host=settings.fastapi_host, port=settings.fastapi_port, reload=True)
