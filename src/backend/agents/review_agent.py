from crewai import Task
from typing import Dict, Any, Optional, List
from .base_agent import VSCodeAgent
import os

class ReviewAgent(VSCodeAgent):
    """Code review agent responsible for analyzing code quality and providing feedback"""

    def __init__(self, name: str, project_path: str, config_path: Optional[str] = None):
        super().__init__(name, project_path, config_path)
        
        # Review criteria categories
        self.review_criteria = {
            'code_style': [
                'Consistent naming conventions',
                'Proper indentation and formatting',
                'Code organization and structure'
            ],
            'functionality': [
                'Logic correctness',
                'Error handling',
                'Edge cases consideration'
            ],
            'performance': [
                'Algorithm efficiency',
                'Resource usage',
                'Optimization opportunities'
            ],
            'security': [
                'Input validation',
                'Data sanitization',
                'Security best practices'
            ],
            'maintainability': [
                'Code readability',
                'Documentation completeness',
                'Modularity and reusability'
            ]
        }

    async def execute(self, task: Task) -> Dict[str, Any]:
        """Execute a review task using CrewAI's task system
        
        Args:
            task: CrewAI Task object with task details
            
        Returns:
            Dict containing execution result and status
        """
        try:
            # Analyze the type of review task
            review_type = self._analyze_review_task(task.description)
            target = self._extract_review_target(task.description)
            
            # For specific reviews, extract focus area
            focus = None
            if review_type == 'specific':
                target, focus = self._extract_review_focus(task.description)
            
            # Create specific task based on type
            execution_task = self.create_task(
                description=self._create_task_description(task.description, review_type, target, focus),
                expected_output=self._create_expected_output(review_type, focus)
            )
            
            # Execute the task using CrewAI's system
            result = await super().execute(execution_task)
            
            # Perform review analysis based on type
            if review_type == 'full':
                review_results = {}
                for category, criteria in self.review_criteria.items():
                    review_results[category] = self._review_category(result, category, criteria)
                summary = self._generate_review_summary(review_results)
                result['review_results'] = review_results
                result['summary'] = summary
            elif review_type == 'specific' and focus:
                review_results = {
                    focus: self._review_category(result, focus, self.review_criteria.get(focus, []))
                }
                result['review_results'] = review_results
            
            return {
                'status': 'success',
                'type': review_type,
                'target': target,
                'focus': focus if review_type == 'specific' else None,
                'result': result
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': f'Review task execution failed: {str(e)}'
            }

    def _analyze_review_task(self, task_description: str) -> str:
        """Determine the type of review task"""
        task = task_description.lower()
        
        if any(word in task for word in ['complete', 'full', 'comprehensive']):
            return 'full'
        elif any(word in task for word in ['fix', 'implement', 'apply']):
            return 'fix'
        else:
            return 'specific'

    def _create_task_description(self, base_description: str, review_type: str, target: str, focus: Optional[str] = None) -> str:
        """Create detailed task description based on type"""
        if review_type == 'full':
            return f"""
            Comprehensive Code Review Task:
            {base_description}
            
            Target: {target}
            
            Review all aspects:
            1. Code Style and Organization
            2. Functionality and Logic
            3. Performance and Efficiency
            4. Security Considerations
            5. Maintainability and Documentation
            """
        elif review_type == 'specific':
            return f"""
            Focused Code Review Task:
            {base_description}
            
            Target: {target}
            Focus Area: {focus}
            
            1. Analyze {focus} aspects in detail
            2. Identify specific improvements
            3. Provide actionable recommendations
            4. Consider impact on other areas
            """
        else:  # fix
            return f"""
            Review Fix Implementation Task:
            {base_description}
            
            Target: {target}
            
            1. Review previous findings
            2. Implement recommended fixes
            3. Verify improvements
            4. Ensure no regressions
            """

    def _create_expected_output(self, review_type: str, focus: Optional[str] = None) -> str:
        """Define expected output based on task type"""
        if review_type == 'full':
            return """
            1. Comprehensive review findings
            2. Detailed analysis per category
            3. Prioritized recommendations
            4. Summary of key issues
            """
        elif review_type == 'specific':
            return f"""
            1. Detailed analysis of {focus}
            2. Specific improvement suggestions
            3. Impact assessment
            4. Implementation recommendations
            """
        else:  # fix
            return """
            1. Implemented fixes
            2. Verification results
            3. Regression test results
            4. Updated code status
            """

    def _extract_review_target(self, task_description: str) -> str:
        """Extract the target file for review"""
        words = task_description.split()
        for i, word in enumerate(words):
            if word in ['review', 'check'] and i + 1 < len(words):
                return words[i + 1]
        return 'unknown_target'

    def _extract_review_focus(self, task_description: str) -> tuple[str, str]:
        """Extract review target and focus area"""
        target = self._extract_review_target(task_description)
        task = task_description.lower()
        
        for category in self.review_criteria.keys():
            if category in task:
                return target, category
        
        return target, 'functionality'  # Default focus

    def _review_category(self, result: Dict[str, Any], category: str, criteria: List[str]) -> Dict[str, Any]:
        """Review code against specific category criteria"""
        results = {
            'category': category,
            'findings': [],
            'suggestions': []
        }
        
        for criterion in criteria:
            finding = self._analyze_criterion(result.get('content', ''), criterion)
            if finding:
                results['findings'].append(finding)
                if 'suggestion' in finding:
                    results['suggestions'].append(finding['suggestion'])
        
        return results

    def _analyze_criterion(self, content: str, criterion: str) -> Dict[str, Any]:
        """Analyze code against a specific criterion"""
        return {
            'criterion': criterion,
            'status': 'pass',  # or 'fail'
            'details': f'Analysis for {criterion}',
            'suggestion': f'Suggestion for improving {criterion}'
        }

    def _generate_review_summary(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable summary of review results"""
        summary_parts = []
        
        for category, result in results.items():
            findings = len(result['findings'])
            suggestions = len(result['suggestions'])
            summary_parts.append(
                f"{category.capitalize()}: "
                f"{findings} finding(s), {suggestions} suggestion(s)"
            )
        
        return '\n'.join(summary_parts)
