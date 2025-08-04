#!/usr/bin/env python3
"""
Platform configuration service for managing user-specific Git platform settings
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, text
from sqlalchemy.exc import IntegrityError

from core.models.platform_config import UserPlatformConfig
from core.database.router import DatabaseRouter

logger = logging.getLogger(__name__)


class PlatformConfigService:
    """Service for managing user platform configurations"""
    
    def __init__(self, settings):
        """Initialize service with settings"""
        self.settings = settings
        self.db_router = DatabaseRouter(settings)
    
    def get_user_configs(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all platform configurations for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of platform configurations
        """
        try:
            session = self.db_router.get_users_session()
            configs = session.query(UserPlatformConfig).filter(
                UserPlatformConfig.user_id == user_id
            ).order_by(UserPlatformConfig.platform, UserPlatformConfig.name).all()

            return [config.to_dict() for config in configs]
                
        except Exception as e:
            logger.error(f"Error getting user configs: {str(e)}")
            return []
    
    def save_user_configs(self, user_id: str, configs: List[Dict[str, Any]]) -> bool:
        """Save platform configurations for a user
        
        Args:
            user_id: User identifier
            configs: List of platform configurations
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = self.db_router.get_users_session()

            # Delete existing configs for this user
            session.query(UserPlatformConfig).filter(
                UserPlatformConfig.user_id == user_id
            ).delete()

            # Add new configs
            for config_data in configs:
                config = UserPlatformConfig.from_dict(config_data)
                config.user_id = user_id
                session.add(config)

            # Ensure only one default per platform per user
            self._ensure_single_default_per_platform(session, user_id)

            # Commit and flush to ensure data is written
            session.commit()
            session.flush()

            logger.info(f"Saved {len(configs)} platform configurations for user {user_id}")
            return True
                
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving user configs: {str(e)}")
            return False

    def save_single_user_config(self, user_id: str, config_data: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
        """Save a single platform configuration for a user

        Args:
            user_id: User identifier
            config_data: Platform configuration data

        Returns:
            Tuple of (success, error_message, error_type)
            - success: True if successful, False otherwise
            - error_message: Human-readable error message if failed
            - error_type: Error type ('duplicate_name', 'duplicate_base_url', 'other')
        """
        try:
            session = self.db_router.get_users_session()

            # Create new config
            config = UserPlatformConfig.from_dict(config_data)
            config.user_id = user_id
            session.add(config)

            # Ensure only one default per platform per user
            self._ensure_single_default_per_platform(session, user_id)

            # Commit and flush to ensure data is written
            session.commit()
            session.flush()

            logger.info(f"Saved single platform configuration for user {user_id}: {config_data['platform']} - {config_data['name']}")
            return True, None, None

        except IntegrityError as e:
            session.rollback()
            error_str = str(e)

            # Parse the error to determine if it's a name or base_url duplicate
            if 'uq_user_platform_name' in error_str or 'name' in error_str.lower():
                error_msg = f"Configuration name '{config_data.get('name', '')}' already exists"
                error_type = 'duplicate_name'
            elif 'uq_user_platform_base_url' in error_str or 'base_url' in error_str.lower():
                error_msg = f"Base URL '{config_data.get('base_url', '')}' already exists"
                error_type = 'duplicate_base_url'
            else:
                error_msg = "A configuration with these details already exists"
                error_type = 'duplicate_other'

            logger.warning(f"Duplicate configuration for user {user_id}: {error_msg}")
            return False, error_msg, error_type

        except Exception as e:
            session.rollback()
            logger.error(f"Error saving single user config: {str(e)}")
            return False, "Failed to save configuration", "other"

    def update_user_config(self, user_id: str, config_id: int, config_data: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
        """Update a specific user platform configuration

        Args:
            user_id: User identifier
            config_id: Configuration ID to update
            config_data: Configuration data to update

        Returns:
            Tuple of (success, error_message, error_type)
            - success: True if successful, False otherwise
            - error_message: Human-readable error message if failed
            - error_type: Error type ('duplicate_name', 'duplicate_base_url', 'not_found', 'other')
        """
        try:
            session = self.db_router.get_users_session()

            # Find the existing configuration
            existing_config = session.query(UserPlatformConfig).filter(
                and_(
                    UserPlatformConfig.id == config_id,
                    UserPlatformConfig.user_id == user_id
                )
            ).first()

            if not existing_config:
                return False, "Configuration not found", "not_found"

            # Check for duplicates (excluding the current config)
            # Check for duplicate name
            duplicate_name = session.query(UserPlatformConfig).filter(
                and_(
                    UserPlatformConfig.user_id == user_id,
                    UserPlatformConfig.name == config_data.get('name'),
                    UserPlatformConfig.id != config_id
                )
            ).first()

            if duplicate_name:
                return False, f"Configuration name '{config_data.get('name', '')}' already exists", "duplicate_name"

            # Check for duplicate base URL
            duplicate_url = session.query(UserPlatformConfig).filter(
                and_(
                    UserPlatformConfig.user_id == user_id,
                    UserPlatformConfig.base_url == config_data.get('base_url'),
                    UserPlatformConfig.id != config_id
                )
            ).first()

            if duplicate_url:
                return False, f"Base URL '{config_data.get('base_url', '')}' already exists", "duplicate_base_url"

            # Update the configuration
            existing_config.name = config_data.get('name', existing_config.name)
            existing_config.platform = config_data.get('platform', existing_config.platform)
            existing_config.base_url = config_data.get('base_url', existing_config.base_url)
            existing_config.token = config_data.get('token', existing_config.token)
            existing_config.is_default = config_data.get('is_default', existing_config.is_default)
            existing_config.updated_at = datetime.utcnow()

            # Ensure only one default per platform per user
            self._ensure_single_default_per_platform(session, user_id)

            # Commit and flush to ensure data is written
            session.commit()
            session.flush()

            logger.info(f"Updated platform configuration {config_id} for user {user_id}: {config_data['platform']} - {config_data['name']}")
            return True, None, None

        except Exception as e:
            session.rollback()
            logger.error(f"Error updating user config: {str(e)}")
            return False, "Failed to update configuration", "other"

    def get_user_config_for_platform(self, user_id: str, platform: str, base_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get platform configuration for a specific platform and URL
        
        Args:
            user_id: User identifier
            platform: Platform name ('github' or 'gitlab')
            base_url: Optional base URL to match
            
        Returns:
            Platform configuration or None
        """
        try:
            session = self.db_router.get_users_session()
            query = session.query(UserPlatformConfig).filter(
                and_(
                    UserPlatformConfig.user_id == user_id,
                    UserPlatformConfig.platform == platform
                )
            )

            if base_url:
                # Try to find exact match first
                config = query.filter(UserPlatformConfig.base_url == base_url).first()
                if config:
                    return config.to_dict()

            # Fall back to default for this platform
            config = query.filter(UserPlatformConfig.is_default == True).first()
            if config:
                return config.to_dict()

            # If no default, get any config for this platform
            config = query.first()
            if config:
                return config.to_dict()

            return None
                
        except Exception as e:
            logger.error(f"Error getting user config for platform: {str(e)}")
            return None
    
    def delete_user_config(self, user_id: str, config_id: int) -> bool:
        """Delete a specific platform configuration
        
        Args:
            user_id: User identifier
            config_id: Configuration ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = self.db_router.get_users_session()
            config = session.query(UserPlatformConfig).filter(
                and_(
                    UserPlatformConfig.id == config_id,
                    UserPlatformConfig.user_id == user_id
                )
            ).first()

            if config:
                session.delete(config)
                session.commit()
                logger.info(f"Deleted platform configuration {config_id} for user {user_id}")
                return True
            else:
                logger.warning(f"Platform configuration {config_id} not found for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting user config: {str(e)}")
            return False
    
    def _ensure_single_default_per_platform(self, session: Session, user_id: str):
        """Ensure only one default configuration per platform per user"""
        platforms = ['github', 'gitlab']
        
        for platform in platforms:
            defaults = session.query(UserPlatformConfig).filter(
                and_(
                    UserPlatformConfig.user_id == user_id,
                    UserPlatformConfig.platform == platform,
                    UserPlatformConfig.is_default == True
                )
            ).all()
            
            if len(defaults) > 1:
                # Keep the first one as default, remove default flag from others
                for config in defaults[1:]:
                    config.is_default = False
                logger.info(f"Fixed multiple defaults for platform {platform} for user {user_id}")
    
    def create_table_if_not_exists(self):
        """Create the user_platform_configs table if it doesn't exist"""
        try:
            from core.models.platform_config import CREATE_TABLE_SQL
            session = self.db_router.get_users_session()
            session.execute(text(CREATE_TABLE_SQL))
            session.commit()
            logger.info("Created user_platform_configs table")
        except Exception as e:
            logger.error(f"Error creating table: {str(e)}")
            raise
