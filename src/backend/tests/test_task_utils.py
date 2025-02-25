"""
Unit tests for task utility classes and functions.

This test suite covers:
- Task type detection
- Task formatting
- Response formatting
- Template management
- Input validation
- Rate limiting functionality
"""

import pytest
from typing import Dict, Any, List
from datetime import datetime
import re
from ..agents.utils.task_utils import (
    TaskType,
    CodeTaskDetector,
    TaskFormatter,
    ResponseFormatter,
    TaskTemplateManager,
    TaskValidationMixin,
    TaskTemplate,
    ConfigurationError,
    ValidationError,
    SecurityError
)

# Test Data

@pytest.fixture
def sample_templates() -> Dict[TaskType, TaskTemplate]:
    """Provide sample task templates for testing.
    
    Returns:
        Dict mapping TaskType to TaskTemplate
    """
    return {
        TaskType.CODE_MODIFICATION: TaskTemplate(
            description_template="Modify: {description}\n\nSteps:\n{steps}",
            output_template="Expected:\n{requirements}",
            steps=["Analyze", "Plan", "Modify", "Test"]
        ),
        TaskType.CODE_CREATION: TaskTemplate(
            description_template="Create: {description}\n\nSteps:\n{steps}",
            output_template="Expected:\n{requirements}",
            steps=["Design", "Implement", "Document", "Test"]
        )
    }

@pytest.fixture
def sample_steps() -> List[str]:
    """Provide sample task steps.
    
    Returns:
        List of task step strings
    """
    return [
        "Step 1: Analysis",
        "Step 2: Implementation",
        "Step 3: Testing"
    ]

class TestCodeTaskDetector:
    """Test suite for CodeTaskDetector class with pattern weights and caching"""
    
    @pytest.fixture
    def detector(self) -> CodeTaskDetector:
        """Provide CodeTaskDetector instance."""
        return CodeTaskDetector()
    
    @pytest.mark.parametrize("description,expected_type", [
        # Basic patterns with high weights (2)
        ("Modify the login function", TaskType.CODE_MODIFICATION),
        ("Create a new API endpoint", TaskType.CODE_CREATION),
        
        # Multiple patterns with weights
        ("Fix bug in performance optimization", TaskType.CODE_MODIFICATION),  # 2 + 1 + 1
        ("Create new feature from scratch", TaskType.CODE_CREATION),  # 2 + 1
        
        # Competing patterns
        ("Fix and create authentication component", TaskType.CODE_MODIFICATION),  # Modification wins with higher weight
        ("Initialize new feature with bug fixes", TaskType.CODE_CREATION),  # Creation wins with explicit 'new'
        
        # Context-based patterns
        ("Address security issue in API", TaskType.CODE_MODIFICATION),  # 'security' implies modification
        ("Start implementing performance improvements", TaskType.CODE_MODIFICATION),  # 'performance' suggests modification
    ])
    def test_detect_type(
        self,
        detector: CodeTaskDetector,
        description: str,
        expected_type: TaskType
    ) -> None:
        """Test task type detection with weighted patterns."""
        assert detector.detect_type(description) == expected_type

    def test_detect_type_edge_cases(self, detector: CodeTaskDetector) -> None:
        """Test task type detection with edge cases."""
        with pytest.raises(ValidationError):
            detector.detect_type("")
        
        # Test pattern weighting system
        result = detector.detect_type("Create by modifying existing code")
        assert result == TaskType.CODE_MODIFICATION  # 'modify' (2) outweighs 'create' (2) due to modification preference
        
        # Test cache behavior
        description = "Implement new feature with optimizations"
        first_result = detector.detect_type(description)
        second_result = detector.detect_type(description)
        assert first_result == second_result  # Results should be consistent
        
        # Test max length validation
        with pytest.raises(ValidationError):
            detector.detect_type("a" * 1001)  # Exceeds max length

class TestTaskFormatter:
    """Test suite for TaskFormatter class"""
    
    @pytest.fixture
    def template(self) -> str:
        """Provide sample template string."""
        return """
        Task: {description}
        
        Steps:
        {steps}
        """
    
    def test_format_description(self, template: str, sample_steps: List[str]) -> None:
        """Test description formatting with steps.
        
        Args:
            template: Template string
            sample_steps: List of task steps
        """
        description = "Test task"
        result = TaskFormatter.format_description(template, description, sample_steps)
        
        # Verify structure
        assert description in result
        for step in sample_steps:
            assert step in result
        assert "Steps:" in result
        
        # Verify formatting
        assert result.strip().startswith("Task:")
        assert all(str(i+1) in result for i in range(len(sample_steps)))
    
    def test_format_output_template(self) -> None:
        """Test output template formatting."""
        template = "Expected:\n{requirements}"
        requirements = ["Clean code", "Documentation", "Tests"]
        
        result = TaskFormatter.format_output_template(template, requirements)
        
        # Verify content
        assert "Expected:" in result
        for req in requirements:
            assert req in result
            
        # Verify numbering
        assert all(f"{i+1}. " in result for i in range(len(requirements)))

