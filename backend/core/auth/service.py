from typing import Optional
import jwt
import httpx
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import User
import logging
import uuid

logger = logging.getLogger(__name__)

class GitHubOAuthService:
    """GitHub OAuth authentication service"""
    
    def __init__(self, users_session: Session, db_router, client_id: str, client_secret: str, jwt_secret: str):
        self.users_session = users_session
        self.db_router = db_router
        self.client_id = client_id
        self.client_secret = client_secret
        self.jwt_secret = jwt_secret
        self.github_api_base = "https://api.github.com"
        self.github_oauth_base = "https://github.com/login/oauth"
    
    def get_authorization_url(self, redirect_uri: str, state: Optional[str] = None) -> str:
        """Generate GitHub OAuth authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": "user:email",
            "state": state or str(uuid.uuid4())
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.github_oauth_base}/authorize?{query_string}"
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Optional[str]:
        """Exchange authorization code for access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.github_oauth_base}/access_token",
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "redirect_uri": redirect_uri
                    },
                    headers={"Accept": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("access_token")
                
                logger.error(f"Failed to exchange code for token: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            return None
    
    async def get_github_user_info(self, access_token: str) -> Optional[dict]:
        """Get GitHub user information using access token"""
        try:
            async with httpx.AsyncClient() as client:
                # Get user basic info
                user_response = await client.get(
                    f"{self.github_api_base}/user",
                    headers={"Authorization": f"token {access_token}"}
                )
                
                if user_response.status_code != 200:
                    logger.error(f"Failed to get user info: {user_response.text}")
                    return None
                
                user_data = user_response.json()
                
                # Get user email if not public
                if not user_data.get("email"):
                    email_response = await client.get(
                        f"{self.github_api_base}/user/emails",
                        headers={"Authorization": f"token {access_token}"}
                    )
                    
                    if email_response.status_code == 200:
                        emails = email_response.json()
                        primary_email = next((email["email"] for email in emails if email["primary"]), None)
                        user_data["email"] = primary_email
                
                return user_data
                
        except Exception as e:
            logger.error(f"Error getting GitHub user info: {e}")
            return None
    
    def create_or_update_user(self, github_user_data: dict, access_token: str) -> User:
        """Create new user or update existing user with GitHub data"""
        try:
            github_id = str(github_user_data["id"])
            
            # Check if user already exists
            existing_user = self.users_session.query(User).filter(
                User.github_id == github_id
            ).first()
            
            if existing_user:
                # Update existing user
                existing_user.username = github_user_data["login"]
                existing_user.email = github_user_data.get("email")
                existing_user.avatar_url = github_user_data.get("avatar_url")
                existing_user.access_token = access_token
                # updated_at will be automatically set by database UTC_TIMESTAMP()
                
                self.users_session.commit()
                logger.info(f"Updated existing user: {existing_user.username}")
                return existing_user
            else:
                # Create new user
                user = User(
                    github_id=github_id,
                    username=github_user_data["login"],
                    email=github_user_data.get("email"),
                    avatar_url=github_user_data.get("avatar_url"),
                    access_token=access_token
                )
                
                self.users_session.add(user)
                self.users_session.commit()
                
                # Create user-specific database
                self.db_router.create_user_database(user.id)
                
                logger.info(f"Created new user: {user.username}")
                return user
                
        except Exception as e:
            self.users_session.rollback()
            logger.error(f"Error creating/updating user: {e}")
            raise
    
    def create_jwt_token(self, user_id: str) -> str:
        """Create JWT token for authenticated user"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(days=7),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")
    
    def verify_jwt_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return user ID"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload.get("user_id")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users_session.query(User).filter(User.id == user_id).first()
    
    def get_user_by_github_id(self, github_id: str) -> Optional[User]:
        """Get user by GitHub ID"""
        return self.users_session.query(User).filter(User.github_id == github_id).first()
