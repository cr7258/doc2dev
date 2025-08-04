#!/usr/bin/env python3
"""
Settings API routes for platform configuration management
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from api.auth import get_current_user_optional
from core.services.platform_config import PlatformConfigService

logger = logging.getLogger(__name__)

# Services will be initialized when needed to avoid circular imports
platform_config_service = None

def get_platform_config_service():
    """Get platform config service instance"""
    global platform_config_service
    if platform_config_service is None:
        # Import here to avoid circular imports
        from main import settings
        platform_config_service = PlatformConfigService(settings)
    return platform_config_service

# Create router
router = APIRouter(prefix="/settings", tags=["settings"])


class PlatformConfigRequest(BaseModel):
    """Platform configuration request model"""
    name: str = Field(..., description="User-friendly name for the configuration")
    platform: str = Field(..., description="Platform type: 'github' or 'gitlab'")
    base_url: str = Field(..., description="Base URL of the platform instance")
    token: str = Field(..., description="Access token for the platform")
    is_default: bool = Field(default=False, description="Whether this is the default configuration for the platform")


class PlatformConfigsRequest(BaseModel):
    """Request model for saving multiple platform configurations"""
    platforms: List[PlatformConfigRequest] = Field(..., description="List of platform configurations")


class PlatformConfigResponse(BaseModel):
    """Platform configuration response model"""
    id: str
    name: str
    platform: str
    base_url: str
    token: str  # This will be masked in the actual response
    is_default: bool
    created_at: str
    updated_at: str


class PlatformConfigsResponse(BaseModel):
    """Response model for platform configurations"""
    status: str = "success"
    platforms: List[PlatformConfigResponse]


@router.get("/platforms", response_model=PlatformConfigsResponse)
async def get_platform_configurations(
    current_user_id: Optional[str] = Depends(get_current_user_optional)
):
    """Get all platform configurations for the current user"""
    try:
        # Initialize service on first use
        initialize_platform_config_service()
        if not current_user_id:
            # Return empty list for unauthenticated users
            return PlatformConfigsResponse(platforms=[])

        logger.info(f"Getting platform configurations for user: {current_user_id}")
        configs = get_platform_config_service().get_user_configs(current_user_id)
        logger.info(f"Found {len(configs)} configurations for user {current_user_id}")
        
        return PlatformConfigsResponse(platforms=configs)
        
    except Exception as e:
        logger.error(f"Error getting platform configurations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get platform configurations")


@router.post("/platform", response_model=PlatformConfigResponse)
async def save_platform_configuration(
    request: PlatformConfigRequest,
    current_user_id: Optional[str] = Depends(get_current_user_optional)
):
    """Save a single platform configuration for the current user"""
    try:
        # Initialize service on first use
        initialize_platform_config_service()
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")

        # Convert Pydantic model to dictionary
        config_dict = {
            'name': request.name,
            'platform': request.platform,
            'base_url': request.base_url,
            'token': request.token,
            'is_default': request.is_default
        }

        # Validate platform
        if config_dict['platform'] not in ['github', 'gitlab']:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform: {config_dict['platform']}. Must be 'github' or 'gitlab'"
            )

        # Validate base URL
        if not config_dict['base_url'].startswith(('http://', 'https://')):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid base URL: {config_dict['base_url']}. Must start with http:// or https://"
            )

        # Save single configuration
        success, error_message, error_type = get_platform_config_service().save_single_user_config(current_user_id, config_dict)

        if not success:
            if error_type in ['duplicate_name', 'duplicate_base_url', 'duplicate_other']:
                raise HTTPException(status_code=409, detail=error_message)
            else:
                raise HTTPException(status_code=500, detail=error_message or "Failed to save platform configuration")

        # Return the saved configuration
        # Get the most recently saved config for this user and platform
        configs = get_platform_config_service().get_user_configs(current_user_id)
        saved_config = None
        for config in configs:
            if (config['platform'] == config_dict['platform'] and
                config['name'] == config_dict['name'] and
                config['base_url'] == config_dict['base_url']):
                saved_config = config
                break

        if not saved_config:
            raise HTTPException(status_code=500, detail="Failed to retrieve saved configuration")

        return PlatformConfigResponse(**saved_config)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving platform configuration: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save platform configuration")


@router.post("/platforms", response_model=PlatformConfigsResponse)
async def save_platform_configurations(
    request: PlatformConfigsRequest,
    current_user_id: Optional[str] = Depends(get_current_user_optional)
):
    """Save platform configurations for the current user"""
    try:
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Convert request to dict format
        configs_data = []
        for config in request.platforms:
            configs_data.append({
                'name': config.name,
                'platform': config.platform,
                'base_url': config.base_url,
                'token': config.token,
                'is_default': config.is_default
            })
        
        # Validate platforms
        for config in configs_data:
            if config['platform'] not in ['github', 'gitlab']:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid platform: {config['platform']}. Must be 'github' or 'gitlab'"
                )
            
            if not config['base_url'].startswith(('http://', 'https://')):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid base URL: {config['base_url']}. Must start with http:// or https://"
                )
        
        # Save configurations
        success = get_platform_config_service().save_user_configs(current_user_id, configs_data)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to save platform configurations")

        # Return updated configurations
        updated_configs = get_platform_config_service().get_user_configs(current_user_id)
        
        return PlatformConfigsResponse(platforms=updated_configs)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving platform configurations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save platform configurations")


@router.put("/platforms/{config_id}", response_model=PlatformConfigResponse)
async def update_platform_configuration(
    config_id: int,
    request: PlatformConfigRequest,
    current_user_id: Optional[str] = Depends(get_current_user_optional)
):
    """Update a specific platform configuration"""
    try:
        # Initialize service on first use
        initialize_platform_config_service()
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")

        # Convert Pydantic model to dictionary
        config_dict = {
            'name': request.name,
            'platform': request.platform,
            'base_url': request.base_url,
            'token': request.token,
            'is_default': request.is_default
        }

        # Validate platform
        if config_dict['platform'] not in ['github', 'gitlab']:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform: {config_dict['platform']}. Must be 'github' or 'gitlab'"
            )

        if not config_dict['base_url'].startswith(('http://', 'https://')):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid base URL: {config_dict['base_url']}. Must start with http:// or https://"
            )

        # Update configuration
        success, error_message, error_type = get_platform_config_service().update_user_config(current_user_id, config_id, config_dict)

        if not success:
            if error_type in ['duplicate_name', 'duplicate_base_url', 'duplicate_other']:
                raise HTTPException(status_code=409, detail=error_message)
            elif error_type == 'not_found':
                raise HTTPException(status_code=404, detail=error_message)
            else:
                raise HTTPException(status_code=500, detail=error_message or "Failed to update platform configuration")

        # Return the updated configuration
        configs = get_platform_config_service().get_user_configs(current_user_id)
        updated_config = None
        for config in configs:
            if config['id'] == str(config_id):
                updated_config = config
                break

        if not updated_config:
            raise HTTPException(status_code=500, detail="Failed to retrieve updated configuration")

        return PlatformConfigResponse(**updated_config)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating platform configuration: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update platform configuration")


@router.delete("/platforms/{config_id}")
async def delete_platform_configuration(
    config_id: int,
    current_user_id: Optional[str] = Depends(get_current_user_optional)
):
    """Delete a specific platform configuration"""
    try:
        # Initialize service on first use
        initialize_platform_config_service()
        if not current_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")

        success = get_platform_config_service().delete_user_config(current_user_id, config_id)

        if not success:
            raise HTTPException(status_code=404, detail="Platform configuration not found")

        return {"status": "success", "message": "Platform configuration deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting platform configuration: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete platform configuration")


# Initialize database table when service is first used
def initialize_platform_config_service():
    """Initialize platform configuration service and create table if needed"""
    try:
        get_platform_config_service().create_table_if_not_exists()
        logger.info("Platform configuration service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize platform configuration service: {str(e)}")
        raise
