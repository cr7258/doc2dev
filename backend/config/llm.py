"""
LLM Configuration

Configuration classes for different Language Model providers using Pydantic v2 discriminated unions.
"""

import os
from typing import Literal, Union, Optional, Annotated
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenAILLMConfig(BaseSettings):
    """OpenAI LLM configuration"""
    type: Literal["openai"] = "openai"
    api_key: str = Field(..., description="OpenAI API key")
    api_base: str = Field(default="https://api.openai.com/v1", description="OpenAI API base URL")
    model: str = Field(default="gpt-4o", description="OpenAI model name")
    temperature: float = Field(default=0.3, ge=0.0, le=2.0, description="Temperature for response generation")
    max_tokens: int = Field(default=2000, gt=0, description="Maximum tokens in response")
    
    model_config = SettingsConfigDict(env_prefix='LLM_OPENAI_')


class AnthropicLLMConfig(BaseSettings):
    """Anthropic Claude LLM configuration"""
    type: Literal["anthropic"] = "anthropic"
    api_key: str = Field(..., description="Anthropic API key")
    model: str = Field(default="claude-3-opus-20240229", description="Anthropic model name")
    temperature: float = Field(default=0.3, ge=0.0, le=1.0, description="Temperature for response generation")
    max_tokens: int = Field(default=2000, gt=0, description="Maximum tokens in response")
    
    model_config = SettingsConfigDict(env_prefix='LLM_ANTHROPIC_')


class HuggingFaceLLMConfig(BaseSettings):
    """HuggingFace LLM configuration"""
    type: Literal["huggingface"] = "huggingface"
    api_key: Optional[str] = Field(default=None, description="HuggingFace API key (optional for some models)")
    model: str = Field(default="microsoft/DialoGPT-medium", description="HuggingFace model name")
    temperature: float = Field(default=0.3, ge=0.0, le=1.0, description="Temperature for response generation")
    max_tokens: int = Field(default=2000, gt=0, description="Maximum tokens in response")
    
    model_config = SettingsConfigDict(env_prefix='LLM_HUGGINGFACE_')


class OllamaLLMConfig(BaseSettings):
    """Ollama local LLM configuration"""
    type: Literal["ollama"] = "ollama"
    base_url: str = Field(default="http://localhost:11434", description="Ollama server URL")
    model: str = Field(default="llama2", description="Ollama model name")
    temperature: float = Field(default=0.3, ge=0.0, le=1.0, description="Temperature for response generation")
    
    model_config = SettingsConfigDict(env_prefix='LLM_OLLAMA_')

# Discriminated union for LLM configurations
LLMConfigUnion = Annotated[
    OpenAILLMConfig | AnthropicLLMConfig | HuggingFaceLLMConfig | OllamaLLMConfig,
    Field(discriminator='type')
]

class LLMConfig(BaseSettings):
    """Configuration for LLM service"""
    config: LLMConfigUnion
    
    model_config = SettingsConfigDict(
        env_prefix='LLM_', 
        env_nested_delimiter='_'
    )
