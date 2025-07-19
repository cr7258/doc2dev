"""
LLM Configuration

Configuration classes for different Language Model providers using Pydantic v2 discriminated unions.
"""

from typing import Literal, Union, Optional
from pydantic import BaseModel, Field


class OpenAILLMConfig(BaseModel):
    """OpenAI LLM configuration"""
    type: Literal["openai"] = "openai"
    api_key: str = Field(..., description="OpenAI API key")
    api_base: str = Field(default="https://api.openai.com/v1", description="OpenAI API base URL")
    model: str = Field(default="gpt-4o", description="OpenAI model name")
    temperature: float = Field(default=0.3, ge=0.0, le=2.0, description="Temperature for response generation")
    max_tokens: int = Field(default=2000, gt=0, description="Maximum tokens in response")
    
    class Config:
        env_prefix = "LLM_OPENAI_"


class AnthropicLLMConfig(BaseModel):
    """Anthropic Claude LLM configuration"""
    type: Literal["anthropic"] = "anthropic"
    api_key: str = Field(..., description="Anthropic API key")
    model: str = Field(default="claude-3-opus-20240229", description="Anthropic model name")
    temperature: float = Field(default=0.3, ge=0.0, le=1.0, description="Temperature for response generation")
    max_tokens: int = Field(default=2000, gt=0, description="Maximum tokens in response")
    
    class Config:
        env_prefix = "LLM_ANTHROPIC_"


class HuggingFaceLLMConfig(BaseModel):
    """HuggingFace LLM configuration"""
    type: Literal["huggingface"] = "huggingface"
    api_key: Optional[str] = Field(default=None, description="HuggingFace API key (optional for some models)")
    model: str = Field(default="microsoft/DialoGPT-medium", description="HuggingFace model name")
    temperature: float = Field(default=0.3, ge=0.0, le=1.0, description="Temperature for response generation")
    max_tokens: int = Field(default=2000, gt=0, description="Maximum tokens in response")
    
    class Config:
        env_prefix = "LLM_HUGGINGFACE_"


class OllamaLLMConfig(BaseModel):
    """Ollama local LLM configuration"""
    type: Literal["ollama"] = "ollama"
    base_url: str = Field(default="http://localhost:11434", description="Ollama server URL")
    model: str = Field(default="llama2", description="Ollama model name")
    temperature: float = Field(default=0.3, ge=0.0, le=1.0, description="Temperature for response generation")
    
    class Config:
        env_prefix = "LLM_OLLAMA_"


class AzureOpenAILLMConfig(BaseModel):
    """Azure OpenAI LLM configuration"""
    type: Literal["azure_openai"] = "azure_openai"
    api_key: str = Field(..., description="Azure OpenAI API key")
    azure_endpoint: str = Field(..., description="Azure OpenAI endpoint")
    api_version: str = Field(default="2024-02-15-preview", description="Azure OpenAI API version")
    deployment_name: str = Field(..., description="Azure OpenAI deployment name")
    temperature: float = Field(default=0.3, ge=0.0, le=2.0, description="Temperature for response generation")
    max_tokens: int = Field(default=2000, gt=0, description="Maximum tokens in response")
    
    class Config:
        env_prefix = "LLM_AZURE_OPENAI_"


# Union type for all LLM configurations
LLMConfigUnion = Union[
    OpenAILLMConfig,
    AnthropicLLMConfig,
    HuggingFaceLLMConfig,
    OllamaLLMConfig,
    AzureOpenAILLMConfig,
]


class LLMConfig(BaseModel):
    """Main LLM configuration with discriminated union"""
    config: LLMConfigUnion = Field(..., discriminator='type', description="LLM provider configuration")
    
    class Config:
        env_prefix = "LLM_"
