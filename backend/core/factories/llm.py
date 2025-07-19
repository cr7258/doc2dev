"""
LLM Factory

Factory for creating different Language Model instances based on configuration.
"""

from typing import Union
from langchain_core.language_models.base import BaseLanguageModel
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_huggingface import HuggingFacePipeline
from langchain_community.llms import Ollama

from config.llm import (
    LLMConfig,
    OpenAILLMConfig,
    AnthropicLLMConfig,
    HuggingFaceLLMConfig,
    OllamaLLMConfig,
    AzureOpenAILLMConfig,
)


class LLMFactory:
    """Factory for creating Language Model instances"""
    
    @staticmethod
    def create_llm(llm_config: LLMConfig) -> BaseLanguageModel:
        """
        Create a Language Model instance based on configuration.
        
        Args:
            llm_config: LLM configuration with provider-specific settings
            
        Returns:
            BaseLanguageModel instance
            
        Raises:
            ValueError: If unsupported LLM type is specified
        """
        specific_config = llm_config.config
        
        match specific_config.type:
            case "openai":
                return LLMFactory._create_openai_llm(specific_config)
            case "anthropic":
                return LLMFactory._create_anthropic_llm(specific_config)
            case "huggingface":
                return LLMFactory._create_huggingface_llm(specific_config)
            case "ollama":
                return LLMFactory._create_ollama_llm(specific_config)
            case "azure_openai":
                return LLMFactory._create_azure_openai_llm(specific_config)
            case _:
                raise ValueError(f"Unsupported LLM type: {specific_config.type}")
    
    @staticmethod
    def _create_openai_llm(config: OpenAILLMConfig) -> ChatOpenAI:
        """Create OpenAI ChatGPT instance"""
        return ChatOpenAI(
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            openai_api_key=config.api_key,
            openai_api_base=config.api_base,
        )
    
    @staticmethod
    def _create_anthropic_llm(config: AnthropicLLMConfig) -> ChatAnthropic:
        """Create Anthropic Claude instance"""
        return ChatAnthropic(
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            anthropic_api_key=config.api_key,
        )
    
    @staticmethod
    def _create_huggingface_llm(config: HuggingFaceLLMConfig) -> HuggingFacePipeline:
        """Create HuggingFace model instance"""
        try:
            from transformers import pipeline
        except ImportError:
            raise ImportError(
                "transformers package is required for HuggingFace models. "
                "Install with: pip install transformers torch"
            )
        
        # Create HuggingFace pipeline
        hf_pipeline = pipeline(
            "text-generation",
            model=config.model,
            temperature=config.temperature,
            max_new_tokens=config.max_tokens,
            token=config.api_key,  # HuggingFace token (optional)
        )
        
        return HuggingFacePipeline(pipeline=hf_pipeline)
    
    @staticmethod
    def _create_ollama_llm(config: OllamaLLMConfig) -> Ollama:
        """Create Ollama local model instance"""
        return Ollama(
            base_url=config.base_url,
            model=config.model,
            temperature=config.temperature,
        )
    
    @staticmethod
    def _create_azure_openai_llm(config: AzureOpenAILLMConfig) -> AzureChatOpenAI:
        """Create Azure OpenAI instance"""
        return AzureChatOpenAI(
            deployment_name=config.deployment_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            azure_endpoint=config.azure_endpoint,
            api_key=config.api_key,
            api_version=config.api_version,
        )
    
    @staticmethod
    def get_supported_llm_types() -> list[str]:
        """Get list of supported LLM types"""
        return ["openai", "anthropic", "huggingface", "ollama", "azure_openai"]
