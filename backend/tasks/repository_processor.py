#!/usr/bin/env python3
"""
Repository processing tasks for background operations
"""

import os
import shutil
import tempfile
import logging
from typing import Optional

from utils.github import extract_org_repo, download_md_files_with_progress
from utils.md import count_code_blocks_in_documents
from core.services.document import DocumentService
from core.services.repository import RepositoryService
from core.factories.document import DocumentLoaderFactory, DocumentSplitterFactory
from core.models.repository import RepositoryStatus

# Configure logging
logger = logging.getLogger(__name__)


class RepositoryProcessor:
    """
    Repository processor for handling background repository download and indexing tasks
    """
    
    def __init__(self, websocket_manager, repository_service: RepositoryService, document_service: DocumentService):
        """
        Initialize repository processor
        
        Args:
            websocket_manager: WebSocket connection manager for progress updates
            repository_service: Repository service for database operations
            document_service: Document service for embedding and vector operations
        """
        self.manager = websocket_manager
        self.repository_service = repository_service
        self.document_service = document_service
        self.current_client_id = None
        self.websocket_connected = True
    
    async def _download_progress_callback(self, current, total, message):
        """
        Handle download progress updates via WebSocket
        
        Args:
            current: Current progress count
            total: Total items count
            message: Progress message
        """
        if self.current_client_id and self.websocket_connected:
            progress = int((current / total) * 100) if total > 0 else 0
            self.websocket_connected = await self.manager.send_json({
                "type": "download",
                "status": "in_progress",
                "progress": progress,
                "current": current,
                "total": total,
                "message": message
            }, self.current_client_id)
            
            # If WebSocket connection fails, log and stop trying to send
            if not self.websocket_connected:
                logger.warning(f"WebSocket connection to client {self.current_client_id} failed during download progress update")
                self.current_client_id = None  # Avoid subsequent attempts to send
    
    async def _embedding_progress_callback(self, current, total, message):
        """
        Handle embedding progress updates via WebSocket
        
        Args:
            current: Current progress count
            total: Total items count
            message: Progress message
        """
        if self.current_client_id and self.websocket_connected:
            self.websocket_connected = await self.manager.send_json({
                "type": "embedding",
                "status": "in_progress",
                "progress": int((current / total) * 100) if total > 0 else 0,
                "current": current,
                "total": total,
                "message": message
            }, self.current_client_id)
            
            if not self.websocket_connected:
                logger.warning(f"WebSocket connection to client {self.current_client_id} failed during embedding progress update")
                self.current_client_id = None  # Avoid subsequent attempts to send
    
    async def _embed_and_store_with_progress(self, documents, table_name, drop_old=False, progress_callback=None):
        """
        Embed documents and store to vector database with progress callback support
        
        Args:
            documents: List of documents to embed
            table_name: Vector table name
            drop_old: Whether to drop old table
            progress_callback: Progress callback function
            
        Returns:
            bool: Success status
        """
        import asyncio
        
        total_docs = len(documents)
        
        # Use DocumentService to embed and store documents with progress updates
        try:
            # Initialize progress
            if progress_callback:
                await progress_callback(0, total_docs, "Starting document embedding...")
            
            # Use asyncio.to_thread to convert sync function to async operation
            # This avoids blocking the event loop
            success = await asyncio.to_thread(
                self.document_service.embed_and_store,
                documents, 
                table_name,
                drop_old=drop_old
            )
            
            # Complete progress
            if progress_callback:
                await progress_callback(total_docs, total_docs, "Document embedding completed")
                
            return success
        except Exception as e:
            if progress_callback:
                await progress_callback(0, 1, f"Error embedding documents: {str(e)}")
            raise e
    
    async def process_repository_background(self, repo_url: str, library_name: Optional[str] = None, client_id: Optional[str] = None):
        """
        Process repository download and indexing in background
        
        Args:
            repo_url: Repository URL
            library_name: Optional library name
            client_id: Optional client ID for WebSocket updates
        """
        try:
            # Extract organization and repository name from URL
            org, repo = extract_org_repo(str(repo_url))
            
            # Check if repository already exists
            repo_path = f"{org}/{repo}"
            existing_repo = self.repository_service.get_repository_by_path(repo_path)
            
            # If repository already exists, return directly
            if existing_repo:
                return
                
            # If no library_name provided, generate automatically
            table_name = library_name
            if not table_name:
                table_name = f"{org}_{repo}"
            
            # Ensure hyphens in table name are replaced with underscores
            table_name = table_name.replace("-", "_")
            
            # Set repository status to in_progress
            repo_id = None
            try:
                # First add repository to database with in_progress status
                repo_name = repo.replace("-", " ").title()
                repo_url_full = f"https://github.com/{org}/{repo}"
                
                # Add to repositories table using RepositoryService
                repo_id = self.repository_service.create_repository(
                    name=repo_name,
                    description="",
                    repo=repo_path,
                    repo_url=repo_url_full,
                    repo_status=RepositoryStatus.in_progress,
                    tokens=0,
                    snippets=0
                )
                
                if repo_id:
                    logger.info(f"Added repository with ID: {repo_id}")
            except Exception as e:
                logger.error(f"Error adding repository to database: {str(e)}")
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            logger.info(f"Created temporary directory: {temp_dir}")
            
            # Set up WebSocket connection state
            self.current_client_id = client_id
            self.websocket_connected = True
            
            # Send initial progress information
            if self.current_client_id:
                self.websocket_connected = await self.manager.send_json({
                    "type": "download",
                    "status": "started",
                    "progress": 0,
                    "message": f"Starting download of {org}/{repo} repository..."
                }, self.current_client_id)
                
                # If WebSocket connection fails, log but continue processing
                if not self.websocket_connected:
                    logger.warning(f"WebSocket connection to client {self.current_client_id} failed, but continuing with repository processing")
                    # Set client_id to None to avoid subsequent message attempts
                    self.current_client_id = None



            # Download Markdown files using progress version
            md_files = await download_md_files_with_progress(
                repo_url, 
                temp_dir, 
                progress_callback=self._download_progress_callback if self.current_client_id else None
            )
            
            if not md_files:
                if self.current_client_id and self.websocket_connected:
                    self.websocket_connected = await self.manager.send_json({
                        "type": "download",
                        "status": "error",
                        "progress": 0,
                        "message": "No Markdown files found in repository"
                    }, self.current_client_id)
                    
                    if not self.websocket_connected:
                        logger.warning(f"WebSocket connection to client {self.current_client_id} failed when sending error message")
                        self.current_client_id = None
                
                # If there's a repository ID, update status to failed
                if repo_id:
                    try:
                        self.repository_service.update_repository_status(repo_id, RepositoryStatus.failed)
                        logger.info(f"Updated repository status to 'failed' for ID: {repo_id}")
                    except Exception as e:
                        logger.error(f"Error updating repository status: {str(e)}")
                
                shutil.rmtree(temp_dir)
                return

            # Download completion notification
            if self.current_client_id and self.websocket_connected:
                self.websocket_connected = await self.manager.send_json({
                    "type": "download",
                    "status": "completed",
                    "progress": 100,
                    "message": f"Downloaded {len(md_files)} Markdown files"
                }, self.current_client_id)
                
                if not self.websocket_connected:
                    logger.warning(f"WebSocket connection to client {self.current_client_id} failed when sending download completion message")
                    self.current_client_id = None
            
            # Load Markdown files using DocumentLoaderFactory
            loader_class = DocumentLoaderFactory.get_loader("markdown")
            documents = []
            for file_path in md_files:
                loader = loader_class(file_path)
                docs = loader.load()
                documents.extend(docs)
            
            # Split documents using DocumentSplitterFactory
            splitter = DocumentSplitterFactory.get_splitter("recursive")
            docs = splitter.split_documents(documents)

            # Embed and store documents using progress version
            if self.current_client_id and self.websocket_connected:
                self.websocket_connected = await self.manager.send_json({
                    "type": "embedding",
                    "status": "started",
                    "progress": 0,
                    "message": "Starting document embedding..."
                }, self.current_client_id)
                
                if not self.websocket_connected:
                    logger.warning(f"WebSocket connection to client {self.current_client_id} failed when sending embedding start message")
                    self.current_client_id = None
                        
            try:
                # Embed and store documents
                vector_store = await self._embed_and_store_with_progress(
                    docs, 
                    table_name=table_name, 
                    drop_old=True,
                    progress_callback=self._embedding_progress_callback
                )
                
                # Completion notification
                if self.current_client_id and self.websocket_connected:
                    try:
                        self.websocket_connected = await self.manager.send_json({
                            "type": "embedding",
                            "status": "completed",
                            "progress": 100,
                            "message": f"Successfully embedded {len(docs)} documents to table {table_name}"
                        }, self.current_client_id)
                    except Exception as e:
                        logger.error(f"Error sending embedding completion message: {str(e)}")
                        self.websocket_connected = False
                        self.current_client_id = None
                
                # If there's a repository ID, update status to completed
                if repo_id:
                    try:
                        # Calculate token count and code block count in documents
                        tokens_count = sum(len(doc.page_content.split()) for doc in documents)
                        snippets_count = count_code_blocks_in_documents(documents)
                        
                        # Update repository status
                        self.repository_service.update_repository_status(repo_id, RepositoryStatus.completed)
                        logger.info(f"Updated repository status to 'completed' for ID: {repo_id}")
                        
                        # Update repository token and code snippet counts
                        self.repository_service.update_repository_counts(repo_id, tokens_count, snippets_count)
                        logger.info(f"Updated repository counts for ID: {repo_id} - Tokens: {tokens_count}, Snippets: {snippets_count}")
                    except Exception as e:
                        logger.error(f"Error updating repository status or counts: {str(e)}")
                
                # Repository information already handled above in the repo_id block
                # Send database completion notification
                if self.current_client_id and self.websocket_connected:
                    try:
                        await self.manager.send_json({
                            "type": "database",
                            "status": "completed",
                            "message": f"Repository information updated in database"
                        }, self.current_client_id)
                    except Exception as e:
                        logger.error(f"Error sending database completion message: {str(e)}")
                        self.websocket_connected = False
                        self.current_client_id = None
            except Exception as e:
                logger.error(f"Error embedding documents: {str(e)}")
                
                # Send error notification
                if self.current_client_id and self.websocket_connected:
                    try:
                        await self.manager.send_json({
                            "type": "embedding",
                            "status": "error",
                            "progress": 0,
                            "message": f"Error embedding documents: {str(e)}"
                        }, self.current_client_id)
                    except Exception as ws_err:
                        logger.error(f"Error sending embedding error message: {str(ws_err)}")
                    
                # If there's a repository ID, update status to failed
                if repo_id:
                    try:
                        self.repository_service.update_repository_status(repo_id, RepositoryStatus.failed)
                        logger.info(f"Updated repository status to 'failed' for ID: {repo_id}")
                    except Exception as status_err:
                        logger.error(f"Error updating repository status: {str(status_err)}")
            
            # Clean up temporary directory
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                logger.error(f"Error cleaning up temporary directory: {str(e)}")
                
        except Exception as e:
            logger.error(f"Background task error: {str(e)}")
            if self.current_client_id:
                await self.manager.send_json({
                    "type": "error",
                    "message": f"Error processing repository: {str(e)}"
                }, self.current_client_id)