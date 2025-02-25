from typing import Dict, Any, Optional, List
from crewai import Task
from .base_agent import VSCodeAgent
from ..modes.mode_manager import ModeManager, AgentMode

class PlanningAgent(VSCodeAgent):
    """Planning agent responsible for analyzing tasks and creating execution plans"""

    def __init__(self, name: str, project_path: str, config_path: Optional[str] = None):
        super().__init__(name, project_path, config_path)
        self.mode_manager = ModeManager()

    async def execute(self, task: Task) -> Dict[str, Any]:
        """Execute a planning task using CrewAI's task system
        
        Args:
            task: CrewAI Task object with task details
            
        Returns:
            Dict containing execution result and status
        """
        try:
            current_mode = self.mode_manager.get_current_mode()
            
            # Adjust LLM settings based on mode
            llm_settings = self.mode_manager.get_llm_settings()
            self._apply_llm_settings(llm_settings)
            
            if current_mode == AgentMode.PLAN:
                return await self._plan_task(task)
            else:  # ACT mode
                return await self._execute_plan(task)
            
        except Exception as e:
            return {
                'status': 'error',
                'error': f'Planning task execution failed: {str(e)}'
            }

    async def _plan_task(self, task: Task) -> Dict[str, Any]:
        """Create a detailed execution plan
        
        Args:
            task: Task to plan
            
        Returns:
            Dict containing plan details
        """
        try:
            # Create planning task
            planning_task = self.create_task(
                description=self._create_planning_description(task.description),
                expected_output=self._create_planning_output()
            )
            
            # Execute planning
            result = await super().execute(planning_task)
            
            # Structure the plan
            plan = self._structure_plan(result.get('result', ''))
            
            return {
                'status': 'success',
                'mode': 'plan',
                'plan': plan
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': f'Planning failed: {str(e)}'
            }

    async def _execute_plan(self, task: Task) -> Dict[str, Any]:
        """Execute a previously created plan
        
        Args:
            task: Task containing execution details
            
        Returns:
            Dict containing execution results
        """
        try:
            # Verify we have necessary permissions
            if not self.mode_manager.is_operation_allowed('execute'):
                return {
                    'status': 'error',
                    'error': 'Execution not allowed in current mode'
                }
            
            # Create execution task
            execution_task = self.create_task(
                description=self._create_execution_description(task.description),
                expected_output=self._create_execution_output()
            )
            
            # Execute planned actions
            result = await super().execute(execution_task)
            
            return {
                'status': 'success',
                'mode': 'act',
                'result': result.get('result', '')
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': f'Execution failed: {str(e)}'
            }

    def _create_planning_description(self, base_description: str) -> str:
        """Create detailed planning task description"""
        return f"""
        Planning Task:
        {base_description}
        
        Create a detailed execution plan including:
        1. Required steps and their sequence
        2. Dependencies and prerequisites
        3. Resources needed
        4. Potential risks and mitigations
        5. Success criteria
        
        DO NOT execute any actions - this is planning only.
        """

    def _create_planning_output(self) -> str:
        """Define expected planning output"""
        return """
        1. Structured execution plan
        2. Required steps with dependencies
        3. Risk assessment
        4. Resource requirements
        5. Success criteria
        """

    def _create_execution_description(self, base_description: str) -> str:
        """Create detailed execution task description"""
        return f"""
        Execution Task:
        {base_description}
        
        Execute the planned actions following:
        1. Verify prerequisites
        2. Follow defined sequence
        3. Validate each step
        4. Monitor for issues
        5. Report progress
        """

    def _create_execution_output(self) -> str:
        """Define expected execution output"""
        return """
        1. Execution results
        2. Step completion status
        3. Issues encountered
        4. Validation results
        """

    def _structure_plan(self, raw_plan: str) -> Dict[str, Any]:
        """Structure a raw plan into organized sections"""
        plan = {
            'steps': [],
            'dependencies': [],
            'resources': [],
            'risks': [],
            'success_criteria': []
        }
        
        # Parse raw plan and organize into sections
        current_section = None
        for line in raw_plan.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Identify sections
            if 'step' in line.lower():
                current_section = 'steps'
            elif 'dependenc' in line.lower():
                current_section = 'dependencies'
            elif 'resource' in line.lower():
                current_section = 'resources'
            elif 'risk' in line.lower():
                current_section = 'risks'
            elif 'success' in line.lower():
                current_section = 'success_criteria'
            elif current_section:
                plan[current_section].append(line)
        
        return plan

    def _apply_llm_settings(self, settings: Dict[str, Any]) -> None:
        """Apply mode-specific LLM settings"""
        if self.agent and self.agent.llm:
            for key, value in settings.items():
                if hasattr(self.agent.llm, key):
                    setattr(self.agent.llm, key, value)
