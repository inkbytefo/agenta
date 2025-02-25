"""
Test configuration and shared fixtures for the agent system.
"""
import os
import pytest
from typing import Dict, Any
from unittest.mock import MagicMock
from crewai import Task, Agent

# Ensure we're using test configuration
os.environ['TESTING'] = 'true'

@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Provide sample agent configuration"""
    return {
        'role': 'Test Agent',
        'goal': 'Testing functionality',
        'backstory': 'A test agent for unit testing',
        'verbose': False,
        'allow_delegation': False
    }

@pytest.fixture
def mock_task() -> Task:
    """Provide a mock CrewAI task"""
    mock_agent = MagicMock(spec=Agent)
    return Task(
        description="Test task description",
        expected_output="Test expected output",
        agent=mock_agent
    )

@pytest.fixture
def sample_project_path(tmp_path) -> str:
    """Provide a temporary project path"""
    proj_dir = tmp_path / "test_project"
    proj_dir.mkdir()
    return str(proj_dir)