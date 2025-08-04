#!/usr/bin/env python3
"""
Git platform configuration validator and diagnostic tool

This module provides validation and diagnostic capabilities for Git platform configurations.
"""

import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from config.git import get_git_config_manager, GitPlatformConfig
from .utils import PlatformDetector

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of configuration validation"""
    platform: str
    is_valid: bool
    issues: List[str]
    warnings: List[str]
    config_summary: Dict


class GitConfigValidator:
    """Validator for Git platform configurations"""
    
    def __init__(self):
        """Initialize validator"""
        self.config_manager = get_git_config_manager()
    
    def validate_platform(self, platform: str) -> ValidationResult:
        """Validate specific platform configuration
        
        Args:
            platform: Platform name to validate
            
        Returns:
            ValidationResult with validation details
        """
        config = self.config_manager.get_platform_config(platform)
        issues = []
        warnings = []
        
        if not config:
            return ValidationResult(
                platform=platform,
                is_valid=False,
                issues=[f"Platform '{platform}' configuration not found"],
                warnings=[],
                config_summary={}
            )
        
        # Check token
        if not config.token:
            env_var = f"{platform.upper()}_TOKEN"
            issues.append(f"Missing {env_var} environment variable")
        elif len(config.token) < 10:
            warnings.append(f"Token for {platform} seems too short (possible invalid token)")
        
        # Check URLs
        if not config.base_url:
            issues.append(f"Missing base URL for {platform}")
        elif not config.base_url.startswith(('http://', 'https://')):
            issues.append(f"Invalid base URL format for {platform}: {config.base_url}")
        
        if not config.api_url:
            issues.append(f"Could not generate API URL for {platform}")
        
        # Check if platform is supported
        if not PlatformDetector.is_supported_platform(platform):
            issues.append(f"Platform '{platform}' is not supported")
        
        # Platform-specific validations
        if platform == 'github':
            self._validate_github_config(config, issues, warnings)
        elif platform == 'gitlab':
            self._validate_gitlab_config(config, issues, warnings)
        
        # Generate config summary
        config_summary = {
            'enabled': config.enabled,
            'configured': config.is_configured(),
            'base_url': config.base_url,
            'api_url': config.api_url,
            'has_token': bool(config.token),
            'token_length': len(config.token) if config.token else 0,
            'is_default_instance': config.is_default_instance(),
            'domain': config.get_domain()
        }
        
        return ValidationResult(
            platform=platform,
            is_valid=len(issues) == 0,
            issues=issues,
            warnings=warnings,
            config_summary=config_summary
        )
    
    def _validate_github_config(self, config: GitPlatformConfig, issues: List[str], warnings: List[str]):
        """Validate GitHub-specific configuration"""
        # Check if it's GitHub Enterprise vs public GitHub
        if config.base_url != 'https://github.com':
            # GitHub Enterprise Server
            if not config.base_url.endswith('/api/v3') and '/api/v3' not in config.api_url:
                warnings.append("GitHub Enterprise Server detected - ensure API endpoint is correct")
        
        # Check token format (GitHub tokens usually start with specific prefixes)
        if config.token:
            if not any(config.token.startswith(prefix) for prefix in ['ghp_', 'gho_', 'ghu_', 'ghs_', 'ghr_']):
                warnings.append("GitHub token format may be invalid (should start with ghp_, gho_, etc.)")
    
    def _validate_gitlab_config(self, config: GitPlatformConfig, issues: List[str], warnings: List[str]):
        """Validate GitLab-specific configuration"""
        # Check if it's self-hosted GitLab vs GitLab.com
        if config.base_url != 'https://gitlab.com':
            warnings.append("Self-hosted GitLab detected - ensure API endpoint is accessible")
        
        # GitLab tokens are typically longer
        if config.token and len(config.token) < 20:
            warnings.append("GitLab token seems short - ensure it's a valid personal access token")
    
    def validate_all_platforms(self) -> Dict[str, ValidationResult]:
        """Validate all configured platforms
        
        Returns:
            Dictionary mapping platform names to validation results
        """
        results = {}
        all_configs = self.config_manager.get_all_platforms()
        
        for platform_name in all_configs.keys():
            results[platform_name] = self.validate_platform(platform_name)
        
        return results
    
    def get_validation_summary(self) -> Dict:
        """Get overall validation summary
        
        Returns:
            Summary of validation results for all platforms
        """
        results = self.validate_all_platforms()
        
        summary = {
            'total_platforms': len(results),
            'valid_platforms': sum(1 for r in results.values() if r.is_valid),
            'enabled_platforms': [],
            'disabled_platforms': [],
            'platforms_with_issues': [],
            'platforms_with_warnings': []
        }
        
        for platform, result in results.items():
            if result.config_summary.get('enabled', False):
                summary['enabled_platforms'].append(platform)
            else:
                summary['disabled_platforms'].append(platform)
            
            if result.issues:
                summary['platforms_with_issues'].append({
                    'platform': platform,
                    'issues': result.issues
                })
            
            if result.warnings:
                summary['platforms_with_warnings'].append({
                    'platform': platform,
                    'warnings': result.warnings
                })
        
        return summary
    
    def diagnose_url_support(self, url: str) -> Dict:
        """Diagnose URL support and configuration
        
        Args:
            url: Repository URL to diagnose
            
        Returns:
            Diagnostic information about URL support
        """
        try:
            platform = PlatformDetector.detect_platform(url)
            config = self.config_manager.get_platform_config(platform)
            validation = self.validate_platform(platform)
            
            return {
                'url': url,
                'detected_platform': platform,
                'platform_supported': True,
                'platform_configured': config.is_configured() if config else False,
                'platform_enabled': config.enabled if config else False,
                'validation_result': validation,
                'can_process': validation.is_valid and config.enabled if config else False
            }
        except ValueError as e:
            return {
                'url': url,
                'detected_platform': None,
                'platform_supported': False,
                'platform_configured': False,
                'platform_enabled': False,
                'error': str(e),
                'can_process': False
            }
    
    def get_configuration_recommendations(self) -> List[str]:
        """Get configuration recommendations
        
        Returns:
            List of configuration recommendations
        """
        recommendations = []
        results = self.validate_all_platforms()
        
        for platform, result in results.items():
            if not result.is_valid:
                if not result.config_summary.get('has_token', False):
                    env_var = f"{platform.upper()}_TOKEN"
                    recommendations.append(
                        f"Set {env_var} environment variable to enable {platform} support"
                    )
                
                for issue in result.issues:
                    recommendations.append(f"Fix {platform} issue: {issue}")
        
        # Check if no platforms are enabled
        enabled_platforms = [p for p, r in results.items() if r.config_summary.get('enabled', False)]
        if not enabled_platforms:
            recommendations.append(
                "No Git platforms are enabled. Set GITHUB_TOKEN or GITLAB_TOKEN to enable repository access"
            )
        
        return recommendations


def validate_git_configuration() -> Dict:
    """Convenience function to validate Git configuration
    
    Returns:
        Complete validation report
    """
    validator = GitConfigValidator()
    return {
        'validation_results': validator.validate_all_platforms(),
        'summary': validator.get_validation_summary(),
        'recommendations': validator.get_configuration_recommendations()
    }


__all__ = [
    "ValidationResult",
    "GitConfigValidator",
    "validate_git_configuration"
]
