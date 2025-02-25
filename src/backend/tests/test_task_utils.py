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
from ..agents.utils.task_utils import (
    TaskType,
    CodeTaskDetector,
    TaskFormatter,
    ResponseFormatter,
    TaskTemplateManager,
    TaskValidationMixin,
    TaskTemplate,
    ConfigurationError
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
    """Test suite for CodeTaskDetector class"""
    
    @pytest.fixture
    def detector(self) -> CodeTaskDetector:
        """Provide CodeTaskDetector instance."""
        return CodeTaskDetector()
    
    @pytest.mark.parametrize("description,expected_type", [
        ("Modify the login function", TaskType.CODE_MODIFICATION),
        ("Update user authentication", TaskType.CODE_MODIFICATION),
        ("Fix the bug in parser", TaskType.CODE_MODIFICATION),
        ("Refactor database queries", TaskType.CODE_MODIFICATION),
        ("Create a new API endpoint", TaskType.CODE_CREATION),
        ("Implement user registration", TaskType.CODE_CREATION),
        ("Add input validation", TaskType.CODE_CREATION),
        ("Build authentication system", TaskType.CODE_CREATION),
    ])
    def test_detect_type(
        self,
        detector: CodeTaskDetector,
        description: str,
        expected_type: TaskType
    ) -> None:
        """Test task type detection with various descriptions.
        
        Args:
            detector: CodeTaskDetector instance
            description: Task description to test
            expected_type: Expected TaskType result
        """
        assert detector.detect_type(description) == expected_type

    def test_detect_type_edge_cases(self, detector: CodeTaskDetector) -> None:
        """Test task type detection with edge cases.
        
        Args:
            detector: CodeTaskDetector instance
        """
        # Empty description defaults to creation
        assert detector.detect_type("") == TaskType.CODE_CREATION
        
        # Mixed signals default to most specific (modification)
        assert detector.detect_type("Create by modifying existing code") == TaskType.CODE_MODIFICATION

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
    """Test suite for TaskValidationMixin class"""
    
    @pytest.fixture
    def validator(self) -> TaskValidationMixin:
        """Provide TaskValidationMixin instance."""
        return TaskValidationMixin()
    
    @pytest.mark.parametrize("description", [
        "",
        "   ",
        "short",
        "a" * 9,  # Just under minimum length
    ])
    def test_validate_task_description_invalid(
        self,
        validator: TaskValidationMixin,
        description: str
    ) -> None:
        """Test task description validation with invalid inputs.
        
        Args:
            validator: TaskValidationMixin instance
            description: Invalid description to test
        """
        with pytest.raises(ValueError):
            validator.validate_task_description(description)
    
    def test_validate_task_description_valid(self, validator: TaskValidationMixin) -> None:
        """Test task description validation with valid input.
        
        Args:
            validator: TaskValidationMixin instance
        """
        valid_descriptions = [
            "This is a valid task description that is long enough",
            "Create a new authentication system with OAuth support",
            "Implement input validation for all form fields"
        ]
        
        for description in valid_descriptions:
            validator.validate_task_description(description)  # Should not raise
    
    @pytest.mark.parametrize("output", [
        "",
        "   ",
        "\n\n",
    ])
    def test_validate_expected_output_invalid(
        self,
        validator: TaskValidationMixin,
        output: str
    ) -> None:
        """Test expected output validation with invalid inputs.
        
        Args:
            validator: TaskValidationMixin instance
            output: Invalid output to test
        """
        with pytest.raises(ValueError):
            validator.validate_expected_output(output)
    
    def test_validate_expected_output_valid(self, validator: TaskValidationMixin) -> None:
        """Test expected output validation with valid input.
        
        Args:
            validator: TaskValidationMixin instance
        """
        valid_outputs = [
            "Valid expected output",
            "Multiple\nline\noutput",
            "Detailed output with specifications"
        ]
        
        for output in valid_outputs:
            validator.validate_expected_output(output)  # Should not raise

if __name__ == '__main__':
    pytest.main([__file__])