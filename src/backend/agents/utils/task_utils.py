from typing import Dict, Any, Optional, List, Type
from enum import Enum
import logging
import re
import ast
from dataclasses import dataclass
from abc import ABC, abstractmethod
from functools import lru_cache
from datetime import datetime

logger = logging.getLogger(__name__)

class TaskError(Exception):
    """Base exception class for task-related errors"""
    pass

class ValidationError(TaskError):
    """Exception raised for task validation errors"""
    pass

class SecurityError(TaskError):
    """Exception raised for security-related errors"""
    pass


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
        if not description:
            raise ValidationError("Task description cannot be empty")
        return self._analyze_description(description)
    
    @abstractmethod
    def _analyze_description(self, description: str) -> TaskType:
        """Analyze task description to determine type"""
        pass
    
    @staticmethod
    def validate_description(description: str) -> None:
        """Validate task description format and content"""
        if not description or len(description.strip()) < 10:
            raise ValidationError("Task description must be at least 10 characters")
        if len(description) > 1000:
            raise ValidationError("Task description is too long (max 1000 chars)")

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
    """Task type detector for code-related tasks with advanced pattern matching"""
    
    TASK_PATTERNS = {
        TaskType.CODE_MODIFICATION: [
            (r'\b(modify|update|change|fix|refactor|improve)\b', 2),
            (r'\b(bug|issue|error|problem)\b', 1),
            (r'\b(optimization|performance|security)\b', 1)
        ],
        TaskType.CODE_CREATION: [
            (r'\b(create|new|implement|add|build)\b', 2),
            (r'\b(from scratch|initialize|start)\b', 1),
            (r'\b(feature|functionality|component)\b', 1)
        ]
    }
    
    def __init__(self):
        """Initialize with compiled regex patterns"""
        super().__init__()
        self._pattern_cache = {}
        for task_type, patterns in self.TASK_PATTERNS.items():
            self._pattern_cache[task_type] = [
                (re.compile(pattern, re.IGNORECASE), weight)
                for pattern, weight in patterns
            ]
    
    @lru_cache(maxsize=1000)
    def _analyze_description(self, description: str) -> TaskType:
        """Analyze task description using weighted pattern matching"""
        self.validate_description(description)
        
        scores = {task_type: 0 for task_type in TaskType}
        for task_type, patterns in self._pattern_cache.items():
            for pattern, weight in patterns:
                matches = pattern.findall(description)
                scores[task_type] += len(matches) * weight
        
        # Get task type with highest score or default to creation
        max_score = max(scores.values())
        if max_score == 0:
            return TaskType.CODE_CREATION
            
        # If tie, prefer modification as it's more specific
        max_types = [t for t, s in scores.items() if s == max_score]
        return (TaskType.CODE_MODIFICATION if TaskType.CODE_MODIFICATION in max_types
                else max_types[0])

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
    """Mixin for task validation functionality with enhanced security checks"""
    
    MAX_DESCRIPTION_LENGTH = 1000
    MAX_OUTPUT_LENGTH = 5000
    SECURITY_PATTERNS = [
        r'rm\s+-rf',
        r'system\s*\(',
        r'exec\s*\(',
        r'eval\s*\(',
        r'__import__\s*\(',
        r'subprocess\..*',
        r'os\.(system|popen|spawn)',
    ]
    
    @classmethod
    def validate_task_description(cls, description: str) -> None:
        """Validate task description with comprehensive checks"""
        if not description or not description.strip():
            raise ValidationError("Task description cannot be empty")
        if len(description) < 10:
            raise ValidationError("Task description is too short")
        if len(description) > cls.MAX_DESCRIPTION_LENGTH:
            raise ValidationError(f"Task description exceeds maximum length of {cls.MAX_DESCRIPTION_LENGTH}")
            
        # Check for potentially malicious patterns
        cls._check_security_patterns(description)
    
    @classmethod
    def validate_expected_output(cls, output: str) -> None:
        """Validate expected output with comprehensive checks"""
        if not output or not output.strip():
            raise ValidationError("Expected output cannot be empty")
        if len(output) > cls.MAX_OUTPUT_LENGTH:
            raise ValidationError(f"Expected output exceeds maximum length of {cls.MAX_OUTPUT_LENGTH}")
        
        # Check for potentially malicious patterns
        cls._check_security_patterns(output)
    
    @classmethod
    def validate_code_output(cls, code: str) -> None:
        """Validate code output for security and syntax"""
        if not code or not code.strip():
            raise ValidationError("Code output cannot be empty")
            
        # Check for potentially malicious patterns
        cls._check_security_patterns(code)
        
        # Validate Python syntax
        try:
            ast.parse(code)
        except SyntaxError as e:
            raise ValidationError(f"Invalid Python syntax: {str(e)}")
    
    @classmethod
    def _check_security_patterns(cls, content: str) -> None:
        """Check content for potentially malicious patterns"""
        for pattern in cls.SECURITY_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                raise SecurityError(f"Potentially unsafe pattern detected: {pattern}")