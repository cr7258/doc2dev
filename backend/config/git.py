#!/usr/bin/env python3
"""
Git platform configuration management

This module provides configuration management for different Git platforms
including validation, environment variable handling, and platform-specific settings.
"""

import os
import logging
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field, validator
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class GitPlatformConfig(BaseModel):
    """Configuration for a specific Git platform"""
    
    name: str = Field(..., description="Platform name (github, gitlab)")
    token: str = Field(default="", description="Authentication token")
    base_url: str = Field(..., description="Base URL for the platform")
    api_url: str = Field(default="", description="API URL (auto-generated if empty)")
    enabled: bool = Field(default=True, description="Whether platform is enabled")
    
    @validator('api_url', always=True)
    def generate_api_url(cls, v, values):
        """Auto-generate API URL if not provided"""
        if v:  # If API URL is explicitly provided, use it
            return v
            
        name = values.get('name', '').lower()
        base_url = values.get('base_url', '')
        
        if not base_url:
            return ""
            
        if name == 'github':
            if base_url == 'https://github.com':
                return 'https://api.github.com'
            else:
                # GitHub Enterprise Server
                return f"{base_url}/api/v3"
        elif name == 'gitlab':
            return f"{base_url}/api/v4"
        else:
            return ""
    
    @validator('base_url')
    def validate_base_url(cls, v):
        """Validate base URL format"""
        if not v:
            raise ValueError("Base URL cannot be empty")
        
        if not v.startswith(('http://', 'https://')):
            raise ValueError("Base URL must start with http:// or https://")
        
        try:
            parsed = urlparse(v)
            if not parsed.netloc:
                raise ValueError("Invalid URL format")
        except Exception as e:
            raise ValueError(f"Invalid URL format: {e}")
        
        return v.rstrip('/')  # Remove trailing slash
    
    def is_configured(self) -> bool:
        """Check if platform is properly configured"""
        return bool(self.token and self.base_url and self.enabled)
    
    def get_domain(self) -> str:
        """Get domain from base URL"""
        try:
            parsed = urlparse(self.base_url)
            return parsed.netloc
        except Exception:
            return ""
    
    def is_default_instance(self) -> bool:
        """Check if this is the default public instance"""
        if self.name == 'github':
            return self.base_url == 'https://github.com'
        elif self.name == 'gitlab':
            return self.base_url == 'https://gitlab.com'
        return False


class GitPlatformConfigManager:
    """Manager for Git platform configurations"""
    
    def __init__(self, settings=None):
        """Initialize configuration manager
        
        Args:
            settings: Optional Settings object, will load from environment if None
        """
        self.settings = settings
        self._platforms = {}
        self._load_configurations()
    
    def _load_configurations(self):
        """Load platform configurations from environment or settings"""
        # GitHub configuration
        github_token = self._get_env_or_setting('GITHUB_TOKEN', 'github_token', '')
        github_url = self._get_env_or_setting('GITHUB_URL', 'github_url', 'https://github.com')
        
        self._platforms['github'] = GitPlatformConfig(
            name='github',
            token=github_token,
            base_url=github_url,
            enabled=bool(github_token)  # Enable only if token is provided
        )
        
        # GitLab configuration
        gitlab_token = self._get_env_or_setting('GITLAB_TOKEN', 'gitlab_token', '')
        gitlab_url = self._get_env_or_setting('GITLAB_URL', 'gitlab_url', 'https://gitlab.com')
        
        self._platforms['gitlab'] = GitPlatformConfig(
            name='gitlab',
            token=gitlab_token,
            base_url=gitlab_url,
            enabled=bool(gitlab_token)  # Enable only if token is provided
        )
        
        logger.info(f"Loaded configurations for platforms: {list(self._platforms.keys())}")
    
    def _get_env_or_setting(self, env_var: str, setting_attr: str, default: str) -> str:
        """Get value from environment variable or settings object"""
        # First try environment variable
        value = os.getenv(env_var)
        if value:
            return value
        
        # Then try settings object
        if self.settings and hasattr(self.settings, setting_attr):
            value = getattr(self.settings, setting_attr)
            if value:
                return value
        
        # Return default
        return default
    
    def get_platform_config(self, platform: str) -> Optional[GitPlatformConfig]:
        """Get configuration for specific platform
        
        Args:
            platform: Platform name ('github' or 'gitlab')
            
        Returns:
            GitPlatformConfig or None if platform not found
        """
        return self._platforms.get(platform.lower())
    
    def get_enabled_platforms(self) -> List[str]:
        """Get list of enabled platform names
        
        Returns:
            List of enabled platform names
        """
        return [
            name for name, config in self._platforms.items()
            if config.enabled and config.is_configured()
        ]
    
    def get_all_platforms(self) -> Dict[str, GitPlatformConfig]:
        """Get all platform configurations
        
        Returns:
            Dictionary of platform configurations
        """
        return self._platforms.copy()
    
    def is_platform_enabled(self, platform: str) -> bool:
        """Check if platform is enabled and configured
        
        Args:
            platform: Platform name
            
        Returns:
            True if platform is enabled and configured
        """
        config = self.get_platform_config(platform)
        return config is not None and config.enabled and config.is_configured()
    
    def validate_platform_config(self, platform: str) -> Tuple[bool, List[str]]:
        """Validate platform configuration
        
        Args:
            platform: Platform name to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        config = self.get_platform_config(platform)
        if not config:
            return False, [f"Platform '{platform}' not found"]
        
        issues = []
        
        if not config.token:
            env_var = f"{platform.upper()}_TOKEN"
            issues.append(f"Missing {env_var} environment variable")
        
        if not config.base_url:
            env_var = f"{platform.upper()}_URL"
            issues.append(f"Invalid {env_var} environment variable")
        
        if not config.api_url:
            issues.append(f"Could not generate API URL for {platform}")
        
        return len(issues) == 0, issues
    
    def validate_all_platforms(self) -> Dict[str, Tuple[bool, List[str]]]:
        """Validate all platform configurations
        
        Returns:
            Dictionary mapping platform names to validation results
        """
        results = {}
        for platform in self._platforms.keys():
            results[platform] = self.validate_platform_config(platform)
        return results
    
    def get_configuration_summary(self) -> Dict[str, Dict]:
        """Get summary of all platform configurations
        
        Returns:
            Dictionary with configuration summary
        """
        summary = {}
        for name, config in self._platforms.items():
            summary[name] = {
                'enabled': config.enabled,
                'configured': config.is_configured(),
                'base_url': config.base_url,
                'api_url': config.api_url,
                'has_token': bool(config.token),
                'is_default_instance': config.is_default_instance(),
                'domain': config.get_domain()
            }
        return summary
    
    def reload_configurations(self):
        """Reload configurations from environment/settings"""
        self._platforms.clear()
        self._load_configurations()
        logger.info("Reloaded Git platform configurations")


# Global configuration manager instance
_config_manager = None


def get_git_config_manager(settings=None) -> GitPlatformConfigManager:
    """Get global Git configuration manager instance
    
    Args:
        settings: Optional Settings object
        
    Returns:
        GitPlatformConfigManager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = GitPlatformConfigManager(settings)
    return _config_manager


def reload_git_config(settings=None):
    """Reload global Git configuration
    
    Args:
        settings: Optional Settings object
    """
    global _config_manager
    _config_manager = GitPlatformConfigManager(settings)


__all__ = [
    "GitPlatformConfig",
    "GitPlatformConfigManager",
    "get_git_config_manager",
    "reload_git_config"
]
