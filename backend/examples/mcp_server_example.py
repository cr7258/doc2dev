#!/usr/bin/env python3
"""
Example demonstrating the refactored MCP server usage.

This example shows how the MCP server now uses the service layer
architecture instead of direct database connections.
"""

import asyncio
from config.settings import Settings
from core.services.repository import RepositoryService

async def demonstrate_mcp_functionality():
    """Demonstrate MCP server functionality using the service layer"""
    
    print("🚀 Doc2Dev MCP Server Example")
    print("=" * 50)
    
    # Initialize settings and repository service
    settings = Settings()
    repository_service = RepositoryService(settings)
    
    print("\n📋 1. Testing Repository Search Functionality")
    print("-" * 40)
    
    # Test search functionality (same as MCP search-library-id tool)
    search_terms = ["kubernetes", "langchain", "elasticsearch"]
    
    for term in search_terms:
        print(f"\n🔍 Searching for: '{term}'")
        repositories = repository_service.search_repositories(term)
        
        if repositories:
            print(f"✅ Found {len(repositories)} matching repositories:")
            for repo in repositories[:3]:  # Show first 3 results
                library_id = repo.repo.lstrip('/').replace('/', '_')
                print(f"  - Library ID: {library_id}")
                print(f"    Repository: {repo.repo}")
                print(f"    Name: {repo.name}")
                print(f"    Status: {repo.repo_status.value if repo.repo_status else 'unknown'}")
                print(f"    Tokens: {repo.tokens}, Snippets: {repo.snippets}")
        else:
            print(f"❌ No repositories found for '{term}'")
    
    print("\n📚 2. MCP Server Architecture Benefits")
    print("-" * 40)
    print("✅ Uses RepositoryService for database operations")
    print("✅ Leverages existing service layer architecture")
    print("✅ Maintains consistent error handling and logging")
    print("✅ Follows single responsibility principle")
    print("✅ Easy to test and maintain")
    
    print("\n🔧 3. How to Run the MCP Server")
    print("-" * 40)
    print("1. Navigate to the backend directory:")
    print("   cd /Users/I576375/Code/ai/doc2dev/backend")
    print("\n2. Run the MCP server:")
    print("   python mcp/server.py")
    print("\n3. The server will provide two tools:")
    print("   - search-library-id: Search for library IDs")
    print("   - get-library-docs: Get documentation via API")
    
    print("\n🎯 4. Migration Benefits")
    print("-" * 40)
    print("✅ Removed direct database connection code")
    print("✅ Uses centralized configuration management")
    print("✅ Leverages existing RepositoryService methods")
    print("✅ Consistent with overall architecture")
    print("✅ Better error handling and logging")

if __name__ == "__main__":
    asyncio.run(demonstrate_mcp_functionality())
