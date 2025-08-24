from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    
    # Include routers
    app.include_router(router, prefix="/api/v1", tags=["research"])
    
    @app.get("/")
    async def root():
        return {"message": "Research Brief Generator API", "status": "healthy"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "version": "1.0.0"}
    
    return app

# Create app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)