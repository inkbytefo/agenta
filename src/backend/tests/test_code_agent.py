"""
Unit tests for the CodeAgent class.

Tests cover:
- Agent initialization
- Task execution
- Configuration management
- Rate limiting
- Error handling
- Input validation

Important: Run with pytest's async support:
    pytest --asyncio-mode=auto
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from typing import Dict, Any
from pathlib import Path
from ..agents.code_agent import CodeAgent
from ..agents.utils.task_utils import TaskType
from ..config.config_manager import (
    AgentConfig,
    ConfigurationError,
    get_config_manager,
    init_config_manager
)
from crewai import Task

# Test Fixtures

@pytest.fixture
def mock_llm_manager():
    """Provide a mock LLM provider manager.
    
    Returns:
        MagicMock: Configured mock manager
    """
    manager = MagicMock()
    manager.get_agent_config.return_value = None
    manager.get_provider.return_value = None
    return manager

@pytest.fixture
def mock_config_path(tmp_path: Path) -> str:
    """Create a temporary agent configuration file.
    
    Args:
        tmp_path: Pytest fixture providing temporary directory
        
    Returns:
        str: Path to configuration file
    """
    config_content = """
    test_agent:
        role: "Test Code Agent"
        goal: "Writing and modifying code"
        backstory: "An agent for testing"
        verbose: false
        allow_delegation: false
        max_iter: 10
        max_retry_limit: 3
    """
    config_file = tmp_path / "agents.yaml"
    config_file.write_text(config_content)
    return str(config_file)

@pytest.fixture
def mock_config_manager(mock_config_path: str):
    """Initialize configuration manager with test configuration.
    
    Args:
        mock_config_path: Path to test configuration
        
    Returns:
        ConfigManager: Initialized configuration manager
    """
    config_dir = str(Path(mock_config_path).parent)
    return init_config_manager(config_dir)

@pytest.fixture
async def code_agent(
    sample_project_path: str,
    mock_config_path: str,
    mock_config_manager
) -> CodeAgent:
    """Create a CodeAgent instance for testing.
    
    Args:
        sample_project_path: Path to test project
        mock_config_path: Path to test configuration
        mock_config_manager: Configured manager instance
        
    Returns:
        CodeAgent: Initialized agent instance
    """
    with patch('crewai.Agent'):  # Mock CrewAI Agent
        agent = CodeAgent("test_agent", sample_project_path, mock_config_path)
        agent.agent = MagicMock()  # Mock the CrewAI agent instance
        agent.agent.execute = AsyncMock()  # Mock execute method
        return agent

# Test Classes

class TestCodeAgent:
    """Test suite for CodeAgent class"""

    def test_initialization(
        self,
        code_agent: CodeAgent,
        sample_project_path: str
    ) -> None:
        """Test agent initialization with configuration.
        
        Args:
            code_agent: CodeAgent fixture
            sample_project_path: Test project path
        """
        assert code_agent.name == "test_agent"
        assert code_agent.project_path == sample_project_path
        assert code_agent.task_detector is not None
        assert code_agent.tools == []

    def test_initialization_invalid_path(self, mock_config_path: str) -> None:
        """Test initialization with invalid project path.
        
        Args:
            mock_config_path: Test configuration path
        """
        with pytest.raises(ValueError, match="Project path does not exist"):
            CodeAgent("test_agent", "/invalid/path", mock_config_path)

    def test_initialization_invalid_name(
        self,
        sample_project_path: str,
        mock_config_path: str
    ) -> None:
        """Test initialization with invalid agent name.
        
        Args:
            sample_project_path: Test project path
            mock_config_path: Test configuration path
        """
        with pytest.raises(ValueError, match="Agent name must be a non-empty string"):
            CodeAgent("", sample_project_path, mock_config_path)

    @pytest.mark.asyncio
    async def test_execute_modification_task(
        self,
        code_agent: CodeAgent,
        mock_task: Task
    ) -> None:
        """Test execution of a code modification task.
        
        Args:
            code_agent: CodeAgent fixture
            mock_task: CrewAI Task fixture
        """
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
    async def test_execute_creation_task(
        self,
        code_agent: CodeAgent,
        mock_task: Task
    ) -> None:
        """Test execution of a code creation task.
        
        Args:
            code_agent: CodeAgent fixture
            mock_task: CrewAI Task fixture
        """
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
    async def test_execute_with_empty_description(
        self,
        code_agent: CodeAgent,
        mock_task: Task
    ) -> None:
        """Test execution with invalid empty description.
        
        Args:
            code_agent: CodeAgent fixture
            mock_task: CrewAI Task fixture
        """
        # Setup
        mock_task.description = ""

        # Execute and Assert
        with pytest.raises(ValueError, match="Task description cannot be empty"):
            await code_agent.execute(mock_task)

    @pytest.mark.asyncio
    async def test_execute_with_rate_limit(
        self,
        code_agent: CodeAgent,
        mock_task: Task
    ) -> None:
        """Test rate limiting during task execution.
        
        Args:
            code_agent: CodeAgent fixture
            mock_task: CrewAI Task fixture
        """
        # Setup
        mock_task.description = "Test rate limited task"
        code_agent.agent.execute.side_effect = [
            {"status": "completed", "output": "Result"}
            for _ in range(5)
        ]

        # Execute multiple times
        results = []
        for _ in range(5):
            result = await code_agent.execute(mock_task)
            results.append(result)
            
        # Assert all succeeded
        assert all(r["status"] == "success" for r in results)

    @pytest.mark.asyncio
    async def test_execute_with_retry(
        self,
        code_agent: CodeAgent,
        mock_task: Task
    ) -> None:
        """Test task execution with retries.
        
        Args:
            code_agent: CodeAgent fixture
            mock_task: CrewAI Task fixture
        """
        # Setup
        mock_task.description = "Test retry task"
        code_agent.agent.execute.side_effect = [
            Exception("First attempt failed"),
            {"status": "completed", "output": "Second attempt succeeded"}
        ]

        # Execute
        result = await code_agent.execute(mock_task)

        # Assert
        assert result["status"] == "success"
        assert code_agent.agent.execute.call_count == 2

    def test_task_validation(self, code_agent: CodeAgent) -> None:
        """Test task description validation.
        
        Args:
            code_agent: CodeAgent fixture
        """
        invalid_descriptions = ["", "   ", "too short"]
        valid_description = "This is a valid task description"

        # Test invalid descriptions
        for desc in invalid_descriptions:
            with pytest.raises(ValueError):
                code_agent.validate_task_description(desc)

        # Test valid description
        code_agent.validate_task_description(valid_description)  # Should not raise

if __name__ == '__main__':
    pytest.main([__file__])