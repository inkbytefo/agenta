"""
Unit tests for task utility classes and functions.
"""
import pytest
from typing import Dict, Any
from ..agents.utils.task_utils import (
    TaskType,
    CodeTaskDetector,
    TaskFormatter,
    ResponseFormatter,
    TaskTemplateManager,
    TaskValidationMixin
)

class TestCodeTaskDetector:
    """Tests for the CodeTaskDetector class"""
    
    @pytest.fixture
    def detector(self) -> CodeTaskDetector:
        return CodeTaskDetector()
    
    @pytest.mark.parametrize("description,expected_type", [
        ("Modify the login function", TaskType.CODE_MODIFICATION),
        ("Update user authentication", TaskType.CODE_MODIFICATION),
        ("Fix the bug in parser", TaskType.CODE_MODIFICATION),
        ("Refactor database queries", TaskType.CODE_MODIFICATION),
        ("Create a new API endpoint", TaskType.CODE_CREATION),
        ("Implement user registration", TaskType.CODE_CREATION),
        ("Add input validation", TaskType.CODE_CREATION),
    ])
    def test_detect_type(self, detector: CodeTaskDetector, description: str, expected_type: TaskType) -> None:
        """Test task type detection with various descriptions"""
        assert detector.detect_type(description) == expected_type

class TestTaskFormatter:
    """Tests for the TaskFormatter class"""
    
    @pytest.fixture
    def template(self) -> str:
        return """
        Task: {description}
        
        Steps:
        {steps}
        """
    
    @pytest.fixture
    def steps(self) -> list:
        return [
            "Analyze requirements",
            "Design solution",
            "Implement changes"
        ]
    
    def test_format_description(self, template: str, steps: list) -> None:
        """Test description formatting with steps"""
        description = "Test task"
        result = TaskFormatter.format_description(template, description, steps)
        
        assert description in result
        for step in steps:
            assert step in result
        assert "1. " in result  # Check numbering
    
    def test_format_output_template(self) -> None:
        """Test output template formatting"""
        template = "Expected:\n{requirements}"
        requirements = ["Clean code", "Documentation", "Tests"]
        
        result = TaskFormatter.format_output_template(template, requirements)
        
        assert "Expected:" in result
        for req in requirements:
            assert req in result

class TestResponseFormatter:
    """Tests for the ResponseFormatter class"""
    
    def test_format_success(self) -> None:
        """Test successful response formatting"""
        result = {"data": "test"}
        task_type = TaskType.CODE_CREATION
        
        response = ResponseFormatter.format_success(result, task_type)
        
        assert response["status"] == "success"
        assert response["result"] == result
        assert response["type"] == task_type.value
    
    def test_format_error(self) -> None:
        """Test error response formatting"""
        error = ValueError("Test error")
        context = "Operation failed"
        
        response = ResponseFormatter.format_error(error, context)
        
        assert response["status"] == "error"
        assert "Test error" in response["error"]
        assert context in response["error"]

class TestTaskTemplateManager:
    """Tests for the TaskTemplateManager class"""
    
    def test_get_template_valid_type(self) -> None:
        """Test getting template for valid task type"""
        template = TaskTemplateManager.get_template(TaskType.CODE_MODIFICATION)
        
        assert template.description_template
        assert template.output_template
        assert template.steps
        assert len(template.steps) > 0
    
    def test_get_template_invalid_type(self) -> None:
        """Test getting template for invalid task type"""
        with pytest.raises(ValueError):
            TaskTemplateManager.get_template("invalid_type")  # type: ignore

class TestTaskValidationMixin:
    """Tests for the TaskValidationMixin class"""
    
    @pytest.fixture
    def validator(self) -> TaskValidationMixin:
        return TaskValidationMixin()
    
    @pytest.mark.parametrize("description", [
        "",
        "   ",
        "too short",
    ])
    def test_validate_task_description_invalid(self, validator: TaskValidationMixin, description: str) -> None:
        """Test task description validation with invalid inputs"""
        with pytest.raises(ValueError):
            validator.validate_task_description(description)
    
    def test_validate_task_description_valid(self, validator: TaskValidationMixin) -> None:
        """Test task description validation with valid input"""
        description = "This is a valid task description that is long enough"
        validator.validate_task_description(description)  # Should not raise
    
    @pytest.mark.parametrize("output", [
        "",
        "   ",
    ])
    def test_validate_expected_output_invalid(self, validator: TaskValidationMixin, output: str) -> None:
        """Test expected output validation with invalid inputs"""
        with pytest.raises(ValueError):
            validator.validate_expected_output(output)
    
    def test_validate_expected_output_valid(self, validator: TaskValidationMixin) -> None:
        """Test expected output validation with valid input"""
        output = "Valid expected output"
        validator.validate_expected_output(output)  # Should not raise

if __name__ == '__main__':
    pytest.main([__file__])