from crewai import Task
from typing import Dict, Any, Optional
from .base_agent import VSCodeAgent
import os

class TestAgent(VSCodeAgent):
    """Test implementation agent responsible for creating and managing tests"""

    def __init__(self, name: str, project_path: str, config_path: Optional[str] = None):
        super().__init__(name, project_path, config_path)

    async def execute(self, task: Task) -> Dict[str, Any]:
        """Execute a test-related task using CrewAI's task system
        
        Args:
            task: CrewAI Task object with task details
            
        Returns:
            Dict containing execution result and status
        """
        try:
            # Analyze the type of test task
            task_type = self._analyze_test_task(task.description)
            target = self._extract_test_target(task.description)
            
            # Create specific task based on type
            execution_task = self.create_task(
                description=self._create_task_description(task.description, task_type, target),
                expected_output=self._create_expected_output(task_type)
            )
            
            # Execute the task using CrewAI's system
            result = await super().execute(execution_task)
            
            return {
                'status': 'success',
                'type': task_type,
                'target': target,
                'result': result
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': f'Test task execution failed: {str(e)}'
            }

    def _analyze_test_task(self, task_description: str) -> str:
        """Determine the type of test task"""
        task = task_description.lower()
        
        if any(word in task for word in ['create', 'write', 'implement']):
            return 'create'
        elif any(word in task for word in ['run', 'execute', 'check']):
            return 'run'
        elif any(word in task for word in ['update', 'modify', 'fix']):
            return 'update'
        else:
            return 'unknown'

    def _extract_test_target(self, task_description: str) -> str:
        """Extract the target file/component for testing"""
        words = task_description.split()
        for i, word in enumerate(words):
            if word in ['test', 'tests'] and i + 1 < len(words):
                return words[i + 1]
        return 'unknown_target'

    def _create_task_description(self, base_description: str, task_type: str, target: str) -> str:
        """Create detailed task description based on type"""
        if task_type == 'create':
            test_file = self._generate_test_filename(target)
            return f"""
            Test Creation Task:
            {base_description}
            
            Target: {target}
            Test File: {test_file}
            
            1. Analyze the target implementation
            2. Identify key functionality to test
            3. Create comprehensive test cases
            4. Implement test setup and teardown
            5. Add assertions and error cases
            """
        elif task_type == 'run':
            return f"""
            Test Execution Task:
            {base_description}
            
            Target: {target}
            
            1. Set up test environment
            2. Run test suite
            3. Collect and analyze results
            4. Report coverage and outcomes
            """
        else:  # update
            return f"""
            Test Update Task:
            {base_description}
            
            Target: {target}
            
            1. Review existing tests
            2. Identify areas needing updates
            3. Implement test modifications
            4. Verify test coverage
            5. Ensure backwards compatibility
            """

    def _create_expected_output(self, task_type: str) -> str:
        """Define expected output based on task type"""
        if task_type == 'create':
            return """
            1. Complete test suite implementation
            2. High test coverage
            3. Clear test documentation
            4. Proper error handling cases
            """
        elif task_type == 'run':
            return """
            1. Test execution results
            2. Coverage report
            3. Identified issues if any
            4. Performance metrics
            """
        else:  # update
            return """
            1. Updated test suite
            2. Maintained or improved coverage
            3. Documentation updates
            4. Successful test execution
            """

    def _generate_test_filename(self, target: str) -> str:
        """Generate appropriate test filename"""
        test_file = f"test_{os.path.basename(target)}"
        if not test_file.endswith('_test.py'):
            test_file = test_file.replace('.py', '_test.py')
        return test_file
