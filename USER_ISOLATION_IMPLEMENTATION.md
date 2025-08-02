# User Isolation Implementation for doc2dev

## Overview

This document describes the implementation of user isolation in the doc2dev application to ensure that logged-in users can only see and manage their own repositories, not all public repositories.

## Problem Statement

Previously, all users could see all repositories stored in the public database (`doc2dev`), which was a security issue. The goal was to implement proper user isolation so that:

1. Unauthenticated users can see public repositories but cannot perform repository operations
2. Authenticated users can only see repositories they have created/own
3. Repository operations (create, read, update, delete) are scoped to the authenticated user

## Solution Architecture

The solution leverages the existing multi-tenant database architecture:

- **Public Database (`doc2dev`)**: Stores public repositories visible to all users
- **User Private Databases (`doc2dev_user_{user_id}`)**: Each user has their own database where their private repositories are stored
- **Authentication**: Repository viewing supports both authenticated and unauthenticated access, but repository operations require JWT authentication

## Implementation Details

### 1. Backend API Changes

#### Repository Routes (`backend/routes/repository.py`)

**Modified Endpoints:**
- `GET /repositories/` - Returns public repositories for unauthenticated users, user's private repositories for authenticated users
- `POST /download/` - Requires authentication and saves repositories to user's private database
- `GET /repositories/{repo_path}` - Requires authentication and looks up in user's database
- `DELETE /repositories/{repo_id}` - Requires authentication and deletes from user's database

**Key Changes:**
```python
# Added optional authentication for repository listing
from api.auth import get_current_user_required, get_current_user_optional

@router.get("/repositories/")
async def get_repositories(current_user_id: str = Depends(get_current_user_optional)):
    # Return different data based on authentication status
    if current_user_id:
        # User is logged in - return their private repositories
        repositories = repository_service.get_user_repositories(current_user_id)
    else:
        # User is not logged in - return all public repositories
        repositories = repository_service.get_repositories()
```

#### Repository Service (`backend/core/services/repository.py`)

**New User-Specific Methods:**
- `get_user_repositories(user_id)` - Get all repositories for a specific user
- `get_user_repository_by_path(user_id, repo_path)` - Get repository by path for a user
- `get_user_repository_by_id(user_id, repo_id)` - Get repository by ID for a user
- `create_user_repository(user_id, ...)` - Create repository in user's database
- `update_user_repository_status(user_id, repo_id, status)` - Update repository status
- `update_user_repository_counts(user_id, repo_id, tokens, snippets)` - Update counts
- `delete_user_repository(user_id, repo_id)` - Delete repository from user's database

**Key Implementation:**
```python
def get_user_repositories(self, user_id: str) -> List[Repository]:
    user_session = self.db_router.get_session(user_id)
    repositories = user_session.query(Repository).order_by(Repository.name).all()
    return repositories
```

#### Repository Processor (`backend/tasks/repository_processor.py`)

**Modified Background Processing:**
- `process_repository_background()` now accepts `user_id` parameter
- Repository creation, status updates, and count updates use user-specific methods
- All database operations are performed on the user's private database

**Key Changes:**
```python
async def process_repository_background(self, repo_url: str, user_id: str, ...):
    # Check if repository exists for this user
    existing_repo = self.repository_service.get_user_repository_by_path(user_id, repo_path)
    
    # Create repository in user's database
    repo_id = self.repository_service.create_user_repository(user_id, ...)
```

### 2. Frontend Changes

#### Main Page (`frontend/app/page.tsx`)

**Authentication Integration:**
- Added `useAuth` hook to get user token
- Repository list requests include Authorization header when user is logged in
- Repository deletion requests include Authorization header
- Requests are made regardless of authentication status (public access for unauthenticated users)

**Key Changes:**
```typescript
const { token, user } = useAuth();

// Repository fetch with optional authentication
const headers: Record<string, string> = {
  'Content-Type': 'application/json',
};

if (token) {
  headers['Authorization'] = `Bearer ${token}`;
}

const response = await fetch(`${BACKEND_URL}/repositories/`, {
  headers,
});
```

#### Search Component (`frontend/components/search.tsx`)

**Similar Authentication Changes:**
- Added `useAuth` hook
- Repository suggestions now require authentication
- Requests include Authorization header

### 3. Database Architecture

The multi-tenant database structure remains the same:

```
doc2dev_users          # User authentication data
doc2dev               # Public database (stores public repositories)
doc2dev_user_1        # User 1's private database with their repositories
doc2dev_user_2        # User 2's private database with their repositories
...
```

Each user's private database contains:
- `repositories` table with their repositories
- `code_snippets` table with their code snippets
- Vector tables for their repository embeddings

## Security Benefits

1. **Data Isolation**: Authenticated users can only access their own private data
2. **Public Access Control**: Unauthenticated users can only view public repositories
3. **Operation Authentication**: Repository operations (create, update, delete) require valid JWT token
4. **Authorization Scoped**: Operations are scoped to the authenticated user's database
5. **No Cross-User Access**: Users cannot see or modify other users' private repositories

## Testing

A test script (`test_user_isolation.py`) has been created to verify:

1. Unauthenticated users can access public repositories
2. Unauthenticated users cannot download repositories
3. Authenticated users can access their own private repositories
4. Repository download works with authentication

## Migration Notes

**For Existing Data:**
- Existing repositories in the public database need to be migrated to user-specific databases
- This requires mapping repositories to their original creators
- A migration script should be created for production deployment

**For New Installations:**
- No migration needed
- All repositories will be created in user-specific databases from the start

## Future Enhancements

1. **Repository Sharing**: Allow users to share repositories with other users
2. **Organization Support**: Support for organization-level repositories
3. **Public Repositories**: Option to make repositories publicly visible
4. **Access Control**: Fine-grained permissions for repository access

## Conclusion

The user isolation implementation successfully addresses the security issue by:
- Requiring authentication for all repository operations
- Storing repositories in user-specific databases
- Ensuring users can only access their own data
- Maintaining the existing multi-tenant architecture

This provides a secure foundation for the doc2dev application while preserving all existing functionality.
