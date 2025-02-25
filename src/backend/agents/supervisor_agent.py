from crewai import Agent, Task, Crew, Process
from typing import List, Dict, Any, Optional
from .base_agent import VSCodeAgent
import yaml
import os

class SupervisorAgent(VSCodeAgent):
    """Supervisor agent that manages the development crew"""

    def __init__(self, name: str, project_path: str, config_path: Optional[str] = None):
        super().__init__(name, project_path, config_path)
        self.agents = {}
        self.tasks_config = self._load_tasks_config()

    def _load_tasks_config(self) -> Dict:
        """Load tasks configuration from YAML"""
        tasks_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'tasks.yaml')
        with open(tasks_path, 'r') as f:
            return yaml.safe_load(f)

    def register_agent(self, agent_type: str, agent: VSCodeAgent) -> None:
        """Register a specialized agent in the crew"""
        self.agents[agent_type] = agent

    def create_task(self, task_type: str, context: str = "") -> Task:
        """Create a task from configuration
        
        Args:
            task_type: Type of task from tasks.yaml
            context: Additional context for the task
            
        Returns:
            Task: Configured CrewAI task
        """
        if task_type not in self.tasks_config:
            raise ValueError(f"Unknown task type: {task_type}")
            
        task_config = self.tasks_config[task_type]
        description = task_config['description']
        if context:
            description = f"{description}\nContext: {context}"
            
        return Task(
            description=description,
            expected_output=task_config['expected_output'],
            agent=self.agents[task_config['agent']].agent
        )

    async def coordinate_task(self, main_task: str) -> Dict[str, Any]:
        """Coordinate task execution using CrewAI crew
        
        Args:
            main_task: Description of the main task to accomplish
            
        Returns:
            Dict containing results from the crew execution
        """
        try:
            # Break down task into subtasks
            tasks = []
            
            # Implementation task
            if 'code' in main_task.lower() or 'implement' in main_task.lower():
                tasks.append(self.create_task('implement_code', main_task))
                tasks.append(self.create_task('write_tests', main_task))
                tasks.append(self.create_task('create_documentation', main_task))
                tasks.append(self.create_task('review_changes', main_task))
            
            # Testing task
            elif 'test' in main_task.lower():
                tasks.append(self.create_task('write_tests', main_task))
                tasks.append(self.create_task('review_changes', main_task))
            
            # Documentation task
            elif 'document' in main_task.lower():
                tasks.append(self.create_task('create_documentation', main_task))
                tasks.append(self.create_task('review_changes', main_task))
            
            # Review task
            elif 'review' in main_task.lower():
                tasks.append(self.create_task('review_changes', main_task))
            
            # Default to implementation if no specific type detected
            else:
                tasks.append(self.create_task('implement_code', main_task))
            
            # Create crew with all agents and tasks
            crew = Crew(
                agents=list(self.agents.values()),
                tasks=tasks,
                process=Process.sequential,
                verbose=True,
                manager_llm=self.agent.llm,  # Use supervisor's LLM for management
                max_rpm=10,  # Limit requests per minute
                memory=True,  # Enable crew memory
                cache=True,  # Enable caching
            )
            
            # Execute crew tasks
            result = await crew.kickoff()
            
            return {
                'status': 'success',
                'result': result,
                'tasks': [t.description for t in tasks]
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': f'Task coordination failed: {str(e)}'
            }

    async def execute(self, task: Task) -> Dict[str, Any]:
        """Override execute to use crew coordination"""
        return await self.coordinate_task(task.description)
