from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx

from .routes import router
from ..utils.config import settings
from ..utils.logger import logger


def create_app() -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(
        title="Research Brief Generator API",
        description="AI-powered research assistant with context awareness",
        version="1.0.0"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers (main API routes under /api/v1)
    app.include_router(router, prefix="/api/v1", tags=["research"])
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {"message": "Research Brief Generator API", "status": "healthy"}
    
    # Health check endpoint
    @app.get("/health")
    async def health():
        return {"status": "healthy", "version": "1.0.0"}
    
    # --- Aliases for easier testing/demo ---
    @app.post("/brief")
    async def brief_alias(request: Request):
        """Alias for POST /api/v1/brief"""
        async with httpx.AsyncClient() as client:
            body = await request.json()
            resp = await client.post(str(request.base_url) + "api/v1/brief", json=body)
        return JSONResponse(content=resp.json(), status_code=resp.status_code)

    @app.get("/brief/{brief_id}")
    async def brief_alias_get(brief_id: str, request: Request):
        """Alias for GET /api/v1/brief/{brief_id}"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(str(request.base_url) + f"api/v1/brief/{brief_id}")
        return JSONResponse(content=resp.json(), status_code=resp.status_code)

    return app


# Create app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
