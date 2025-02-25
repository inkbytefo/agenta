"""Base agent class for VSCode integration with CrewAI framework."""

from crewai import Agent, Task
from crewai.project import CrewBase
from typing import Dict, Any, List, Optional, Union
import os
import logging
from ..llm.providers import LLMProviderManager, LLMProviderConfig
from ..config.config_manager import (
    get_config_manager,
    ConfigurationError,
    AgentConfig,
    init_config_manager
)

class AgentError(Exception):
    """Base class for agent-related errors"""
    pass

class AgentConfigError(AgentError):
    """Error in agent configuration"""
    pass

class AgentExecutionError(AgentError):
    """Error during agent execution"""
    pass

class InputValidationError(AgentError):
    """Error in input validation"""
    pass

class VSCodeAgent(Agent):
    """Base class for all VSCode agents using CrewAI framework.
    
    This class provides:
    - Configuration management
    - Rate limiting
    - Input/output validation
    - Error handling
    - Logging
    
    Attributes:
        name (str): Name of the agent
        project_path (str): Path to the project directory
        config (AgentConfig): Validated agent configuration
        logger (logging.Logger): Agent-specific logger
    """

    def __init__(self, name: str, project_path: str, config_path: Optional[str] = None) -> None:
        """Initialize the VSCode agent with configuration.
        
        Args:
            name: Name of the agent (used to load config)
            project_path: Path to the project directory
            config_path: Optional path to configuration directory
            
        Raises:
            AgentConfigError: If configuration is invalid
            ValueError: If name or project_path is invalid
        """
        if not name or not isinstance(name, str):
            raise ValueError("Agent name must be a non-empty string")
            
        if not os.path.exists(project_path):
            raise ValueError(f"Project path does not exist: {project_path}")

        super().__init__()
        self.name = name
        self.project_path = project_path
        
        # Setup logging
        self.logger = logging.getLogger(f"agent.{name}")
        
        # Initialize configuration
        try:
            config_dir = os.path.dirname(config_path) if config_path else os.path.join(
                os.path.dirname(__file__), '..', 'config'
            )
            init_config_manager(config_dir)
            self.config = self._load_configuration()
            self.logger.info(f"Successfully initialized agent: {name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize agent: {e}")
            raise AgentConfigError(f"Failed to initialize agent: {e}")
        
        # Initialize LLM provider manager
        self.llm_manager = LLMProviderManager()
        
        # Initialize CrewAI agent with configuration
        self._initialize_agent()
        
        # Initialize tools
        self.tools: List[Any] = []

    def _load_configuration(self) -> AgentConfig:
        """Load and validate agent configuration.
        
        Returns:
            Validated AgentConfig instance
            
        Raises:
            AgentConfigError: If configuration is invalid or missing
        """
        try:
            return get_config_manager().get_agent_config(self.name)
        except ConfigurationError as e:
            raise AgentConfigError(str(e))

    def _initialize_agent(self) -> None:
        """Initialize or reinitialize the CrewAI agent with current configuration.
        
        Raises:
            AgentConfigError: If LLM configuration fails
        """
        try:
            # Get LLM configuration if available
            llm_config = self.llm_manager.get_agent_config(self.name)
            llm = None
            
            if llm_config:
                # Get the configured LLM provider
                provider = self.llm_manager.get_provider(llm_config.provider_name)
                if provider:
                    provider.initialize_model(llm_config)
                    llm = provider.model
                    self.logger.info(f"Initialized LLM provider: {llm_config.provider_name}")
                else:
                    self.logger.warning(f"LLM provider not found: {llm_config.provider_name}")

            # Initialize CrewAI agent with validated configuration
            self.agent = Agent(
                role=self.config.role,
                goal=self.config.goal,
                backstory=self.config.backstory,
                verbose=self.config.verbose,
                allow_delegation=self.config.allow_delegation,
                max_iter=self.config.max_iter,
                max_retry_limit=self.config.max_retry_limit,
                memory=True,  # Use CrewAI's built-in memory
                respect_context_window=True,
                llm=llm  # Use configured LLM if available
            )
            
            # Reattach tools if any
            if self.tools:
                self.agent.tools = self.tools
                
            self.logger.info("Agent initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing agent: {e}")
            raise AgentConfigError(f"Error initializing agent: {e}")

    @get_config_manager().rate_limit_decorator
    async def execute(self, task: Task) -> Dict[str, Any]:
        """Execute a CrewAI task with rate limiting and validation.
        
        Args:
            task: Task to execute
            
        Returns:
            Dict containing the task result and status
            
        Raises:
            InputValidationError: If task is invalid
            AgentExecutionError: If execution fails
        """
        if not task:
            raise InputValidationError("Task cannot be None")
            
        if not task.description or not task.description.strip():
            raise InputValidationError("Task description cannot be empty")
            
        try:
            self.logger.info(f"Executing task: {task.description[:100]}...")
            result = await self.agent.execute(task)
            
            # Validate output
            if not result or not isinstance(result, (str, dict)):
                raise AgentExecutionError("Invalid output format from agent")
                
            self.logger.info("Task executed successfully")
            return {
                'status': 'success',
                'result': result
            }
        except Exception as e:
            self.logger.error(f"Error executing task: {e}")
            raise AgentExecutionError(f"Task execution failed: {e}")

    def add_tool(self, tool: Any) -> None:
        """Add a tool to the agent's toolkit.
        
        Args:
            tool: Tool instance to add
            
        Raises:
            InputValidationError: If tool is invalid
        """
        if tool is None:
            raise InputValidationError("Tool cannot be None")
            
        self.tools.append(tool)
        self.agent.tools = self.tools
        self.logger.info(f"Added tool: {tool.__class__.__name__}")

    def create_task(self, description: str, expected_output: str) -> Task:
        """Create a task for this agent.
        
        Args:
            description: Detailed description of what needs to be done
            expected_output: What the task should produce
            
        Returns:
            Task: A CrewAI Task object
            
        Raises:
            InputValidationError: If description or expected_output is invalid
        """
        if not description or not expected_output:
            raise InputValidationError("Task description and expected output are required")
            
        self.logger.info(f"Creating task: {description[:100]}...")
        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.agent
        )

    def configure_llm(self, config: LLMProviderConfig) -> bool:
        """Configure the LLM for this agent.
        
        Args:
            config: LLM provider configuration
            
        Returns:
            bool: True if configuration was successful
            
        Raises:
            AgentConfigError: If LLM configuration fails
        """
        if not config:
            raise InputValidationError("LLM configuration cannot be None")
            
        try:
            self.logger.info(f"Configuring LLM with provider: {config.provider_name}")
            if self.llm_manager.configure_agent_llm(self.name, config):
                self._initialize_agent()  # Reinitialize agent with new LLM
                self.logger.info("LLM configuration successful")
                return True
            self.logger.warning("LLM configuration failed")
            return False
        except Exception as e:
            self.logger.error(f"Error configuring LLM: {e}")
            raise AgentConfigError(f"Error configuring LLM: {e}")

    def get_llm_config(self) -> Optional[LLMProviderConfig]:
        """Get current LLM configuration for this agent.
        
        Returns:
            Optional[LLMProviderConfig]: Current LLM configuration if available
        """
        try:
            return self.llm_manager.get_agent_config(self.name)
        except Exception as e:
            self.logger.error(f"Error getting LLM config: {e}")
            return None

    def get_available_providers(self) -> List[str]:
        """Get list of available LLM providers.
        
        Returns:
            List[str]: Available provider names
        """
        try:
            return self.llm_manager.get_available_providers()
        except Exception as e:
            self.logger.error(f"Error getting available providers: {e}")
            return []

    def get_available_models(self, provider_name: str) -> List[str]:
        """Get available models for a provider.
        
        Args:
            provider_name: Name of the LLM provider
            
        Returns:
            List[str]: Available model names
            
        Raises:
            InputValidationError: If provider_name is invalid
        """
        if not provider_name:
            raise InputValidationError("Provider name cannot be empty")
            
        try:
            return self.llm_manager.get_available_models(provider_name)
        except Exception as e:
            self.logger.error(f"Error getting available models for {provider_name}: {e}")
            return []
