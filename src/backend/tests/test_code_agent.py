"""
Unit tests for the CodeAgent class.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from typing import Dict, Any
from ..agents.code_agent import CodeAgent
from ..agents.utils.task_utils import TaskType
from crewai import Task

@pytest.fixture
def mock_llm_manager():
    """Mock LLM provider manager"""
    manager = MagicMock()
    manager.get_agent_config.return_value = None
    manager.get_provider.return_value = None
    return manager

@pytest.fixture
def mock_config_path(tmp_path) -> str:
    """Create a temporary config file"""
    config_content = """
    test_agent:
        role: "Test Code Agent"
        goal: "Writing and modifying code"
        backstory: "An agent for testing"
        verbose: false
        allow_delegation: false
    """
    config_file = tmp_path / "agents.yaml"
    config_file.write_text(config_content)
    return str(config_file)

@pytest.fixture
async def code_agent(sample_project_path: str, mock_config_path: str) -> CodeAgent:
    """Create a CodeAgent instance for testing"""
    with patch('crewai.Agent'):  # Mock CrewAI Agent
        agent = CodeAgent("test_agent", sample_project_path, mock_config_path)
        agent.agent = MagicMock()  # Mock the CrewAI agent instance
        agent.agent.execute = AsyncMock()  # Mock execute method
        return agent

class TestCodeAgent:
    """Tests for the CodeAgent class"""

    def test_initialization(self, code_agent: CodeAgent, sample_project_path: str) -> None:
        """Test agent initialization"""
        assert code_agent.name == "test_agent"
        assert code_agent.project_path == sample_project_path
        assert code_agent.task_detector is not None
        assert code_agent.tools == []

    @pytest.mark.asyncio
    async def test_execute_modification_task(self, code_agent: CodeAgent, mock_task: Task) -> None:
        """Test execution of a code modification task"""
        # Setup
        mock_task.description = "Modify the authentication system"
        expected_result = {"status": "completed", "output": "Modified authentication system"}
        code_agent.agent.execute.return_value = expected_result

        # Execute
        result = await code_agent.execute(mock_task)

        # Assert
        assert result["status"] == "success"
        assert result["type"] == TaskType.CODE_MODIFICATION.value
        assert "result" in result
        code_agent.agent.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_creation_task(self, code_agent: CodeAgent, mock_task: Task) -> None:
        """Test execution of a code creation task"""
        # Setup
        mock_task.description = "Create a new API endpoint"
        expected_result = {"status": "completed", "output": "Created new endpoint"}
        code_agent.agent.execute.return_value = expected_result

        # Execute
        result = await code_agent.execute(mock_task)

        # Assert
        assert result["status"] == "success"
        assert result["type"] == TaskType.CODE_CREATION.value
        assert "result" in result

    @pytest.mark.asyncio
    async def test_execute_with_empty_description(self, code_agent: CodeAgent, mock_task: Task) -> None:
        """Test execution with invalid empty description"""
        # Setup
        mock_task.description = ""

        # Execute and Assert
        result = await code_agent.execute(mock_task)
        assert result["status"] == "error"
        assert "Task validation failed" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_with_execution_error(self, code_agent: CodeAgent, mock_task: Task) -> None:
        """Test handling of execution errors"""
        # Setup
        mock_task.description = "Create a new feature"
        code_agent.agent.execute.side_effect = Exception("Execution failed")

        # Execute
        result = await code_agent.execute(mock_task)

        # Assert
        assert result["status"] == "error"
        assert "Code implementation failed" in result["error"]

    @pytest.mark.parametrize("description,expected_validation", [
        ("", False),
        ("   ", False),
        ("too short", False),
        ("This is a valid task description", True),
    ])
    def test_task_validation(self, code_agent: CodeAgent, description: str, expected_validation: bool) -> None:
        """Test task description validation"""
        if expected_validation:
            code_agent.validate_task_description(description)  # Should not raise
        else:
            with pytest.raises(ValueError):
                code_agent.validate_task_description(description)

    def test_validate_code_output(self, code_agent: CodeAgent) -> None:
        """Test code output validation"""
        # Test empty output
        with pytest.raises(ValueError):
            code_agent.validate_code_output("")
        
        # Test valid output
        valid_output = "def test_function():\n    pass"
        code_agent.validate_code_output(valid_output)  # Should not raise

if __name__ == '__main__':
    pytest.main([__file__])