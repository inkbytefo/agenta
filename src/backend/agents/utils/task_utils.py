from typing import Dict, Any, Optional, List
from enum import Enum
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Enumeration of different task types"""
    CODE_MODIFICATION = "modification"
    CODE_CREATION = "creation"
    DOCUMENTATION = "documentation"
    REVIEW = "review"
    TEST = "test"
    PLANNING = "planning"
    PROMPT = "prompt"

@dataclass
class TaskTemplate:
    """Template for task description and expected output"""
    description_template: str
    output_template: str
    steps: List[str]

class TaskDetector(ABC):
    """Abstract base class for task type detection"""
    
    @abstractmethod
    def detect_type(self, description: str) -> TaskType:
        """Detect task type from description"""
        pass

class TaskFormatter:
    """Utility class for formatting task descriptions and outputs"""
    
    @staticmethod
    def format_description(template: str, base_description: str, steps: List[str]) -> str:
        """Format task description with steps"""
        steps_text = "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))
        return template.format(
            description=base_description,
            steps=steps_text
        ).strip()

    @staticmethod
    def format_output_template(template: str, requirements: List[str]) -> str:
        """Format expected output with requirements"""
        reqs_text = "\n".join(f"{i+1}. {req}" for i, req in enumerate(requirements))
        return template.format(requirements=reqs_text).strip()

class CodeTaskDetector(TaskDetector):
    """Task type detector for code-related tasks"""
    
    MODIFICATION_KEYWORDS = ['modify', 'update', 'change', 'fix', 'refactor', 'improve']
    
    def detect_type(self, description: str) -> TaskType:
        """Detect if task is code modification or creation"""
        description_lower = description.lower()
        if any(keyword in description_lower for keyword in self.MODIFICATION_KEYWORDS):
            return TaskType.CODE_MODIFICATION
        return TaskType.CODE_CREATION

class TaskTemplateManager:
    """Manager for task templates"""
    
    _templates: Dict[TaskType, TaskTemplate] = {
        TaskType.CODE_MODIFICATION: TaskTemplate(
            description_template="""
            Code Modification Task:
            {description}
            
            Steps to complete:
            {steps}
            """,
            output_template="""
            Expected deliverables:
            {requirements}
            """,
            steps=[
                "Analyze existing code",
                "Plan necessary modifications",
                "Implement changes following best practices",
                "Ensure backwards compatibility",
                "Add or update comments as needed"
            ]
        ),
        TaskType.CODE_CREATION: TaskTemplate(
            description_template="""
            New Code Implementation Task:
            {description}
            
            Steps to complete:
            {steps}
            """,
            output_template="""
            Expected deliverables:
            {requirements}
            """,
            steps=[
                "Plan the implementation",
                "Write clean, maintainable code",
                "Follow project standards",
                "Include proper documentation",
                "Consider edge cases and error handling"
            ]
        )
    }
    
    @classmethod
    def get_template(cls, task_type: TaskType) -> TaskTemplate:
        """Get template for specified task type"""
        if task_type not in cls._templates:
            raise ValueError(f"No template found for task type: {task_type}")
        return cls._templates[task_type]

class ResponseFormatter:
    """Utility class for formatting agent responses"""
    
    @staticmethod
    def format_success(result: Any, task_type: Optional[TaskType] = None) -> Dict[str, Any]:
        """Format successful response"""
        response = {
            'status': 'success',
            'result': result
        }
        if task_type:
            response['type'] = task_type.value
        return response
    
    @staticmethod
    def format_error(error: Exception, context: str = "") -> Dict[str, Any]:
        """Format error response"""
        error_message = f"{context}: {str(error)}" if context else str(error)
        logger.error(error_message, exc_info=True)
        return {
            'status': 'error',
            'error': error_message
        }

class TaskValidationMixin:
    """Mixin for task validation functionality"""
    
    @staticmethod
    def validate_task_description(description: str) -> None:
        """Validate task description"""
        if not description or not description.strip():
            raise ValueError("Task description cannot be empty")
        if len(description) < 10:
            raise ValueError("Task description is too short")

    @staticmethod
    def validate_expected_output(output: str) -> None:
        """Validate expected output"""
        if not output or not output.strip():
            raise ValueError("Expected output cannot be empty")