class TestResponseFormatter:
    """Test suite for ResponseFormatter class"""
    
    def test_format_success(self) -> None:
        """Test successful response formatting."""
        result = {"data": "test"}
        task_type = TaskType.CODE_CREATION
        
        response = ResponseFormatter.format_success(result, task_type)
        
        assert response["status"] == "success"
        assert response["result"] == result
        assert response["type"] == task_type.value
    
    def test_format_success_without_type(self) -> None:
        """Test success formatting without task type."""
        result = {"data": "test"}
        
        response = ResponseFormatter.format_success(result)
        
        assert response["status"] == "success"
        assert response["result"] == result
        assert "type" not in response
    
    def test_format_error(self) -> None:
        """Test error response formatting."""
        error = ValueError("Test error")
        context = "Operation failed"
        
        response = ResponseFormatter.format_error(error, context)
        
        assert response["status"] == "error"
        assert "Test error" in response["error"]
        assert context in response["error"]
    
    def test_format_error_without_context(self) -> None:
        """Test error formatting without context."""
        error = ValueError("Test error")
        
        response = ResponseFormatter.format_error(error)
        
        assert response["status"] == "error"
        assert "Test error" in response["error"]

class TestTaskTemplateManager:
    """Test suite for TaskTemplateManager class"""
    
    def test_get_template_valid_type(self, sample_templates: Dict[TaskType, TaskTemplate]) -> None:
        """Test getting template for valid task type.
        
        Args:
            sample_templates: Dictionary of test templates
        """
        template = TaskTemplateManager.get_template(TaskType.CODE_MODIFICATION)
        
        assert template.description_template
        assert template.output_template
        assert len(template.steps) > 0
        
        # Verify template structure
        assert "{description}" in template.description_template
        assert "{steps}" in template.description_template
        assert "{requirements}" in template.output_template
    
    def test_get_template_invalid_type(self) -> None:
        """Test getting template for invalid task type."""
        with pytest.raises(ValueError):
            TaskTemplateManager.get_template("invalid_type")  # type: ignore

class TestTaskValidationMixin:
    """Test suite for TaskValidationMixin class with enhanced security and validation"""
    
    @pytest.fixture
    def validator(self) -> TaskValidationMixin:
        """Provide TaskValidationMixin instance."""
        return TaskValidationMixin()
    
    @pytest.mark.parametrize("description", [
        "",
        "   ",
        "short",
        "a" * 9,  # Just under minimum length
        "a" * (TaskValidationMixin.MAX_DESCRIPTION_LENGTH + 1),  # Exceeds max length
    ])
    def test_validate_task_description_invalid(
        self,
        validator: TaskValidationMixin,
        description: str
    ) -> None:
        """Test task description validation with invalid inputs."""
        with pytest.raises((ValidationError)):
            validator.validate_task_description(description)
    
    def test_validate_task_description_valid(self, validator: TaskValidationMixin) -> None:
        """Test task description validation with valid input."""
        valid_descriptions = [
            "This is a valid task description that is long enough",
            "Create a new authentication system with OAuth support",
            "Implement input validation for all form fields",
            "a" * TaskValidationMixin.MAX_DESCRIPTION_LENGTH  # Maximum valid length
        ]
        
        for description in valid_descriptions:
            validator.validate_task_description(description)  # Should not raise
    
    @pytest.mark.parametrize("output", [
        "",
        "   ",
        "\n\n",
        "a" * (TaskValidationMixin.MAX_OUTPUT_LENGTH + 1)  # Exceeds max length
    ])
    def test_validate_expected_output_invalid(
        self,
        validator: TaskValidationMixin,
        output: str
    ) -> None:
        """Test expected output validation with invalid inputs."""
        with pytest.raises(ValidationError):
            validator.validate_expected_output(output)
    
    def test_validate_expected_output_valid(self, validator: TaskValidationMixin) -> None:
        """Test expected output validation with valid input."""
        valid_outputs = [
            "Valid expected output",
            "Multiple\nline\noutput",
            "Detailed output with specifications",
            "a" * TaskValidationMixin.MAX_OUTPUT_LENGTH  # Maximum valid length
        ]
        
        for output in valid_outputs:
            validator.validate_expected_output(output)  # Should not raise
    
    @pytest.mark.parametrize("code", [
        # Invalid Python syntax
        "def broken_func(:",
        "print(Hello World)",
        # Security patterns
        "os.system('rm -rf /')",
        "subprocess.run(['rm', '-rf', '/'])",
        "__import__('os').system('echo hack')",
        "eval('__import__(\\'os\\').system(\\'rm -rf \\/')')",
        # Empty or whitespace
        "",
        "   ",
        "\n\n"
    ])
    def test_validate_code_output_invalid(
        self,
        validator: TaskValidationMixin,
        code: str
    ) -> None:
        """Test code output validation with invalid inputs."""
        with pytest.raises((ValidationError, SecurityError)):
            validator.validate_code_output(code)
    
    def test_validate_code_output_valid(self, validator: TaskValidationMixin) -> None:
        """Test code output validation with valid input."""
        valid_code = [
            "def greet(name: str) -> str:\n    return f'Hello, {name}!'",
            "class User:\n    def __init__(self, name: str):\n        self.name = name",
            """
            from typing import List
            
            def calculate_sum(numbers: List[int]) -> int:
                return sum(numbers)
            """
        ]
        
        for code in valid_code:
            validator.validate_code_output(code)  # Should not raise
    
    @pytest.mark.parametrize("content,pattern", [
        ("os.system('command')", r'system\s*\('),
        ("subprocess.run(['ls'])", r'subprocess\..*'),
        ("eval('2 + 2')", r'eval\s*\('),
        ("__import__('os')", r'__import__\s*\('),
    ])
    def test_security_pattern_detection(
        self,
        validator: TaskValidationMixin,
        content: str,
        pattern: str
    ) -> None:
        """Test security pattern detection."""
        with pytest.raises(SecurityError) as exc_info:
            validator._check_security_patterns(content)
        assert pattern in str(exc_info.value)

if __name__ == '__main__':
    pytest.main([__file__])