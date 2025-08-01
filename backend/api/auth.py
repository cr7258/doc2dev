from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """Optional authentication: returns user ID or None for public access"""
    if not credentials:
        return None
    
    # Import here to avoid circular imports
    from main import github_oauth_service
    
    user_id = github_oauth_service.verify_jwt_token(credentials.credentials)
    return user_id

def get_current_user_required(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Required authentication: returns user ID or raises exception"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # Import here to avoid circular imports
    from main import github_oauth_service
    
    user_id = github_oauth_service.verify_jwt_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    
    return user_id
