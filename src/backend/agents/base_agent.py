from crewai import Agent, Task
from crewai.project import CrewBase
from typing import Dict, Any, List, Optional
from ..llm.providers import LLMProviderManager, LLMProviderConfig
import yaml
import os
from pathlib import Path

class VSCodeAgent(Agent):
    """Base class for all VSCode agents using CrewAI framework"""

    def __init__(self, name: str, project_path: str, config_path: Optional[str] = None):
        """Initialize the VSCode agent with configuration

        Args:
            name: Name of the agent (used to load config)
            project_path: Path to the project directory
            config_path: Optional path to agents.yaml config file
        """
        super().__init__()
        self.name = name
        self.project_path = project_path
        
        # Initialize LLM provider manager
        self.llm_manager = LLMProviderManager()
        
        # Load agent configuration
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'agents.yaml')
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            if name not in config:
                raise ValueError(f"Agent {name} not found in configuration")
            self.config = config[name]

        # Initialize CrewAI agent with configuration
        self._initialize_agent()
        
        # Initialize tools
        self.tools = []

    def _initialize_agent(self) -> None:
        """Initialize or reinitialize the CrewAI agent with current configuration"""
        # Get LLM configuration if available
        llm_config = self.llm_manager.get_agent_config(self.name)
        
        if llm_config:
            # Get the configured LLM provider
            provider = self.llm_manager.get_provider(llm_config.provider_name)
            if provider:
                provider.initialize_model(llm_config)
                llm = provider.model
            else:
                llm = None
        else:
            llm = None

        # Initialize CrewAI agent
        self.agent = Agent(
            role=self.config['role'],
            goal=self.config['goal'],
            backstory=self.config['backstory'],
            verbose=self.config.get('verbose', True),
            allow_delegation=self.config.get('allow_delegation', False),
            max_iter=self.config.get('max_iter', 15),
            max_retry_limit=self.config.get('max_retry_limit', 3),
            memory=True,  # Use CrewAI's built-in memory
            respect_context_window=True,
            llm=llm  # Use configured LLM if available
        )
        
        # Reattach tools if any
        if self.tools:
            self.agent.tools = self.tools

    def add_tool(self, tool: Any) -> None:
        """Add a tool to the agent's toolkit"""
        self.tools.append(tool)
        self.agent.tools = self.tools

    def create_task(self, description: str, expected_output: str) -> Task:
        """Create a task for this agent
        
        Args:
            description: Detailed description of what needs to be done
            expected_output: What the task should produce
            
        Returns:
            Task: A CrewAI Task object
        """
        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.agent
        )

    async def execute(self, task: Task) -> Dict[str, Any]:
        """Execute a CrewAI task
        
        Args:
            task: Task to execute
            
        Returns:
            Dict containing the task result and status
        """
        try:
            result = await self.agent.execute(task)
            return {
                'status': 'success',
                'result': result
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def configure_llm(self, config: LLMProviderConfig) -> bool:
        """Configure the LLM for this agent
        
        Args:
            config: LLM provider configuration
            
        Returns:
            bool: True if configuration was successful
        """
        try:
            if self.llm_manager.configure_agent_llm(self.name, config):
                self._initialize_agent()  # Reinitialize agent with new LLM
                return True
            return False
        except Exception as e:
            print(f"Error configuring LLM for {self.name}: {e}")
            return False

    def get_llm_config(self) -> Optional[LLMProviderConfig]:
        """Get current LLM configuration for this agent"""
        return self.llm_manager.get_agent_config(self.name)

    def get_available_providers(self) -> List[str]:
        """Get list of available LLM providers"""
        return self.llm_manager.get_available_providers()

    def get_available_models(self, provider_name: str) -> List[str]:
        """Get available models for a provider"""
        return self.llm_manager.get_available_models(provider_name)
