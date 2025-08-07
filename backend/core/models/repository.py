"""
Repository Data Model

SQLAlchemy ORM model for repository metadata management.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class RepositoryStatus(str, Enum):
    """Repository processing status enumeration"""
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"

class RepositorySource(str, Enum):
    """Repository source platform enumeration"""
    github = "github"
    gitlab = "gitlab"

class Repository(Base):
    """
    Repository ORM model
    
    Represents a code repository with its metadata and processing status.
    """
    __tablename__ = 'repositories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    repo = Column(String(255), nullable=False)  # Repository path like /owner/repo
    repo_url = Column(String(255), nullable=False)
    tokens = Column(Integer, default=0, nullable=False)
    snippets = Column(Integer, default=0, nullable=False)
    repo_status = Column(
        SQLEnum(RepositoryStatus),
        default=RepositoryStatus.pending,
        nullable=False
    )
    source = Column(
        SQLEnum(RepositorySource),
        default=RepositorySource.github,
        nullable=False
    )
    created_at = Column(DateTime, default=func.utc_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=func.utc_timestamp(), onupdate=func.utc_timestamp(), nullable=False)
    
    def __repr__(self):
        return f"<Repository(id={self.id}, name='{self.name}', repo='{self.repo}', status='{self.repo_status}')>"
    
    def to_dict(self) -> dict:
        """Convert repository to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'repo': self.repo,
            'repo_url': self.repo_url,
            'tokens': self.tokens,
            'snippets': self.snippets,
            'repo_status': self.repo_status,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
