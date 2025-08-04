#!/usr/bin/env python3
"""
Git platform abstraction layer for Doc2Dev

This module provides a unified interface for different Git platforms (GitHub, GitLab)
through the adapter pattern.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Callable, Tuple


class GitPlatformAdapter(ABC):
    """Git platform adapter abstract base class
    
    This abstract class defines the unified interface for different Git platforms.
    Each platform (GitHub, GitLab) should implement this interface to provide
    consistent functionality across the application.
    """

    @abstractmethod
    def get_git_token(self) -> str:
        """Get platform authentication token
        
        Returns:
            str: Platform-specific authentication token
        """
        pass

    @abstractmethod
    def parse_git_url(self, url: str) -> str:
        """Parse platform URL to extract owner/repo format
        
        Args:
            url: Git repository URL
            
        Returns:
            str: Parsed repository path in owner/repo format
        """
        pass

    @abstractmethod
    def extract_org_repo(self, url: str) -> Tuple[str, str]:
        """Extract organization and repository name from URL
        
        Args:
            url: Git repository URL
            
        Returns:
            Tuple[str, str]: (organization, repository) names
        """
        pass

    @abstractmethod
    def get_repo_contents_using_trees(self, repo_client) -> List:
        """Get repository file tree contents
        
        Args:
            repo_client: Platform-specific repository client object
            
        Returns:
            List: List of file objects in the repository
        """
        pass

    @abstractmethod
    async def download_md_files_with_progress(
        self,
        repo_url: str,
        output_dir: str,
        progress_callback: Optional[Callable] = None
    ) -> List[str]:
        """Download Markdown files with progress tracking
        
        Args:
            repo_url: Repository URL
            output_dir: Local directory to save files
            progress_callback: Optional callback function for progress updates
            
        Returns:
            List[str]: List of downloaded file paths
        """
        pass

    @abstractmethod
    def get_git_name(self) -> str:
        """Get platform name identifier
        
        Returns:
            str: Platform name (e.g., 'github', 'gitlab')
        """
        pass

    @abstractmethod
    def get_git_api_base_url(self) -> str:
        """Get platform API base URL
        
        Returns:
            str: API base URL for the platform
        """
        pass


__all__ = [
    "GitPlatformAdapter"
]
