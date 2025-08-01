from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional
from api.auth import get_current_user_required
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

class AuthResponse(BaseModel):
    """Authentication response model"""
    access_token: str
    user_id: str
    github_id: str
    username: str
    avatar_url: Optional[str] = None

class UserProfile(BaseModel):
    """User profile response model"""
    id: str
    github_id: str
    username: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: str
    updated_at: str

@router.get("/github/login")
def github_login(redirect_uri: str = Query(..., description="Frontend redirect URI")):
    """Initiate GitHub OAuth login flow"""
    try:
        # Import here to avoid circular imports
        from main import github_oauth_service
        
        auth_url = github_oauth_service.get_authorization_url(redirect_uri)
        return {"auth_url": auth_url}
        
    except Exception as e:
        logger.error(f"Error initiating GitHub login: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate GitHub login")

@router.get("/github/callback")
async def github_callback(
    code: str = Query(..., description="GitHub authorization code"),
    redirect_uri: str = Query(..., description="Frontend redirect URI")
):
    """Handle GitHub OAuth callback and complete authentication"""
    try:
        # Import here to avoid circular imports
        from main import github_oauth_service
        
        # Exchange code for access token
        access_token = await github_oauth_service.exchange_code_for_token(code, redirect_uri)
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to exchange authorization code")
        
        # Get GitHub user information
        github_user_data = await github_oauth_service.get_github_user_info(access_token)
        if not github_user_data:
            raise HTTPException(status_code=400, detail="Failed to get GitHub user information")
        
        # Create or update user in database
        user = github_oauth_service.create_or_update_user(github_user_data, access_token)
        
        # Generate JWT token
        jwt_token = github_oauth_service.create_jwt_token(user.id)
        
        return AuthResponse(
            access_token=jwt_token,
            user_id=user.id,
            github_id=user.github_id,
            username=user.username,
            avatar_url=user.avatar_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in GitHub callback: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")

@router.get("/profile", response_model=UserProfile)
def get_user_profile(current_user_id: str = Depends(get_current_user_required)):
    """Get current user profile information"""
    try:
        # Import here to avoid circular imports
        from main import github_oauth_service
        
        user = github_oauth_service.get_user_by_id(current_user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserProfile(**user.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")

@router.post("/logout")
def logout(current_user_id: str = Depends(get_current_user_required)):
    """Logout user (client-side token removal)"""
    # Since we're using JWT tokens, logout is primarily handled client-side
    # by removing the token from storage
    return {"message": "Logout successful"}
