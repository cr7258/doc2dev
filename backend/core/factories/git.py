#!/usr/bin/env python3
"""
Git platform factory for creating appropriate adapters

This module provides factory methods to create Git platform adapters
based on URL detection or explicit platform specification.
"""

import logging
from typing import Union, Optional

from core.git import GitPlatformAdapter
from core.git.github import GitHubAdapter
from core.git.gitlab import GitLabAdapter
from core.git.utils import PlatformDetector, GitUrlParser

logger = logging.getLogger(__name__)


class GitFactory:
    """Factory class for creating Git platform adapters"""
    
    @staticmethod
    def create_adapter(url: str, user_id: Optional[str] = None) -> GitPlatformAdapter:
        """Create appropriate adapter based on URL detection

        Args:
            url: Repository URL to analyze
            user_id: Optional user ID for user-specific configuration lookup

        Returns:
            GitPlatformAdapter: Appropriate platform adapter

        Raises:
            ValueError: If platform cannot be detected or is unsupported
        """
        try:
            platform = PlatformDetector.detect_platform(url)
            logger.info(f"Detected platform '{platform}' for URL: {url}")

            return GitFactory.create_adapter_by_platform(platform, user_id)

        except Exception as e:
            logger.error(f"Failed to create adapter for URL {url}: {str(e)}")
            raise ValueError(f"Failed to create Git adapter for URL: {url}") from e
    
    @staticmethod
    def create_adapter_by_platform(platform: str, user_id: Optional[str] = None) -> GitPlatformAdapter:
        """Create adapter for specific platform

        Args:
            platform: Platform name ('github' or 'gitlab')
            user_id: Optional user ID for user-specific configuration lookup

        Returns:
            GitPlatformAdapter: Platform-specific adapter

        Raises:
            ValueError: If platform is unsupported
        """
        platform = platform.lower().strip()

        if platform == "github":
            logger.info("Creating GitHub adapter")
            return GitHubAdapter(user_id=user_id)
        elif platform == "gitlab":
            logger.info("Creating GitLab adapter")
            return GitLabAdapter(user_id=user_id)
        else:
            supported_platforms = PlatformDetector.get_supported_platforms()
            raise ValueError(
                f"Unsupported platform: {platform}. "
                f"Supported platforms: {', '.join(supported_platforms)}"
            )
    
    @staticmethod
    def get_supported_platforms() -> list:
        """Get list of supported platforms
        
        Returns:
            list: List of supported platform names
        """
        return PlatformDetector.get_supported_platforms()
    
    @staticmethod
    def is_supported_platform(platform: str) -> bool:
        """Check if platform is supported
        
        Args:
            platform: Platform name to check
            
        Returns:
            bool: True if platform is supported
        """
        return PlatformDetector.is_supported_platform(platform)
    
    @staticmethod
    def is_supported_url(url: str) -> bool:
        """Check if URL is from a supported platform
        
        Args:
            url: Repository URL to check
            
        Returns:
            bool: True if URL is from a supported platform
        """
        try:
            PlatformDetector.detect_platform(url)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_url_and_create_adapter(url: str) -> tuple:
        """Validate URL and create adapter with detailed result
        
        Args:
            url: Repository URL to validate and process
            
        Returns:
            tuple: (success: bool, adapter: GitPlatformAdapter or None, error: str or None)
        """
        try:
            # Normalize URL first
            normalized_url = GitUrlParser.normalize_git_url(url)
            
            # Detect platform
            platform = PlatformDetector.detect_platform(normalized_url)
            
            # Create adapter
            adapter = GitFactory.create_adapter_by_platform(platform)
            
            # Validate that adapter can parse the URL
            try:
                repo_path = adapter.parse_git_url(normalized_url)
                logger.info(f"Successfully validated URL {url} -> {repo_path} on {platform}")
                return True, adapter, None
            except Exception as parse_error:
                error_msg = f"URL parsing failed: {str(parse_error)}"
                logger.error(error_msg)
                return False, None, error_msg
                
        except Exception as e:
            error_msg = f"URL validation failed: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg


class GitAdapterManager:
    """Manager class for Git adapters with caching and configuration"""
    
    def __init__(self):
        """Initialize adapter manager"""
        self._adapter_cache = {}
        
    def get_adapter(self, platform: str, use_cache: bool = True) -> GitPlatformAdapter:
        """Get adapter for platform with optional caching
        
        Args:
            platform: Platform name
            use_cache: Whether to use cached adapter
            
        Returns:
            GitPlatformAdapter: Platform adapter
        """
        if use_cache and platform in self._adapter_cache:
            logger.debug(f"Using cached adapter for platform: {platform}")
            return self._adapter_cache[platform]
        
        adapter = GitFactory.create_adapter_by_platform(platform)
        
        if use_cache:
            self._adapter_cache[platform] = adapter
            logger.debug(f"Cached adapter for platform: {platform}")
        
        return adapter
    
    def get_adapter_for_url(self, url: str, use_cache: bool = True) -> GitPlatformAdapter:
        """Get adapter for URL with optional caching
        
        Args:
            url: Repository URL
            use_cache: Whether to use cached adapter
            
        Returns:
            GitPlatformAdapter: Appropriate adapter
        """
        platform = PlatformDetector.detect_platform(url)
        return self.get_adapter(platform, use_cache)
    
    def clear_cache(self):
        """Clear adapter cache"""
        self._adapter_cache.clear()
        logger.info("Cleared adapter cache")
    
    def get_cache_info(self) -> dict:
        """Get cache information
        
        Returns:
            dict: Cache status information
        """
        return {
            'cached_platforms': list(self._adapter_cache.keys()),
            'cache_size': len(self._adapter_cache)
        }


# Global adapter manager instance
adapter_manager = GitAdapterManager()


__all__ = [
    "GitFactory",
    "GitAdapterManager",
    "adapter_manager"
]
