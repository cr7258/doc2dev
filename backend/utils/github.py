#!/usr/bin/env python3
"""
GitHub utilities for repository operations
"""

import os
import re
import asyncio
import base64
import logging
from typing import Tuple, List, Optional, Callable
from urllib.parse import urlparse

from github import Github, GithubException

# Configure logging
logger = logging.getLogger(__name__)


def get_github_token() -> str:
    """Get GitHub token from environment variables"""
    token = os.getenv("GITHUB_TOKEN", "")
    if token:
        masked_token = '*' * (len(token) - 4) + token[-4:] if len(token) > 4 else '****'
        logger.info(f"Loaded GitHub token from .env: {masked_token}")
    else:
        logger.warning("No GitHub token found in environment variables")
    return token


def parse_github_url(url: str) -> str:
    """
    Parse a GitHub URL to extract the repository name in the format 'owner/repo'.

    Args:
        url: GitHub repository URL

    Returns:
        Repository name in the format 'owner/repo'
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
        if re.search(r'github\.com[/:]([\w.-]+)/([\w.-]+)', url):
            match = re.search(r'github\.com[/:]([\w.-]+)/([\w.-]+)', url)
            if match:
                owner, repo = match.groups()
                logger.info(f"Extracted owner: {owner}, repo: {repo}")
                return f"{owner}/{repo}"
        
        # Try parsing HTTPS URL format
        if "github.com/" in url:
            parts = url.split("github.com/")
            if len(parts) > 1 and "/" in parts[1]:
                repo_parts = parts[1].split("/")
                if len(repo_parts) >= 2:
                    owner, repo = repo_parts[0], repo_parts[1]
                    logger.info(f"Extracted from HTTPS URL - owner: {owner}, repo: {repo}")
                    return f"{owner}/{repo}"
        
        # Try parsing SSH URL format
        if "git@github.com:" in url:
            parts = url.split("git@github.com:")
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


def extract_org_repo(url: str) -> Tuple[str, str]:
    """
    Extract organization and repository name from GitHub URL

    Args:
        url: GitHub repository URL

    Returns:
        Tuple[str, str]: Tuple of organization name and repository name
    """
    repo_name = parse_github_url(url)
    parts = repo_name.split('/')
    
    if len(parts) != 2:
        raise ValueError(f"Invalid repository name format: {repo_name}")
        
    return parts[0], parts[1]


def get_repo_contents_using_trees(repo):
    """
    Get all repository contents using Git Trees API, more efficient than recursive approach.

    Args:
        repo: GitHub repository object

    Returns:
        list: List containing file information, each element has path and sha attributes
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


async def download_md_files_with_progress(repo_url: str, output_dir: str, progress_callback: Optional[Callable] = None) -> List[str]:
    """
    Download all Markdown files from a GitHub repository with progress callback support

    Args:
        repo_url (str): GitHub repository URL
        output_dir (str): Directory to save downloaded files
        progress_callback (callable, optional): Progress callback function, receives current, total, message parameters

    Returns:
        list: List of downloaded Markdown file paths
    """
    try:
        # Parse GitHub URL to get repository name
        try:
            repo_name = parse_github_url(str(repo_url))
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
        token = get_github_token()
        if not token:
            logger.error("GitHub token not found in environment variables")
            if progress_callback:
                await progress_callback(0, 1, "GitHub token not found in environment variables")
            return []
        
        # Create GitHub instance
        try:
            g = Github(token)
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
            all_contents = await asyncio.to_thread(get_repo_contents_using_trees, repo)
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
