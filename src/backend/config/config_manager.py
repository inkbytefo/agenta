"""
Configuration management module with schema validation and centralized configuration handling.
"""
import os
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field, validator
import logging
from ratelimit import limits, RateLimitException
from functools import wraps

logger = logging.getLogger(__name__)

class LLMConfig(BaseModel):
    """LLM provider configuration schema"""
    provider_name: str
    model_name: str
    temperature: float = Field(ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(ge=1, default=None)
    api_key: Optional[str] = None
    
    @validator('api_key')
    def validate_api_key(cls, v, values):
        """Validate API key is set either in config or environment"""
        if not v:
            env_var = f"{values['provider_name'].upper()}_API_KEY"
            if not os.getenv(env_var):
                logger.warning(f"No API key provided for {values['provider_name']} in config or environment")
        return v

class AgentConfig(BaseModel):
    """Agent configuration schema"""
    role: str
    goal: str
    backstory: str
    verbose: bool = True
    allow_delegation: bool = False
    max_iter: int = Field(ge=1, le=100, default=15)
    max_retry_limit: int = Field(ge=1, le=10, default=3)
    llm: Optional[LLMConfig] = None

class RateLimitConfig(BaseModel):
    """Rate limiting configuration schema"""
    max_requests_per_minute: int = Field(ge=1, default=60)
    max_tokens_per_minute: int = Field(ge=1, default=100000)
    retry_attempts: int = Field(ge=0, default=3)
    retry_delay: float = Field(ge=0.1, default=1.0)

@dataclass
class ConfigurationError(Exception):
    """Configuration related errors"""
    message: str
    details: Optional[Dict[str, Any]] = None

class ConfigManager:
    """Centralized configuration management with schema validation"""
    
    def __init__(self, config_dir: str):
        """Initialize configuration manager
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = config_dir
        self.agent_configs: Dict[str, AgentConfig] = {}
        self.rate_limit_config = self._load_rate_limits()
        self._load_agent_configs()

    def _load_rate_limits(self) -> RateLimitConfig:
        """Load rate limiting configuration"""
        try:
            path = os.path.join(self.config_dir, 'rate_limits.yaml')
            if os.path.exists(path):
                with open(path, 'r') as f:
                    config = yaml.safe_load(f)
                return RateLimitConfig(**config)
            return RateLimitConfig()  # Use defaults
        except Exception as e:
            logger.error(f"Error loading rate limits: {e}")
            return RateLimitConfig()  # Use defaults

    def _load_agent_configs(self) -> None:
        """Load and validate agent configurations"""
        try:
            path = os.path.join(self.config_dir, 'agents.yaml')
            if not os.path.exists(path):
                raise ConfigurationError(f"Configuration file not found: {path}")
                
            with open(path, 'r') as f:
                configs = yaml.safe_load(f)
                
            for name, config in configs.items():
                try:
                    self.agent_configs[name] = AgentConfig(**config)
                except Exception as e:
                    logger.error(f"Error validating config for agent {name}: {e}")
                    raise ConfigurationError(
                        f"Invalid configuration for agent {name}",
                        details={"error": str(e), "config": config}
                    )
                    
        except Exception as e:
            logger.error(f"Error loading agent configurations: {e}")
            raise ConfigurationError("Failed to load agent configurations", details={"error": str(e)})

    def get_agent_config(self, agent_name: str) -> AgentConfig:
        """Get configuration for specified agent
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            AgentConfig for the specified agent
            
        Raises:
            ConfigurationError: If agent configuration is not found
        """
        if agent_name not in self.agent_configs:
            raise ConfigurationError(f"Configuration not found for agent: {agent_name}")
        return self.agent_configs[agent_name]

    def rate_limit_decorator(self, func):
        """Decorator to apply rate limiting to a function
        
        Args:
            func: Function to decorate
            
        Returns:
            Decorated function with rate limiting
        """
        period = 60  # 1 minute in seconds
        max_requests = self.rate_limit_config.max_requests_per_minute

        @limits(calls=max_requests, period=period)
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except RateLimitException:
                logger.warning(f"Rate limit exceeded for {func.__name__}")
                raise ConfigurationError(
                    "Rate limit exceeded",
                    details={
                        "max_requests": max_requests,
                        "period": period,
                        "function": func.__name__
                    }
                )
        return wrapper

# Global configuration manager instance
config_manager: Optional[ConfigManager] = None

def init_config_manager(config_dir: str) -> ConfigManager:
    """Initialize global configuration manager
    
    Args:
        config_dir: Directory containing configuration files
        
    Returns:
        ConfigManager instance
    """
    global config_manager
    if not config_manager:
        config_manager = ConfigManager(config_dir)
    return config_manager

def get_config_manager() -> ConfigManager:
    """Get global configuration manager instance
    
    Returns:
        ConfigManager instance
        
    Raises:
        ConfigurationError: If configuration manager is not initialized
    """
    if not config_manager:
        raise ConfigurationError("Configuration manager not initialized")
    return config_manager