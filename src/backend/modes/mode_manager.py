from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel

class AgentMode(Enum):
    PLAN = "plan"
    ACT = "act"

class ModeConfig(BaseModel):
    """Configuration for different modes"""
    allow_file_operations: bool
    allow_execution: bool
    require_confirmation: bool
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None

class ModeManager:
    """Manages agent operation modes"""
    
    def __init__(self):
        self.current_mode = AgentMode.PLAN
        self.mode_configs = {
            AgentMode.PLAN: ModeConfig(
                allow_file_operations=False,
                allow_execution=False,
                require_confirmation=True,
                temperature=0.8,  # Higher temperature for creative planning
                max_tokens=1000
            ),
            AgentMode.ACT: ModeConfig(
                allow_file_operations=True,
                allow_execution=True,
                require_confirmation=False,
                temperature=0.7,  # Lower temperature for precise execution
                max_tokens=2000
            )
        }
        self.mode_descriptions = {
            AgentMode.PLAN: """
            Plan Mode:
            - Analyze requirements and constraints
            - Design solutions and architectures
            - Create execution strategies
            - No file modifications or executions
            - Requires user confirmation to proceed
            """,
            AgentMode.ACT: """
            Act Mode:
            - Execute planned actions
            - Modify files and systems
            - Run tests and validations
            - Implement solutions
            - Autonomous operation within constraints
            """
        }
        
    def get_current_mode(self) -> AgentMode:
        """Get current operation mode"""
        return self.current_mode
    
    def switch_mode(self, mode: AgentMode) -> Dict[str, Any]:
        """Switch between operation modes"""
        if mode == self.current_mode:
            return {
                'status': 'info',
                'message': f'Already in {mode.value} mode'
            }
            
        self.current_mode = mode
        return {
            'status': 'success',
            'message': f'Switched to {mode.value} mode',
            'description': self.mode_descriptions[mode],
            'config': self.mode_configs[mode].dict()
        }
    
    def get_mode_config(self) -> ModeConfig:
        """Get configuration for current mode"""
        return self.mode_configs[self.current_mode]
    
    def is_operation_allowed(self, operation_type: str) -> bool:
        """Check if an operation type is allowed in current mode"""
        config = self.mode_configs[self.current_mode]
        
        if operation_type == 'file':
            return config.allow_file_operations
        elif operation_type == 'execute':
            return config.allow_execution
        
        return False
    
    def requires_confirmation(self) -> bool:
        """Check if current mode requires user confirmation"""
        return self.mode_configs[self.current_mode].require_confirmation
    
    def get_mode_description(self) -> str:
        """Get description of current mode"""
        return self.mode_descriptions[self.current_mode]
    
    def get_llm_settings(self) -> Dict[str, Any]:
        """Get LLM settings for current mode"""
        config = self.mode_configs[self.current_mode]
        return {
            'temperature': config.temperature,
            'max_tokens': config.max_tokens
        }

    def update_mode_config(self, mode: AgentMode, updates: Dict[str, Any]) -> None:
        """Update configuration for a specific mode"""
        current_config = self.mode_configs[mode]
        new_config = current_config.copy(update=updates)
        self.mode_configs[mode] = new_config
