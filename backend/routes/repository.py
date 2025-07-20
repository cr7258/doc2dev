#!/usr/bin/env python3
"""
Repository routes for Doc2Dev API
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from core.models.api import RepositoryRequest, DownloadResponse
from utils.github import extract_org_repo
from core.services.repository import RepositoryService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/download/", response_model=DownloadResponse)
async def download_repository(repo_request: RepositoryRequest, background_tasks: BackgroundTasks):
    """
    Download markdown files from a GitHub repository directly to the project directory
    and automatically embed them if embedding functionality is available.

    Args:
        repo_request: Repository request containing URL and optional client_id for WebSocket updates

    Returns:
        JSON response with download status and embedding status
    """
    try:
        # Extract organization and repository name from URL
        org, repo = extract_org_repo(str(repo_request.repo_url))
        
        # Import global repository service from main module
        from main import repository_service
        
        # Check if repository already exists
        repo_path = f"{org}/{repo}"
        existing_repo = repository_service.get_repository_by_path(repo_path)
        
        # If no library_name provided, auto-generate
        table_name = repo_request.library_name
        if not table_name:
            table_name = f"{org}_{repo}"
        
        # Ensure table name replaces hyphens with underscores
        table_name = table_name.replace("-", "_")
        
        # If repository already exists, return notification
        if existing_repo:
            repo_name = existing_repo.name
            repo_path = existing_repo.repo
            
            # Generate query page URL with table name, repository name and repository path
            # Use actual table name, not the currently generated table_name
            # Table name should be repository path with slashes replaced by underscores, hyphens replaced by underscores
            actual_table_name = repo_path.replace('/', '_').replace('-', '_')
            
            # Generate query page URL
            query_url = f"http://localhost:3000/query?table={actual_table_name}&repo_name={repo_name}&repo_path={repo_path}"
            
            return DownloadResponse(
                status="exists",
                message=f"This repository has already been submitted. Check {repo_path} to see it.",
                table_name=actual_table_name,
                query_url=query_url,
                repo_path=repo_path
            )
        
        # Process repository download and indexing in background task
        # Import global repository_processor from main module
        from main import repository_processor
        background_tasks.add_task(
            repository_processor.process_repository_background,
            str(repo_request.repo_url),
            repo_request.library_name,
            repo_request.client_id
        )
        
        # Generate query page URL
        query_url = f"http://localhost:3000/query?table={table_name}&repo_name={repo.replace('-', ' ').title()}&repo_path={repo_path}"
        
        # Return response indicating task started in background
        return DownloadResponse(
            status="accepted",
            message=f"Repository processing started in background. You can continue using the application while the repository is being processed.",
            table_name=table_name,
            query_url=query_url,
            repo_path=repo_path
        )

    except ValueError as e:
        logger.error(f"ValueError in download_repository: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Exception in download_repository: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.get("/repositories/")
async def get_repositories():
    """
    Get all repository information
    
    Returns:
        JSON response containing all repository information
    """
    try:
        # Import global repository service from main module
        from main import repository_service
        
        repositories = repository_service.get_all_repositories()
        
        # Convert ORM objects to dictionaries and handle time conversion
        repo_list = []
        for repo in repositories:
            repo_dict = {
                "id": repo.id,
                "name": repo.name,
                "description": repo.description,
                "repo": repo.repo,
                "repo_url": repo.repo_url,
                "repo_status": repo.repo_status.value if repo.repo_status else None,
                "tokens": repo.tokens,
                "snippets": repo.snippets,
                "created_at": repo.created_at.isoformat() if repo.created_at else None,
                "updated_at": repo.updated_at.isoformat() if repo.updated_at else None
            }
            repo_list.append(repo_dict)
        
        return {"status": "success", "repositories": repo_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get repository information: {str(e)}")


@router.get("/repositories/{repo_path}")
async def get_repository_details(repo_path: str):
    """
    Get detailed information for a specific repository
    
    Args:
        repo_path: Repository path in format owner/repo
        
    Returns:
        JSON response containing repository detailed information
    """
    try:
        # Import global repository service from main module
        from main import repository_service
        
        # Replace underscores with slashes in path
        repo_path = repo_path.replace("_", "/")
        
        # Get repository information
        repository = repository_service.get_repository_by_path(repo_path)
        
        if not repository:
            raise HTTPException(status_code=404, detail=f"Repository not found: {repo_path}")
        
        # Convert ORM object to dictionary with proper time formatting
        repo_dict = {
            "id": repository.id,
            "name": repository.name,
            "description": repository.description,
            "repo": repository.repo,
            "repo_url": repository.repo_url,
            "repo_status": repository.repo_status.value if repository.repo_status else None,
            "tokens": repository.tokens,
            "snippets": repository.snippets,
            "created_at": repository.created_at.isoformat() if repository.created_at else None,
            "updated_at": repository.updated_at.isoformat() if repository.updated_at else None
        }
        
        return {"status": "success", "repository": repo_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get repository detailed information: {str(e)}")


@router.delete("/repositories/{repo_id}")
async def delete_repository_endpoint(repo_id: int):
    """
    Delete repository
    
    Args:
        repo_id: Repository ID
        
    Returns:
        JSON response with delete status
    """
    try:
        # Import global repository service from main module
        from main import repository_service
        
        # Get repository information using RepositoryService
        repository = repository_service.get_repository_by_id(repo_id)
        
        if not repository:
            raise HTTPException(status_code=404, detail=f"Repository does not exist: ID {repo_id}")
        
        # Get repository path for generating table name
        repo_path = repository.repo
        # Ensure path has no leading slash
        if repo_path.startswith('/'):
            repo_path = repo_path[1:]
        
        # Generate table name
        table_name = repo_path.replace('/', '_').replace('-', '_')
        
        # Delete vector table (temporarily using direct import until we add this to RepositoryService)
        try:
            from repository_db import delete_vector_table
            vector_table_deleted = delete_vector_table(table_name)
            if vector_table_deleted:
                logger.info(f"Deleted vector table: {table_name}")
            else:
                logger.warning(f"Failed to delete vector table: {table_name}")
        except Exception as e:
            logger.error(f"Failed to delete vector table: {str(e)}")
            # Even if deleting vector table fails, we still try to delete database record
        
        # Delete database record using RepositoryService
        success = repository_service.delete_repository(repo_id)
        
        if success:
            return {
                "status": "success",
                "message": f"Successfully deleted repository: {repository.name}"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete repository record")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete repository: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete repository: {str(e)}")
