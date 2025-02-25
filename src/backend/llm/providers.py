from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from pydantic import BaseModel
import os
import yaml
from langchain.chat_models import (
    ChatOpenAI,
    ChatGooglePalm,
    ChatAnthropic,
    ChatVertexAI
)
from langchain.schema import HumanMessage

class LLMProviderConfig(BaseModel):
    """Configuration for LLM providers"""
    provider_name: str
    model_name: str
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    additional_config: Dict[str, Any] = {}

class BaseLLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    def initialize_model(self, config: LLMProviderConfig):
        """Initialize the LLM model"""
        pass
    
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate response from prompt"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        pass

class OpenAIProvider(BaseLLMProvider):
    """OpenAI-compatible provider"""
    
    def initialize_model(self, config: LLMProviderConfig):
        api_key = config.api_key or os.getenv("OPENAI_API_KEY")
        self.model = ChatOpenAI(
            model_name=config.model_name,
            temperature=config.temperature,
            openai_api_key=api_key,
            max_tokens=config.max_tokens,
            **config.additional_config
        )
    
    async def generate(self, prompt: str) -> str:
        messages = [HumanMessage(content=prompt)]
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    def get_available_models(self) -> List[str]:
        return [
            "gpt-4",
            "gpt-4-turbo-preview",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]

class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider"""
    
    def initialize_model(self, config: LLMProviderConfig):
        api_key = config.api_key or os.getenv("GOOGLE_API_KEY")
        self.model = ChatGooglePalm(
            google_api_key=api_key,
            model_name=config.model_name,
            temperature=config.temperature,
            max_output_tokens=config.max_tokens,
            **config.additional_config
        )
    
    async def generate(self, prompt: str) -> str:
        messages = [HumanMessage(content=prompt)]
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    def get_available_models(self) -> List[str]:
        return [
            "gemini-pro",
            "gemini-pro-vision"
        ]

class VertexAIProvider(BaseLLMProvider):
    """Google VertexAI provider"""
    
    def initialize_model(self, config: LLMProviderConfig):
        self.model = ChatVertexAI(
            model_name=config.model_name,
            temperature=config.temperature,
            max_output_tokens=config.max_tokens,
            project=config.additional_config.get("project"),
            location=config.additional_config.get("location"),
            **config.additional_config
        )
    
    async def generate(self, prompt: str) -> str:
        messages = [HumanMessage(content=prompt)]
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    def get_available_models(self) -> List[str]:
        return [
            "text-bison",
            "code-bison",
            "codechat-bison"
        ]

class AnthropicProvider(BaseLLMProvider):
    """Anthropic provider"""
    
    def initialize_model(self, config: LLMProviderConfig):
        api_key = config.api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = ChatAnthropic(
            model_name=config.model_name,
            anthropic_api_key=api_key,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            **config.additional_config
        )
    
    async def generate(self, prompt: str) -> str:
        messages = [HumanMessage(content=prompt)]
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    def get_available_models(self) -> List[str]:
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-2.1",
            "claude-instant-1.2"
        ]

class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter provider for multiple models"""
    
    def initialize_model(self, config: LLMProviderConfig):
        api_key = config.api_key or os.getenv("OPENROUTER_API_KEY")
        base_url = "https://openrouter.ai/api/v1"
        
        self.model = ChatOpenAI(
            model_name=config.model_name,
            temperature=config.temperature,
            openai_api_key=api_key,
            max_tokens=config.max_tokens,
            openai_api_base=base_url,
            **config.additional_config
        )
    
    async def generate(self, prompt: str) -> str:
        messages = [HumanMessage(content=prompt)]
        response = await self.model.agenerate([messages])
        return response.generations[0][0].text
    
    def get_available_models(self) -> List[str]:
        return [
            "openai/gpt-4-turbo",
            "anthropic/claude-3-opus",
            "google/gemini-pro",
            "meta-llama/llama-2-70b-chat",
            "mistral/mistral-large",
            "deepseek/deepseek-coder",
        ]

class LLMProviderManager:
    """Manages LLM providers and configurations"""
    
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {
            "openai": OpenAIProvider(),
            "gemini": GeminiProvider(),
            "vertexai": VertexAIProvider(),
            "anthropic": AnthropicProvider(),
            "openrouter": OpenRouterProvider()
        }
        self.agent_configs: Dict[str, LLMProviderConfig] = self.get_all_agent_configs()

    def get_provider(self, provider_name: str) -> Optional[BaseLLMProvider]:
        """Get provider by name"""
        return self.providers.get(provider_name)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    def get_available_models(self, provider_name: str) -> List[str]:
        """Get available models for a provider"""
        provider = self.get_provider(provider_name)
        if provider:
            return provider.get_available_models()
        return []
    
    def configure_agent_llm(self, agent_name: str, config: LLMProviderConfig) -> bool:
        """Configure LLM for an agent"""
        try:
            provider = self.get_provider(config.provider_name)
            if provider:
                provider.initialize_model(config)
                self.agent_configs[agent_name] = config

                # Save to file
                all_configs = self.get_all_agent_configs()
                all_configs[agent_name] = config.dict()  # Convert to dict for saving
                with open("src/backend/config/llm_configs.yaml", "w") as f:
                    yaml.dump(all_configs, f)

                return True
            return False
        except Exception as e:
            print(f"Error configuring LLM for agent {agent_name}: {e}")
            return False
    
    def get_agent_config(self, agent_name: str) -> Optional[LLMProviderConfig]:
        """Get LLM configuration for an agent"""
        return self.agent_configs.get(agent_name)
    
    def update_agent_config(self, agent_name: str, updates: Dict[str, Any]) -> bool:
        """Update LLM configuration for an agent"""
        if agent_name in self.agent_configs:
            config = self.agent_configs[agent_name]
            new_config = config.copy(update=updates)
            return self.configure_agent_llm(agent_name, new_config)
        return False

    async def generate_with_agent_llm(self, agent_name: str, prompt: str) -> Optional[str]:
        """Generate response using agent's configured LLM"""
        config = self.get_agent_config(agent_name)
        if config:
            provider = self.get_provider(config.provider_name)
            if provider:
                return await provider.generate(prompt)
        return None

    def get_all_agent_configs(self) -> Dict[str, LLMProviderConfig]:
        """Get all agent LLM configurations."""
        try:
            with open("src/backend/config/llm_configs.yaml", "r") as f:
                configs = yaml.safe_load(f)
                if configs:
                  # Convert to LLMProviderConfig objects
                  return {
                      agent_name: LLMProviderConfig(**config)
                      for agent_name, config in configs.items()
                  }
                else:
                  return {}
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"Error loading LLM configs: {e}")
            return {}
