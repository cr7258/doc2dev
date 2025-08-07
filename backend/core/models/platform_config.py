#!/usr/bin/env python3
"""
Platform configuration models for user-specific Git platform settings
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Dict, Any, Optional

Base = declarative_base()


class UserPlatformConfig(Base):
    """User-specific platform configuration model"""
    __tablename__ = "user_platform_configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)  # GitHub user ID or UUID
    name = Column(String(255), nullable=False)  # User-friendly name
    platform = Column(String(50), nullable=False)  # 'github' or 'gitlab'
    base_url = Column(String(500), nullable=False)  # Base URL of the platform
    token = Column(Text, nullable=False)  # Encrypted access token
    is_default = Column(Boolean, default=False, nullable=False)  # Default config for this platform
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Add unique constraints for user-level uniqueness
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_platform_name'),
        UniqueConstraint('user_id', 'base_url', name='uq_user_platform_base_url'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'name': self.name,
            'platform': self.platform,
            'base_url': self.base_url,
            'token': self.token,  # Note: In real implementation, this should be masked
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_dict_masked(self) -> Dict[str, Any]:
        """Convert model to dictionary with masked token"""
        data = self.to_dict()
        if self.token:
            # Show only first 4 and last 4 characters
            token_len = len(self.token)
            if token_len > 8:
                data['token'] = f"{self.token[:4]}{'*' * (token_len - 8)}{self.token[-4:]}"
            else:
                data['token'] = '*' * token_len
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPlatformConfig':
        """Create model from dictionary"""
        return cls(
            name=data.get('name', ''),
            platform=data.get('platform', ''),
            base_url=data.get('base_url', ''),
            token=data.get('token', ''),
            is_default=data.get('is_default', False)
        )


# Database creation SQL for reference
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS user_platform_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    base_url VARCHAR(500) NOT NULL,
    token TEXT NOT NULL,
    is_default BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_platform (platform),
    UNIQUE KEY uq_user_platform_name (user_id, name),
    UNIQUE KEY uq_user_platform_base_url (user_id, base_url)
);
"""
