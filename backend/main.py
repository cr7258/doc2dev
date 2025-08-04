#!/usr/bin/env python3
"""
FastAPI server for Doc2Dev API
"""

import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import route modules
from routes import base_router, repository_router, query_router, websocket_router
from routes.auth import router as auth_router
from routes.platforms import router as platforms_router

# Import global services
from config.settings import Settings
from core.services.repository import RepositoryService
from core.services.document import DocumentService
from core.database.router import DatabaseRouter
from core.auth.service import GitHubOAuthService
from utils.websocket import ConnectionManager
from tasks.repository_processor import RepositoryProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
# Force reload .env file, ignore cache
load_dotenv(override=True)

app = FastAPI(
    title="Doc2Dev API",
    description="GitHub repository markdown downloader and vector database API",
    version="1.0.0"
)

# Create global WebSocket connection manager
manager = ConnectionManager()

# Initialize global service instances
settings = Settings()
db_router = DatabaseRouter(settings)
repository_service = RepositoryService(db_router)
document_service = DocumentService(settings, db_router)
github_oauth_service = GitHubOAuthService(
    users_session=db_router.get_users_session(),
    db_router=db_router,
    client_id=settings.github_client_id,
    client_secret=settings.github_client_secret,
    jwt_secret=settings.jwt_secret_key
)

# Create global RepositoryProcessor instance with service dependencies
repository_processor = RepositoryProcessor(manager, repository_service, document_service)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(base_router)
app.include_router(auth_router)
app.include_router(repository_router)
app.include_router(query_router)
app.include_router(websocket_router)
app.include_router(platforms_router)

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
