from crewai import Task
from typing import Dict, Any, Optional
from .base_agent import VSCodeAgent

class CodeAgent(VSCodeAgent):
    """Code implementation agent responsible for writing and modifying code"""

    def __init__(self, name: str, project_path: str, config_path: Optional[str] = None):
        super().__init__(name, project_path, config_path)

    async def execute(self, task: Task) -> Dict[str, Any]:
        """Execute a code-related task using CrewAI's task system
        
        Args:
            task: CrewAI Task object with task details
            
        Returns:
            Dict containing execution result and status
        """
        try:
            # Analyze if this is a modification task
            is_modification = self._is_modification_task(task.description)
            
            # Create specific task based on type
            execution_task = self.create_task(
                description=self._create_task_description(task.description, is_modification),
                expected_output=self._create_expected_output(is_modification)
            )
            
            # Execute the task using CrewAI's system
            result = await super().execute(execution_task)
            
            return {
                'status': 'success',
                'type': 'modification' if is_modification else 'new_implementation',
                'result': result
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': f'Code implementation failed: {str(e)}'
            }

    def _is_modification_task(self, task_description: str) -> bool:
        """Determine if task involves modifying existing code"""
        modification_keywords = ['modify', 'update', 'change', 'fix', 'refactor']
        return any(keyword in task_description.lower() for keyword in modification_keywords)

    def _create_task_description(self, base_description: str, is_modification: bool) -> str:
        """Create detailed task description based on type"""
        if is_modification:
            return f"""
            Code Modification Task:
            {base_description}
            
            1. Analyze existing code
            2. Plan necessary modifications
            3. Implement changes following best practices
            4. Ensure backwards compatibility
            5. Add or update comments as needed
            """
        else:
            return f"""
            New Code Implementation Task:
            {base_description}
            
            1. Plan the implementation
            2. Write clean, maintainable code
            3. Follow project standards
            4. Include proper documentation
            5. Consider edge cases and error handling
            """

    def _create_expected_output(self, is_modification: bool) -> str:
        """Define expected output based on task type"""
        if is_modification:
            return """
            1. Successfully modified code that meets requirements
            2. No regressions or breaking changes
            3. Updated documentation if needed
            4. Clear comments explaining changes
            """
        else:
            return """
            1. New code implementation meeting requirements
            2. Proper error handling and edge case coverage
            3. Clear documentation and comments
            4. Tests if applicable
            """
