from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class User(Base):
    """GitHub OAuth user model"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    github_id = Column(String(50), unique=True, nullable=False)  # GitHub user ID
    username = Column(String(50), nullable=False)  # GitHub username
    email = Column(String(100), nullable=True)  # GitHub email (optional)
    avatar_url = Column(String(500), nullable=True)  # GitHub avatar URL
    access_token = Column(String(255), nullable=True)  # GitHub access token (encrypted)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        """Convert user object to dictionary for API responses"""
        return {
            "id": self.id,
            "github_id": self.github_id,
            "username": self.username,
            "email": self.email,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
