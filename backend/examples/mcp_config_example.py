#!/usr/bin/env python3
"""
Example demonstrating MCP server configuration management.

This example shows how the MCP server now uses configurable settings
instead of hardcoded values.
"""

import os
from config.settings import Settings

def demonstrate_mcp_configuration():
    """Demonstrate MCP server configuration options"""
    
    print("🔧 Doc2Dev MCP Server Configuration Example")
    print("=" * 50)
    
    print("\n📋 1. Default Configuration")
    print("-" * 30)
    
    # Load default settings
    settings = Settings()
    print(f"API Base URL: {settings.api_base_url}")
    print(f"App Name: {settings.app_name}")
    print(f"Debug Mode: {settings.debug}")
    print(f"Log Level: {settings.log_level}")
    
    print("\n🌍 2. Environment Variable Configuration")
    print("-" * 40)
    
    # Show how to override via environment variables
    print("You can override settings using environment variables:")
    print("export API_BASE_URL=http://production-server:8000")
    print("export DEBUG=true")
    print("export LOG_LEVEL=DEBUG")
    
    # Demonstrate environment variable override
    original_url = settings.api_base_url
    os.environ["API_BASE_URL"] = "http://custom-server:9000"
    
    # Reload settings to pick up environment changes
    custom_settings = Settings()
    print(f"\nOriginal API URL: {original_url}")
    print(f"Custom API URL: {custom_settings.api_base_url}")
    
    # Clean up environment
    del os.environ["API_BASE_URL"]
    
    print("\n📝 3. .env File Configuration")
    print("-" * 30)
    
    print("Create a .env file with your configuration:")
    print("""
# API Configuration
API_BASE_URL=http://localhost:8000

# Application Settings
APP_NAME=Doc2Dev
DEBUG=false
LOG_LEVEL=INFO

# Database Configuration
METADATA_DB_TYPE=oceanbase
OCEANBASE_HOST=127.0.0.1
OCEANBASE_PORT=2881
OCEANBASE_USER=root@test
OCEANBASE_PASSWORD=admin
OCEANBASE_DATABASE=doc2dev
""")
    
    print("\n🚀 4. MCP Server Usage with Custom Configuration")
    print("-" * 50)
    
    print("The MCP server will automatically use your configuration:")
    print("1. Load settings from .env file")
    print("2. Override with environment variables if set")
    print("3. Use configured API base URL for documentation queries")
    
    print("\n✅ 5. Configuration Benefits")
    print("-" * 30)
    print("✅ No hardcoded URLs in source code")
    print("✅ Easy to switch between development/production")
    print("✅ Centralized configuration management")
    print("✅ Environment-specific settings")
    print("✅ Consistent with overall architecture")
    
    print("\n🔧 6. Available Configuration Options")
    print("-" * 35)
    print("API_BASE_URL - Base URL for API calls")
    print("APP_NAME - Application name")
    print("DEBUG - Enable debug mode")
    print("LOG_LEVEL - Logging level (DEBUG, INFO, WARNING, ERROR)")
    print("Plus all database, vector store, embedding, and LLM configs")

if __name__ == "__main__":
    demonstrate_mcp_configuration()
