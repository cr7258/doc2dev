#!/usr/bin/env python3
"""
GitLab platform adapter implementation

This module provides GitLab-specific implementation of the GitPlatformAdapter interface.
It handles GitLab API interactions, authentication, and file operations.
"""

import os
import re
import asyncio
import base64
import logging
from typing import Tuple, List, Optional, Callable
from urllib.parse import urlparse

import gitlab
from gitlab.exceptions import GitlabError, GitlabAuthenticationError

from . import GitPlatformAdapter
from .utils import GitUrlParser, GitConfigHelper
from config.git import get_git_config_manager

# Configure logging
logger = logging.getLogger(__name__)


class GitLabAdapter(GitPlatformAdapter):
    """GitLab platform adapter implementation"""
    
    def __init__(self, base_url: Optional[str] = None):
        """Initialize GitLab adapter

        Args:
            base_url: Optional custom GitLab base URL (for self-hosted GitLab)
        """
        # Use configuration manager for consistent settings
        config_manager = get_git_config_manager()
        gitlab_config = config_manager.get_platform_config('gitlab')

        if base_url:
            self.base_url = base_url
        elif gitlab_config:
            self.base_url = gitlab_config.base_url
        else:
            self.base_url = os.getenv('GITLAB_URL', 'https://gitlab.com')

        self.api_url = f"{self.base_url}/api/v4"
        
    def get_git_token(self) -> str:
        """Get GitLab token from configuration manager

        Returns:
            str: GitLab authentication token
        """
        # Try configuration manager first
        config_manager = get_git_config_manager()
        gitlab_config = config_manager.get_platform_config('gitlab')

        if gitlab_config and gitlab_config.token:
            token = gitlab_config.token
        else:
            # Fallback to environment variable
            token = os.getenv("GITLAB_TOKEN", "")

        if token:
            masked_token = '*' * (len(token) - 4) + token[-4:] if len(token) > 4 else '****'
            logger.info(f"Loaded GitLab token: {masked_token}")
        else:
            logger.warning("No GitLab token found in configuration or environment variables")
        return token
    
    def parse_git_url(self, url: str) -> str:
        """Parse GitLab URL to extract repository name in 'owner/repo' format
        
        Args:
            url: GitLab repository URL
            
        Returns:
            str: Repository name in 'owner/repo' format
        """
        # Log original URL for debugging
        logger.info(f"Parsing GitLab URL: {url}")
        
        # Remove whitespace from URL
        url = url.strip()
        
        # Remove .git suffix if present
        if url.endswith(".git"):
            url = url[:-4]
        
        # Handle different URL formats
        try:
            # Use regex to match common GitLab URL formats
            # Support both gitlab.com and custom domains
            domain_pattern = self._get_domain_pattern()
            
            if re.search(rf'{domain_pattern}[/:]([\w.-]+)/([\w.-]+)', url):
                match = re.search(rf'{domain_pattern}[/:]([\w.-]+)/([\w.-]+)', url)
                if match:
                    owner, repo = match.groups()
                    logger.info(f"Extracted owner: {owner}, repo: {repo}")
                    return f"{owner}/{repo}"
            
            # Try parsing HTTPS URL format
            domain = self._get_domain()
            if f"{domain}/" in url:
                parts = url.split(f"{domain}/")
                if len(parts) > 1 and "/" in parts[1]:
                    repo_parts = parts[1].split("/")
                    if len(repo_parts) >= 2:
                        owner, repo = repo_parts[0], repo_parts[1]
                        logger.info(f"Extracted from HTTPS URL - owner: {owner}, repo: {repo}")
                        return f"{owner}/{repo}"
            
            # Try parsing SSH URL format
            ssh_pattern = f"git@{domain}:"
            if ssh_pattern in url:
                parts = url.split(ssh_pattern)
                if len(parts) > 1 and "/" in parts[1]:
                    repo_parts = parts[1].split("/")
                    if len(repo_parts) >= 2:
                        owner, repo = repo_parts[0], repo_parts[1]
                        logger.info(f"Extracted from SSH URL - owner: {owner}, repo: {repo}")
                        return f"{owner}/{repo}"
        
            # If all above methods fail, try extracting last two path components from URL
            parsed_url = urlparse(url)
            path_parts = [p for p in parsed_url.path.split("/") if p]
            if len(path_parts) >= 2:
                owner, repo = path_parts[-2], path_parts[-1]
                logger.info(f"Extracted from URL path - owner: {owner}, repo: {repo}")
                return f"{owner}/{repo}"
                
            raise ValueError(f"Unable to extract repository information from URL")
        except Exception as e:
            logger.error(f"Error parsing GitLab URL: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise ValueError(f"Error parsing GitLab URL: {str(e)}")
        
        raise ValueError(f"Invalid GitLab URL format: {url}")
    
    def extract_org_repo(self, url: str) -> Tuple[str, str]:
        """Extract organization and repository name from GitLab URL
        
        Args:
            url: GitLab repository URL
            
        Returns:
            Tuple[str, str]: (organization, repository) names
        """
        repo_name = self.parse_git_url(url)
        parts = repo_name.split('/')
        
        if len(parts) != 2:
            raise ValueError(f"Invalid repository name format: {repo_name}")
            
        return parts[0], parts[1]
    
    def get_repo_contents_using_trees(self, project) -> List:
        """Get repository contents using GitLab API

        Args:
            project: GitLab project object

        Returns:
            List: List of file objects with path and other attributes
        """
        try:
            logger.info("Getting GitLab repository contents using tree API...")

            # Get default branch
            default_branch = project.default_branch
            logger.info(f"Using default branch: {default_branch}")

            # Get repository tree recursively
            # GitLab API: GET /projects/:id/repository/tree?recursive=true
            tree_items = project.repository_tree(ref=default_branch, recursive=True, all=True)
            logger.info(f"Got repository tree with {len(tree_items)} items")

            # Convert GitLab tree items to a format compatible with GitHub
            # GitLab tree items have: id, name, type, path, mode
            file_objects = []
            for item in tree_items:
                if item['type'] == 'blob':  # Only include files, not directories
                    # Create a simple object with path and id (similar to GitHub's sha)
                    file_obj = type('GitLabFile', (), {
                        'path': item['path'],
                        'sha': item['id'],  # GitLab uses 'id' instead of 'sha'
                        'type': item['type'],
                        'mode': item['mode']
                    })()
                    file_objects.append(file_obj)

            logger.info(f"Filtered {len(file_objects)} files from repository tree")
            return file_objects

        except Exception as e:
            logger.error(f"Error getting GitLab repository tree: {e}")
            return []
    
    async def download_md_files_with_progress(
        self,
        repo_url: str,
        output_dir: str,
        progress_callback: Optional[Callable] = None
    ) -> List[str]:
        """Download Markdown files with progress tracking
        
        Args:
            repo_url: GitLab repository URL
            output_dir: Directory to save downloaded files
            progress_callback: Optional progress callback function
            
        Returns:
            List[str]: List of downloaded file paths
        """
        try:
            # Parse GitLab URL to get repository name
            try:
                repo_name = self.parse_git_url(str(repo_url))
                logger.info(f"Parsed repo name: {repo_name}")
            except ValueError as e:
                logger.error(f"Error parsing GitLab URL: {str(e)}")
                if progress_callback:
                    await progress_callback(0, 1, f"URL format error: {str(e)}")
                return []
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            print(f"Created directory: {output_dir}")

            # Get GitLab token
            token = self.get_git_token()
            if not token:
                logger.error("GitLab token not found in environment variables")
                if progress_callback:
                    await progress_callback(0, 1, "GitLab token not found in environment variables")
                return []
            
            # Create GitLab instance
            try:
                gl = gitlab.Gitlab(self.base_url, private_token=token)
                # Test authentication
                gl.auth()
                logger.info(f"Successfully authenticated with GitLab at {self.base_url}")
            except Exception as e:
                logger.error(f"Error initializing GitLab API: {str(e)}")
                if progress_callback:
                    await progress_callback(0, 1, f"Error initializing GitLab API: {str(e)}")
                return []

            # Get project
            try:
                logger.info(f"Getting GitLab project: {repo_name}")
                # python-gitlab library automatically handles URL encoding
                project = await asyncio.to_thread(gl.projects.get, repo_name)
                logger.info(f"Successfully retrieved GitLab project: {project.name}")

            except Exception as e:
                logger.error(f"Error getting GitLab project {repo_name}: {str(e)}")
                if progress_callback:
                    await progress_callback(0, 1, f"Error getting project: {str(e)}")
                return []

            # Send progress update: start getting repository contents
            if progress_callback:
                await progress_callback(0, 1, "Getting repository contents...")

            # Use tree structure API to get all contents
            try:
                logger.info("Getting GitLab repository contents using tree API...")
                all_contents = await asyncio.to_thread(self.get_repo_contents_using_trees, project)
                logger.info(f"Found {len(all_contents)} total items in repository")
            except Exception as e:
                logger.error(f"Error getting repository contents: {str(e)}")
                if progress_callback:
                    await progress_callback(0, 1, f"Error getting repository contents: {str(e)}")
                return []

            # Filter out Markdown files
            md_files = [content for content in all_contents if content.path.lower().endswith(".md")]
            logger.info(f"Found {len(md_files)} Markdown files in repository")

            if not md_files:
                logger.warning("No Markdown files found in repository")
                if progress_callback:
                    await progress_callback(0, 1, "No Markdown files found in repository")
                return []

            # Send progress update: start downloading files
            if progress_callback:
                await progress_callback(0, len(md_files), f"Found {len(md_files)} Markdown files, starting download...")

            # Download Markdown files
            downloaded_files = []
            for i, content in enumerate(md_files):
                try:
                    # Create necessary directory structure
                    file_path = os.path.join(output_dir, content.path)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)

                    # Download file content using GitLab API
                    logger.info(f"Downloading file: {content.path}")

                    try:
                        # Use GitLab's repository file API
                        file_info = await asyncio.to_thread(
                            project.files.get,
                            file_path=content.path,
                            ref=project.default_branch
                        )
                        # Decode content
                        file_content = base64.b64decode(file_info.content)
                    except Exception as file_error:
                        logger.warning(f"Error getting file {content.path}: {file_error}")
                        # Continue with next file
                        continue

                    # Save file
                    with open(file_path, "wb") as f:
                        f.write(file_content)

                    downloaded_files.append(file_path)
                    logger.info(f"Successfully downloaded: {file_path}")

                    # Update progress
                    if progress_callback:
                        await progress_callback(i + 1, len(md_files), f"Downloaded {i + 1}/{len(md_files)}: {content.path}")
                except Exception as e:
                    logger.error(f"Error downloading file {content.path}: {str(e)}")
                    # Continue downloading other files, don't interrupt the entire process

            return downloaded_files

        except GitlabAuthenticationError as e:
            error_message = f"GitLab authentication error: {str(e)}"
            logger.error(error_message)
            if progress_callback:
                await progress_callback(0, 1, error_message)
            return []
        except GitlabError as e:
            error_message = f"GitLab API error: {str(e)}"
            logger.error(error_message)
            if progress_callback:
                await progress_callback(0, 1, error_message)
            return []
        except Exception as e:
            error_message = f"Error downloading markdown files from GitLab: {str(e)}"
            logger.error(error_message)
            if progress_callback:
                await progress_callback(0, 1, error_message)
            return []
    
    def get_git_name(self) -> str:
        """Get platform name identifier
        
        Returns:
            str: Platform name 'gitlab'
        """
        return "gitlab"
    
    def get_git_api_base_url(self) -> str:
        """Get GitLab API base URL
        
        Returns:
            str: GitLab API base URL
        """
        return self.api_url
    
    def _get_domain(self) -> str:
        """Get domain from base URL
        
        Returns:
            str: Domain name
        """
        try:
            parsed = urlparse(self.base_url)
            return parsed.netloc
        except Exception:
            return 'gitlab.com'
    
    def _get_domain_pattern(self) -> str:
        """Get regex pattern for domain matching
        
        Returns:
            str: Regex pattern for domain
        """
        domain = self._get_domain()
        # Escape dots for regex
        return domain.replace('.', r'\.')


__all__ = [
    "GitLabAdapter"
]
