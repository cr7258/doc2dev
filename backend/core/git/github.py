#!/usr/bin/env python3
"""
GitHub platform adapter implementation

This module provides GitHub-specific implementation of the GitPlatformAdapter interface.
It handles GitHub API interactions, authentication, and file operations.
"""

import os
import re
import asyncio
import base64
import logging
from typing import Tuple, List, Optional, Callable
from urllib.parse import urlparse

from github import Github, GithubException

from . import GitPlatformAdapter
from .utils import GitUrlParser, GitConfigHelper
from config.git import get_git_config_manager

# Configure logging
logger = logging.getLogger(__name__)


class GitHubAdapter(GitPlatformAdapter):
    """GitHub platform adapter implementation"""
    
    def __init__(self, base_url: Optional[str] = None):
        """Initialize GitHub adapter

        Args:
            base_url: Optional custom GitHub base URL (for GitHub Enterprise)
        """
        # Use configuration manager for consistent settings
        config_manager = get_git_config_manager()
        github_config = config_manager.get_platform_config('github')

        if base_url:
            self.base_url = base_url
        elif github_config:
            self.base_url = github_config.base_url
        else:
            self.base_url = os.getenv('GITHUB_URL', 'https://github.com')

        self.api_url = self._get_api_url()
        
    def get_git_token(self) -> str:
        """Get GitHub token from configuration manager

        Returns:
            str: GitHub authentication token
        """
        # Try configuration manager first
        config_manager = get_git_config_manager()
        github_config = config_manager.get_platform_config('github')

        if github_config and github_config.token:
            token = github_config.token
        else:
            # Fallback to environment variable
            token = os.getenv("GITHUB_TOKEN", "")

        if token:
            masked_token = '*' * (len(token) - 4) + token[-4:] if len(token) > 4 else '****'
            logger.info(f"Loaded GitHub token: {masked_token}")
        else:
            logger.warning("No GitHub token found in configuration or environment variables")
        return token
    
    def parse_git_url(self, url: str) -> str:
        """Parse GitHub URL to extract repository name in 'owner/repo' format
        
        Args:
            url: GitHub repository URL
            
        Returns:
            str: Repository name in 'owner/repo' format
        """
        # Log original URL for debugging
        logger.info(f"Parsing GitHub URL: {url}")
        
        # Remove whitespace from URL
        url = url.strip()
        
        # Remove .git suffix if present
        if url.endswith(".git"):
            url = url[:-4]
        
        # Handle different URL formats
        try:
            # Use regex to match common GitHub URL formats
            # Support both github.com and custom domains
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
            logger.error(f"Error parsing GitHub URL: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise ValueError(f"Error parsing GitHub URL: {str(e)}")
        
        raise ValueError(f"Invalid GitHub URL format: {url}")
    
    def extract_org_repo(self, url: str) -> Tuple[str, str]:
        """Extract organization and repository name from GitHub URL
        
        Args:
            url: GitHub repository URL
            
        Returns:
            Tuple[str, str]: (organization, repository) names
        """
        repo_name = self.parse_git_url(url)
        parts = repo_name.split('/')
        
        if len(parts) != 2:
            raise ValueError(f"Invalid repository name format: {repo_name}")
            
        return parts[0], parts[1]
    
    def get_repo_contents_using_trees(self, repo) -> List:
        """Get repository contents using Git Trees API
        
        Args:
            repo: GitHub repository object
            
        Returns:
            List: List of file objects with path and sha attributes
        """
        try:
            # Get default branch
            default_branch = repo.default_branch
            logger.info(f"Using default branch: {default_branch}")
            
            # Get tree structure, recursive=True gets all subdirectories
            tree = repo.get_git_tree(default_branch, recursive=True)
            logger.info(f"Got repository tree with {len(tree.tree)} items")
            
            # Return all files
            return tree.tree
        except Exception as e:
            logger.error(f"Error getting repository tree: {e}")
            return []
    
    async def download_md_files_with_progress(
        self,
        repo_url: str,
        output_dir: str,
        progress_callback: Optional[Callable] = None
    ) -> List[str]:
        """Download Markdown files with progress tracking
        
        Args:
            repo_url: GitHub repository URL
            output_dir: Directory to save downloaded files
            progress_callback: Optional progress callback function
            
        Returns:
            List[str]: List of downloaded file paths
        """
        try:
            # Parse GitHub URL to get repository name
            try:
                repo_name = self.parse_git_url(str(repo_url))
                logger.info(f"Parsed repo name: {repo_name}")
            except ValueError as e:
                logger.error(f"Error parsing GitHub URL: {str(e)}")
                if progress_callback:
                    await progress_callback(0, 1, f"URL format error: {str(e)}")
                return []
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            print(f"Created directory: {output_dir}")

            # Get GitHub token
            token = self.get_git_token()
            if not token:
                logger.error("GitHub token not found in environment variables")
                if progress_callback:
                    await progress_callback(0, 1, "GitHub token not found in environment variables")
                return []
            
            # Create GitHub instance
            try:
                g = Github(token, base_url=self.api_url)
                # Check API rate limit
                rate_limit = await asyncio.to_thread(g.get_rate_limit)
                logger.info(f"GitHub API rate limit: {rate_limit.core.remaining}/{rate_limit.core.limit} requests remaining")
            except Exception as e:
                logger.error(f"Error initializing GitHub API: {str(e)}")
                if progress_callback:
                    await progress_callback(0, 1, f"Error initializing GitHub API: {str(e)}")
                return []

            # Get repository
            try:
                logger.info(f"Getting repository: {repo_name}")
                repo = await asyncio.to_thread(g.get_repo, repo_name)
                logger.info(f"Successfully got repository: {repo.full_name}")
            except Exception as e:
                logger.error(f"Error getting repository {repo_name}: {str(e)}")
                if progress_callback:
                    await progress_callback(0, 1, f"Error getting repository: {str(e)}")
                return []

            # Send progress update: start getting repository contents
            if progress_callback:
                await progress_callback(0, 1, "Getting repository contents...")

            # Use tree structure API to get all contents
            try:
                logger.info("Getting repository contents using tree API...")
                # Use asyncio.to_thread to convert sync function to async operation
                all_contents = await asyncio.to_thread(self.get_repo_contents_using_trees, repo)
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

                    # Download file content
                    logger.info(f"Downloading file: {content.path}")
                    
                    # Use blob to get content, more efficient
                    try:
                        # Use asyncio.to_thread to convert sync GitHub API call to async operation
                        blob = await asyncio.to_thread(repo.get_git_blob, content.sha)
                        # Decode content based on encoding
                        if blob.encoding == 'base64':
                            file_content = base64.b64decode(blob.content)
                        else:
                            file_content = blob.content.encode('utf-8')
                    except Exception as blob_error:
                        logger.warning(f"Error getting blob for {content.path}: {blob_error}, falling back to get_contents")
                        # If getting blob fails, fall back to using get_contents
                        contents = await asyncio.to_thread(repo.get_contents, content.path)
                        file_content = contents.decoded_content

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

        except GithubException as e:
            error_message = f"GitHub API error: {e.status} - {e.data.get('message', str(e))}"
            print(f"GitHub Exception: {error_message}")
            print(f"Exception details: {e}")
            
            # Send error progress update
            if progress_callback:
                await progress_callback(0, 1, error_message)
                
            return []
        except Exception as e:
            error_message = f"Error downloading markdown files: {str(e)}"
            print(error_message)
            
            # Send error progress update
            if progress_callback:
                await progress_callback(0, 1, error_message)
            
            return []
    
    def get_git_name(self) -> str:
        """Get platform name identifier
        
        Returns:
            str: Platform name 'github'
        """
        return "github"
    
    def get_git_api_base_url(self) -> str:
        """Get GitHub API base URL
        
        Returns:
            str: GitHub API base URL
        """
        return self.api_url
    
    def _get_api_url(self) -> str:
        """Get GitHub API URL based on base URL
        
        Returns:
            str: GitHub API URL
        """
        if self.base_url == 'https://github.com':
            return 'https://api.github.com'
        else:
            # GitHub Enterprise Server
            return f"{self.base_url}/api/v3"
    
    def _get_domain(self) -> str:
        """Get domain from base URL
        
        Returns:
            str: Domain name
        """
        try:
            parsed = urlparse(self.base_url)
            return parsed.netloc
        except Exception:
            return 'github.com'
    
    def _get_domain_pattern(self) -> str:
        """Get regex pattern for domain matching
        
        Returns:
            str: Regex pattern for domain
        """
        domain = self._get_domain()
        # Escape dots for regex
        return domain.replace('.', r'\.')


__all__ = [
    "GitHubAdapter"
]
