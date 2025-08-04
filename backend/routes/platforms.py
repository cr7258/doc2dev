#!/usr/bin/env python3
"""
Platform configuration and validation routes for Doc2Dev API
"""

import logging
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from core.models.api import (
    PlatformConfigRequest, 
    PlatformConfigResponse, 
    PlatformStatusResponse,
    UrlValidationRequest,
    UrlValidationResponse
)
from config.git import get_git_config_manager
from core.git.config_validator import GitConfigValidator
from core.factories.git import GitFactory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/platforms", tags=["platforms"])


@router.get("/status", response_model=PlatformStatusResponse)
async def get_platforms_status():
    """
    Get configuration status for all Git platforms
    
    Returns:
        PlatformStatusResponse: Status of all configured platforms
    """
    try:
        config_manager = get_git_config_manager()
        validator = GitConfigValidator()
        
        platforms = {}
        summary = {
            "total_platforms": 0,
            "configured_platforms": 0,
            "valid_platforms": 0
        }
        
        # Check each platform
        for platform_name in ['github', 'gitlab']:
            config = config_manager.get_platform_config(platform_name)
            validation = validator.validate_platform(platform_name)
            
            platform_response = PlatformConfigResponse(
                platform=platform_name,
                configured=config.is_configured() if config else False,
                valid=validation.is_valid,
                base_url=config.base_url if config else "",
                api_url=config.api_url if config else "",
                issues=validation.issues,
                warnings=validation.warnings
            )
            
            platforms[platform_name] = platform_response.dict()
            
            # Update summary
            summary["total_platforms"] += 1
            if platform_response.configured:
                summary["configured_platforms"] += 1
            if platform_response.valid:
                summary["valid_platforms"] += 1
        
        return PlatformStatusResponse(
            platforms=platforms,
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Error getting platforms status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting platforms status: {str(e)}")


@router.post("/validate", response_model=PlatformConfigResponse)
async def validate_platform_config(request: PlatformConfigRequest):
    """
    Validate platform configuration
    
    Args:
        request: Platform configuration to validate
        
    Returns:
        PlatformConfigResponse: Validation results
    """
    try:
        validator = GitConfigValidator()
        
        # Validate the platform
        validation = validator.validate_platform(request.platform)
        
        # Get current configuration
        config_manager = get_git_config_manager()
        config = config_manager.get_platform_config(request.platform)
        
        return PlatformConfigResponse(
            platform=request.platform,
            configured=config.is_configured() if config else False,
            valid=validation.is_valid,
            base_url=config.base_url if config else "",
            api_url=config.api_url if config else "",
            issues=validation.issues,
            warnings=validation.warnings
        )
        
    except Exception as e:
        logger.error(f"Error validating platform {request.platform}: {e}")
        raise HTTPException(
            status_code=400, 
            detail=f"Error validating platform {request.platform}: {str(e)}"
        )


@router.post("/validate-url", response_model=UrlValidationResponse)
async def validate_repository_url(request: UrlValidationRequest):
    """
    Validate and parse repository URL
    
    Args:
        request: URL validation request
        
    Returns:
        UrlValidationResponse: URL validation and parsing results
    """
    try:
        url = str(request.url)
        
        # Try to create adapter and parse URL
        try:
            adapter = GitFactory.create_adapter(url)
            
            # Parse URL components
            org, repo = adapter.extract_org_repo(url)
            normalized_url = adapter.parse_git_url(url)
            platform = adapter.get_git_name()
            
            return UrlValidationResponse(
                valid=True,
                platform=platform,
                org=org,
                repo=repo,
                normalized_url=f"{adapter.get_git_api_base_url().replace('/api/v4', '').replace('api.', '')}/{normalized_url}",
                issues=[]
            )
            
        except Exception as parse_error:
            return UrlValidationResponse(
                valid=False,
                platform=None,
                org=None,
                repo=None,
                normalized_url=None,
                issues=[f"URL parsing error: {str(parse_error)}"]
            )
            
    except Exception as e:
        logger.error(f"Error validating URL {request.url}: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Error validating URL: {str(e)}"
        )


@router.get("/config/{platform}", response_model=PlatformConfigResponse)
async def get_platform_config(platform: str):
    """
    Get configuration for a specific platform
    
    Args:
        platform: Platform name ('github' or 'gitlab')
        
    Returns:
        PlatformConfigResponse: Platform configuration status
    """
    try:
        if platform not in ['github', 'gitlab']:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
        
        config_manager = get_git_config_manager()
        validator = GitConfigValidator()
        
        config = config_manager.get_platform_config(platform)
        validation = validator.validate_platform(platform)
        
        return PlatformConfigResponse(
            platform=platform,
            configured=config.is_configured() if config else False,
            valid=validation.is_valid,
            base_url=config.base_url if config else "",
            api_url=config.api_url if config else "",
            issues=validation.issues,
            warnings=validation.warnings
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting config for platform {platform}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting platform configuration: {str(e)}"
        )
