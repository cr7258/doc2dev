#!/usr/bin/env python3
"""
Git platform utility functions

This module provides utility functions for Git platform operations including
URL parsing, platform detection, and common Git operations.
"""

import os
import re
from typing import Optional
from urllib.parse import urlparse


class GitUrlParser:
    """Git URL parsing utilities"""
    
    @staticmethod
    def is_github_url(url: str) -> bool:
        """Check if URL is a GitHub URL
        
        Args:
            url: Repository URL to check
            
        Returns:
            bool: True if URL is from GitHub (including custom domains)
        """
        github_domains = [
            'github.com',
            # Support custom GitHub Enterprise domains
            GitUrlParser._extract_domain_from_env('GITHUB_URL')
        ]
        
        # Filter out None/empty domains
        github_domains = [domain for domain in github_domains if domain]
        
        return any(domain in url.lower() for domain in github_domains)
    
    @staticmethod
    def is_gitlab_url(url: str) -> bool:
        """Check if URL is a GitLab URL
        
        Args:
            url: Repository URL to check
            
        Returns:
            bool: True if URL is from GitLab (including self-hosted)
        """
        gitlab_domains = [
            'gitlab.com',
            # Support self-hosted GitLab domains
            GitUrlParser._extract_domain_from_env('GITLAB_URL')
        ]
        
        # Filter out None/empty domains
        gitlab_domains = [domain for domain in gitlab_domains if domain]
        
        return any(domain in url.lower() for domain in gitlab_domains)
    
    @staticmethod
    def _extract_domain_from_env(env_var: str) -> Optional[str]:
        """Extract domain from environment variable URL
        
        Args:
            env_var: Environment variable name containing URL
            
        Returns:
            Optional[str]: Extracted domain or None
        """
        env_url = os.getenv(env_var, '')
        if not env_url:
            return None
            
        try:
            parsed = urlparse(env_url)
            return parsed.netloc.lower()
        except Exception:
            return None
    
    @staticmethod
    def normalize_git_url(url: str) -> str:
        """Normalize Git URL to standard format

        Args:
            url: Git repository URL

        Returns:
            str: Normalized URL
        """
        # Remove .git suffix if present
        if url.endswith('.git'):
            url = url[:-4]

        # Handle SSH URLs (git@domain:owner/repo)
        if url.startswith('git@'):
            # Convert SSH URL to HTTPS
            # git@github.com:owner/repo -> https://github.com/owner/repo
            ssh_pattern = r'git@([^:]+):(.+)'
            import re
            match = re.match(ssh_pattern, url)
            if match:
                domain, path = match.groups()
                url = f'https://{domain}/{path}'

        # Ensure https:// prefix for other cases
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        return url
    
    @staticmethod
    def extract_repo_path(url: str) -> str:
        """Extract repository path (owner/repo) from URL
        
        Args:
            url: Git repository URL
            
        Returns:
            str: Repository path in owner/repo format
        """
        # Normalize URL first
        url = GitUrlParser.normalize_git_url(url)
        
        try:
            parsed = urlparse(url)
            path = parsed.path.strip('/')
            
            # Remove .git suffix if present
            if path.endswith('.git'):
                path = path[:-4]
            
            # Validate path format (should be owner/repo)
            parts = path.split('/')
            if len(parts) >= 2:
                return '/'.join(parts[:2])  # Take only owner/repo part
            else:
                raise ValueError(f"Invalid repository path: {path}")
                
        except Exception as e:
            raise ValueError(f"Failed to parse repository URL: {url}") from e


class PlatformDetector:
    """Git platform detection utilities"""
    
    @staticmethod
    def detect_platform(url: str) -> str:
        """Automatically detect Git platform type from URL
        
        Args:
            url: Repository URL
            
        Returns:
            str: Platform name ('github' or 'gitlab')
            
        Raises:
            ValueError: If platform cannot be detected
        """
        if GitUrlParser.is_github_url(url):
            return "github"
        elif GitUrlParser.is_gitlab_url(url):
            return "gitlab"
        else:
            raise ValueError(f"Unsupported platform URL: {url}")
    
    @staticmethod
    def get_supported_platforms() -> list:
        """Get list of supported platforms
        
        Returns:
            list: List of supported platform names
        """
        return ["github", "gitlab"]
    
    @staticmethod
    def is_supported_platform(platform: str) -> bool:
        """Check if platform is supported
        
        Args:
            platform: Platform name to check
            
        Returns:
            bool: True if platform is supported
        """
        return platform.lower() in PlatformDetector.get_supported_platforms()


class GitConfigHelper:
    """Git configuration helper utilities"""
    
    @staticmethod
    def get_platform_config(platform: str) -> dict:
        """Get configuration for specific platform
        
        Args:
            platform: Platform name ('github' or 'gitlab')
            
        Returns:
            dict: Platform configuration
        """
        if platform.lower() == 'github':
            return {
                'token_env': 'GITHUB_TOKEN',
                'url_env': 'GITHUB_URL',
                'default_url': 'https://github.com',
                'api_path': '/api/v3'  # For GitHub Enterprise
            }
        elif platform.lower() == 'gitlab':
            return {
                'token_env': 'GITLAB_TOKEN',
                'url_env': 'GITLAB_URL',
                'default_url': 'https://gitlab.com',
                'api_path': '/api/v4'
            }
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    @staticmethod
    def validate_platform_config(platform: str) -> dict:
        """Validate platform configuration
        
        Args:
            platform: Platform name to validate
            
        Returns:
            dict: Validation result with status and messages
        """
        try:
            config = GitConfigHelper.get_platform_config(platform)
            token = os.getenv(config['token_env'])
            url = os.getenv(config['url_env'], config['default_url'])
            
            issues = []
            if not token:
                issues.append(f"Missing {config['token_env']} environment variable")
            
            if not url:
                issues.append(f"Invalid {config['url_env']} environment variable")
            
            return {
                'valid': len(issues) == 0,
                'issues': issues,
                'config': {
                    'token_configured': bool(token),
                    'url': url
                }
            }
            
        except Exception as e:
            return {
                'valid': False,
                'issues': [f"Configuration error: {str(e)}"],
                'config': {}
            }


__all__ = [
    "GitUrlParser",
    "PlatformDetector",
    "GitConfigHelper"
]
