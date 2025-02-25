from crewai import Task
from typing import Dict, Any, Optional
from .base_agent import VSCodeAgent

class PromptAgent(VSCodeAgent):
    """Prompt engineering agent responsible for optimizing and structuring user inputs"""

    def __init__(self, name: str, project_path: str, config_path: Optional[str] = None):
        super().__init__(name, project_path, config_path)

    async def execute(self, task: Task) -> Dict[str, Any]:
        """Execute a prompt engineering task using CrewAI's task system
        
        Args:
            task: CrewAI Task object with task details
            
        Returns:
            Dict containing execution result and status
        """
        try:
            # Create enhanced task description
            execution_task = self.create_task(
                description=self._create_task_description(task.description),
                expected_output=self._create_expected_output()
            )
            
            # Execute the task using CrewAI's system
            result = await super().execute(execution_task)
            
            return {
                'status': 'success',
                'enhanced_prompt': self._structure_prompt(task.description, result),
                'context': self._extract_context(task.description),
                'result': result
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': f'Prompt engineering failed: {str(e)}'
            }

    def _create_task_description(self, base_description: str) -> str:
        """Create detailed prompt engineering task description"""
        return f"""
        Prompt Engineering Task:
        {base_description}
        
        1. Analyze user request and identify key components
        2. Extract specific requirements and constraints
        3. Identify implicit technical requirements
        4. Structure the request for optimal agent understanding
        5. Add necessary context and clarifications
        """

    def _create_expected_output(self) -> str:
        """Define expected output for prompt engineering"""
        return """
        1. Structured and enhanced prompt
        2. Extracted technical requirements
        3. Identified constraints and considerations
        4. Additional context if needed
        """

    def _structure_prompt(self, original_prompt: str, analysis_result: Dict[str, Any]) -> str:
        """Structure the prompt for optimal agent consumption"""
        # Base structure for all prompts
        structured_prompt = {
            'original_request': original_prompt,
            'technical_requirements': self._extract_technical_requirements(original_prompt),
            'target_agents': self._identify_required_agents(original_prompt),
            'constraints': self._identify_constraints(original_prompt),
            'context': self._extract_context(original_prompt)
        }
        
        return structured_prompt

    def _extract_technical_requirements(self, prompt: str) -> list:
        """Extract technical requirements from the prompt"""
        # Keywords to look for that indicate technical requirements
        tech_keywords = [
            'create', 'implement', 'build', 'develop', 'test',
            'function', 'class', 'method', 'api', 'database',
            'interface', 'component', 'module', 'system', 'service'
        ]
        
        requirements = []
        words = prompt.lower().split()
        
        for i, word in enumerate(words):
            if word in tech_keywords and i + 1 < len(words):
                # Capture the requirement with some context
                req = ' '.join(words[max(0, i-2):min(len(words), i+3)])
                requirements.append(req)
                
        return requirements

    def _identify_required_agents(self, prompt: str) -> list:
        """Identify which agents will be needed based on the prompt"""
        agents = []
        
        # Map keywords to agents
        agent_keywords = {
            'code_agent': ['create', 'implement', 'build', 'develop', 'code'],
            'test_agent': ['test', 'verify', 'validate', 'check'],
            'documentation_agent': ['document', 'explain', 'describe'],
            'review_agent': ['review', 'assess', 'evaluate', 'analyze']
        }
        
        prompt_lower = prompt.lower()
        for agent, keywords in agent_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                agents.append(agent)
                
        # Code agent is always included if no specific agents are identified
        if not agents:
            agents.append('code_agent')
            
        return agents

    def _identify_constraints(self, prompt: str) -> list:
        """Identify constraints from the prompt"""
        constraints = []
        
        # Common constraint indicators
        constraint_keywords = {
            'must': 'requirement',
            'should': 'preference',
            'only': 'limitation',
            'except': 'exclusion',
            'without': 'exclusion',
            'using': 'technology constraint',
            'with': 'technology constraint'
        }
        
        words = prompt.lower().split()
        for i, word in enumerate(words):
            if word in constraint_keywords and i + 1 < len(words):
                # Capture the constraint with context
                constraint = ' '.join(words[max(0, i-1):min(len(words), i+3)])
                constraints.append({
                    'type': constraint_keywords[word],
                    'description': constraint
                })
                
        return constraints

    def _extract_context(self, prompt: str) -> Dict[str, Any]:
        """Extract relevant context from the prompt"""
        context = {
            'scope': self._determine_scope(prompt),
            'priority': self._determine_priority(prompt),
            'dependencies': self._identify_dependencies(prompt)
        }
        return context

    def _determine_scope(self, prompt: str) -> str:
        """Determine the scope of the request"""
        if any(word in prompt.lower() for word in ['entire', 'complete', 'full', 'whole']):
            return 'full'
        elif any(word in prompt.lower() for word in ['part', 'specific', 'only', 'just']):
            return 'partial'
        return 'standard'

    def _determine_priority(self, prompt: str) -> str:
        """Determine the priority level of the request"""
        if any(word in prompt.lower() for word in ['urgent', 'asap', 'immediately']):
            return 'high'
        elif any(word in prompt.lower() for word in ['when possible', 'eventually']):
            return 'low'
        return 'medium'

    def _identify_dependencies(self, prompt: str) -> list:
        """Identify any dependencies mentioned in the prompt"""
        dependencies = []
        
        # Look for dependency indicators
        dependency_indicators = ['requires', 'needs', 'depends', 'after', 'before']
        words = prompt.lower().split()
        
        for i, word in enumerate(words):
            if word in dependency_indicators and i + 1 < len(words):
                # Capture the dependency with context
                dep = ' '.join(words[max(0, i):min(len(words), i+3)])
                dependencies.append(dep)
                
        return dependencies
