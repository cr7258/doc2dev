# Token Selection Logic Fix

## 🎯 Problem Description

When downloading public GitHub repositories (like `https://github.com/cr7258/httpbin`), the system was incorrectly using enterprise GitHub tokens instead of the public GitHub token from environment variables.

## 🔧 Root Cause

The original token selection logic had these issues:

1. **Fallback Logic**: `get_user_config_for_platform()` would return any user configuration if no exact base_url match was found
2. **No Domain Prioritization**: Public platforms (github.com, gitlab.com) weren't prioritized for environment variable tokens

## ✅ Solution Implemented

### 1. **Updated Token Selection Logic**

#### GitHub (`backend/core/git/github.py`)
```python
def get_git_token(self, repo_url: Optional[str] = None) -> str:
    # For public GitHub (github.com), prioritize environment variable
    if repo_domain == "github.com":
        env_token = os.getenv("GITHUB_TOKEN", "")
        if env_token:
            return env_token
    
    # For enterprise GitHub, try user-specific configuration first
    # Only exact base_url matches are returned
```

#### GitLab (`backend/core/git/gitlab.py`)
```python
def get_git_token(self, repo_url: Optional[str] = None) -> str:
    # For public GitLab (gitlab.com), prioritize environment variable
    if repo_domain == "gitlab.com":
        env_token = os.getenv("GITLAB_TOKEN", "")
        if env_token:
            return env_token
    
    # For enterprise GitLab, try user-specific configuration first
    # Only exact base_url matches are returned
```

### 2. **Fixed Platform Configuration Service**

#### Updated `get_user_config_for_platform()` (`backend/core/services/platform_config.py`)
- **Before**: Would return default or any configuration if no exact match
- **After**: Only returns exact base_url matches
- **Added**: `get_user_default_config_for_platform()` for other use cases

## 🎯 New Token Selection Priority

### For Public Platforms (github.com, gitlab.com):
1. **Environment Variable** (`GITHUB_TOKEN` / `GITLAB_TOKEN`) - **HIGHEST PRIORITY**
2. Global configuration
3. Fallback environment variable

### For Enterprise Platforms (github.tools.sap, gitlab.company.com, etc.):
1. **User-configured token** (exact base_url match) - **HIGHEST PRIORITY**
2. Global configuration
3. Environment variable fallback

## 🧪 Testing Results

```bash
# Public GitHub
https://github.com/cr7258/httpbin → Uses GITHUB_TOKEN ✅

# Enterprise GitHub  
https://github.tools.sap/user/repo → Uses user-configured token ✅

# Public GitLab
https://gitlab.com/group/project → Uses GITLAB_TOKEN ✅

# Enterprise GitLab
https://gitlab.company.com/team/project → Uses user-configured token ✅
```

## 🎉 Benefits

1. **Correct Authentication**: Public repos use public tokens, enterprise repos use enterprise tokens
2. **Security**: No token leakage between different platforms
3. **Flexibility**: Users can still configure enterprise instances while using public tokens for public repos
4. **Backward Compatibility**: Existing enterprise configurations continue to work

## 🔍 Key Files Modified

- `backend/core/git/github.py` - GitHub token selection logic
- `backend/core/git/gitlab.py` - GitLab token selection logic  
- `backend/core/services/platform_config.py` - Platform configuration matching logic

The fix ensures that the system correctly matches repository URLs with appropriate authentication tokens based on the domain and user configuration.
