#!/usr/bin/env python3
"""
Example usage of LLM Factory and updated SummaryService.

This example demonstrates:
1. Using different LLM providers (OpenAI, Anthropic, Ollama, etc.)
2. Configuring LLM settings via environment variables
3. Using the updated SummaryService with flexible LLM support
4. Switching between different LLM providers
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from config.settings import Settings
from config.llm import LLMConfig, OpenAILLMConfig, AnthropicLLMConfig, OllamaLLMConfig
from core.factories.llm import LLMFactory
from core.services import SummaryService
from langchain_core.documents import Document


def example_llm_factory_usage():
    """Example of using LLMFactory directly with different providers"""
    print("=== LLM Factory Direct Usage ===")
    
    # Example 1: OpenAI Configuration
    print("\n1. OpenAI LLM Example:")
    try:
        openai_config = LLMConfig(config=OpenAILLMConfig(
            api_key=os.environ.get("OPENAI_API_KEY", "sk-test"),
            model="gpt-4o",
            temperature=0.3
        ))
        
        openai_llm = LLMFactory.create_llm(openai_config)
        print(f"✅ Created OpenAI LLM: {type(openai_llm).__name__}")
        
    except Exception as e:
        print(f"❌ OpenAI LLM creation failed: {e}")
    
    # Example 2: Anthropic Configuration
    print("\n2. Anthropic LLM Example:")
    try:
        anthropic_config = LLMConfig(config=AnthropicLLMConfig(
            api_key=os.environ.get("ANTHROPIC_API_KEY", "test-key"),
            model="claude-3-opus-20240229"
        ))
        
        anthropic_llm = LLMFactory.create_llm(anthropic_config)
        print(f"✅ Created Anthropic LLM: {type(anthropic_llm).__name__}")
        
    except Exception as e:
        print(f"❌ Anthropic LLM creation failed: {e}")
    
    # Example 3: Ollama Configuration (local)
    print("\n3. Ollama LLM Example:")
    try:
        ollama_config = LLMConfig(config=OllamaLLMConfig(
            base_url="http://localhost:11434",
            model="llama2"
        ))
        
        ollama_llm = LLMFactory.create_llm(ollama_config)
        print(f"✅ Created Ollama LLM: {type(ollama_llm).__name__}")
        
    except Exception as e:
        print(f"❌ Ollama LLM creation failed: {e}")


def example_summary_service_with_different_llms():
    """Example of using SummaryService with different LLM providers"""
    print("\n=== SummaryService with Different LLMs ===")
    
    # Create sample documents
    sample_documents = [
        Document(
            page_content="FastAPI is a modern, fast web framework for building APIs with Python 3.7+. It's based on standard Python type hints and provides automatic API documentation.",
            metadata={"source": "fastapi_intro.md", "category": "web_framework"}
        ),
        Document(
            page_content="LangChain provides a standard interface for chains, lots of integrations with other tools, and end-to-end chains for common applications.",
            metadata={"source": "langchain_overview.md", "category": "ai_framework"}
        )
    ]
    
    query = "Python web development with AI integration"
    
    # Test with different LLM configurations
    llm_configs = [
        ("OpenAI", {
            "LLM_CONFIG_TYPE": "openai",
            "LLM_OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", ""),
            "LLM_OPENAI_MODEL": "gpt-4o"
        }),
        ("Anthropic", {
            "LLM_CONFIG_TYPE": "anthropic", 
            "LLM_ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY", ""),
            "LLM_ANTHROPIC_MODEL": "claude-3-opus-20240229"
        }),
        ("Ollama", {
            "LLM_CONFIG_TYPE": "ollama",
            "LLM_OLLAMA_BASE_URL": "http://localhost:11434",
            "LLM_OLLAMA_MODEL": "llama2"
        })
    ]
    
    for provider_name, env_vars in llm_configs:
        print(f"\n--- Testing {provider_name} LLM ---")
        
        # Temporarily set environment variables
        original_env = {}
        for key, value in env_vars.items():
            original_env[key] = os.environ.get(key)
            if value:  # Only set if value is not empty
                os.environ[key] = value
        
        try:
            # Create settings with the new environment
            settings = Settings()
            
            # Create and test SummaryService
            summary_service = SummaryService(settings)
            
            print(f"Using {provider_name} ({settings.llm.config.type}) for summarization...")
            summary = summary_service.summarize_search_results(sample_documents, query)
            
            print(f"✅ {provider_name} Summary generated successfully")
            print(f"Summary preview: {summary[:200]}...")
            
            # Service cleanup is automatic
            
        except Exception as e:
            print(f"❌ {provider_name} failed: {e}")
        
        finally:
            # Restore original environment variables
            for key, original_value in original_env.items():
                if original_value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = original_value


def example_configuration_from_env():
    """Example of loading LLM configuration from environment variables"""
    print("\n=== Configuration from Environment Variables ===")
    
    print("Supported LLM types:", LLMFactory.get_supported_llm_types())
    
    # Show current configuration
    try:
        settings = Settings()
        print(f"Current LLM provider: {settings.llm.config.type}")
        print(f"Current LLM config: {settings.llm.config}")
        
    except Exception as e:
        print(f"Configuration error: {e}")
        print("Make sure to set LLM_CONFIG_TYPE and corresponding provider settings in .env")


def show_env_configuration_examples():
    """Show examples of environment variable configurations"""
    print("\n=== Environment Configuration Examples ===")
    
    examples = {
        "OpenAI": [
            "LLM_CONFIG_TYPE=openai",
            "LLM_OPENAI_API_KEY=your_openai_key",
            "LLM_OPENAI_MODEL=gpt-4o",
            "LLM_OPENAI_TEMPERATURE=0.3"
        ],
        "Anthropic": [
            "LLM_CONFIG_TYPE=anthropic",
            "LLM_ANTHROPIC_API_KEY=your_anthropic_key", 
            "LLM_ANTHROPIC_MODEL=claude-3-opus-20240229"
        ],
        "Ollama (Local)": [
            "LLM_CONFIG_TYPE=ollama",
            "LLM_OLLAMA_BASE_URL=http://localhost:11434",
            "LLM_OLLAMA_MODEL=llama2"
        ]
    }
    
    for provider, env_vars in examples.items():
        print(f"\n{provider} Configuration:")
        for var in env_vars:
            print(f"  {var}")


if __name__ == "__main__":
    print("LLM Factory and SummaryService Examples")
    print("=" * 50)
    
    # Show configuration examples
    show_env_configuration_examples()
    
    # Show current configuration
    example_configuration_from_env()
    
    # Test LLM Factory directly
    example_llm_factory_usage()
    
    # Test SummaryService with different LLMs
    # Note: This will only work if you have valid API keys
    if os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"):
        example_summary_service_with_different_llms()
    else:
        print("\n⚠️  Skipping SummaryService tests - no API keys found")
        print("Set OPENAI_API_KEY or ANTHROPIC_API_KEY to test summarization")
    
    print("\nExamples completed!")
    print("Check .env.example for complete configuration options")
