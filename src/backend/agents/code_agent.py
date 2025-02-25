from crewai import Task
from typing import Dict, Any, Optional, cast
from .base_agent import VSCodeAgent
from .utils.task_utils import (
    TaskType,
    CodeTaskDetector,
    TaskTemplateManager,
    ResponseFormatter,
    TaskValidationMixin
)

class CodeAgent(VSCodeAgent, TaskValidationMixin):
    """Code implementation agent responsible for writing and modifying code.
    
    This agent handles code-related tasks including:
    - Creating new code implementations
    - Modifying existing code
    - Ensuring code quality and standards
    - Handling code-specific error cases
    
    Attributes:
        name (str): The name of the agent
        project_path (str): Path to the project directory
        task_detector (CodeTaskDetector): Detector for code task types
    """

    def __init__(self, name: str, project_path: str, config_path: Optional[str] = None) -> None:
        """Initialize the code agent.
        
        Args:
            name: Name of the agent (used to load config)
            project_path: Path to the project directory
            config_path: Optional path to agents.yaml config file
            
        Raises:
            ValueError: If name or project_path is invalid
        """
        super().__init__(name, project_path, config_path)
        self.task_detector = CodeTaskDetector()
        self.logger.info(f"Initialized CodeAgent: {name}")

    async def execute(self, task: Task) -> Dict[str, Any]:
        """Execute a code-related task using CrewAI's task system.
        
        This method:
        1. Validates the task description
        2. Detects the type of code task
        3. Creates a specific task with appropriate templates
        4. Executes the task with proper error handling
        
        Args:
            task: CrewAI Task object with task details
            
        Returns:
            Dict containing execution result and status
            
        Raises:
            ValueError: If task validation fails
        """
        try:
            # Validate task
            self.validate_task_description(task.description)
            
            # Detect task type
            task_type = self.task_detector.detect_type(task.description)
            template = TaskTemplateManager.get_template(task_type)
            
            # Create specific task with templated description and output
            execution_task = self.create_task(
                description=template.description_template.format(
                    description=task.description,
                    steps="\n".join(template.steps)
                ),
                expected_output=template.output_template.format(
                    requirements=[
                        "Successfully implemented/modified code meeting requirements",
                        "Proper error handling and edge case coverage",
                        "Clear documentation and comments",
                        "Tests if applicable",
                        "No regressions or breaking changes"
                    ]
                )
            )
            
            # Execute the task using CrewAI's system
            result = await super().execute(execution_task)
            
            # Format and return response
            return ResponseFormatter.format_success(
                result=cast(Dict[str, Any], result).get('result'),
                task_type=task_type
            )
            
        except ValueError as ve:
            self.logger.error(f"Validation error in code task: {ve}")
            return ResponseFormatter.format_error(ve, "Task validation failed")
            
        except Exception as e:
            self.logger.error(f"Error executing code task: {e}", exc_info=True)
            return ResponseFormatter.format_error(e, "Code implementation failed")

    def validate_code_output(self, output: str) -> None:
        """Validate code output for common issues.
        
        Args:
            output: The code output to validate
            
        Raises:
            ValueError: If output validation fails
        """
        if not output:
            raise ValueError("Code output cannot be empty")
            
        # Add additional code-specific validation as needed
        # For example, check for syntax errors, style violations, etc.
