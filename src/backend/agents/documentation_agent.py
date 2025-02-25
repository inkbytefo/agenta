from crewai import Task
from typing import Dict, Any, Optional, List
from .base_agent import VSCodeAgent
import os
import re

class DocumentationAgent(VSCodeAgent):
    """Documentation agent responsible for creating and managing code documentation"""

    def __init__(self, name: str, project_path: str, config_path: Optional[str] = None):
        super().__init__(name, project_path, config_path)
        
        # Documentation patterns for different languages
        self.doc_patterns = {
            'python': {
                'function': '"""{}\n\nArgs:\n    {}\nReturns:\n    {}\n"""',
                'class': '"""{}\n\nAttributes:\n    {}\n"""',
                'module': '"""{}\n\nThis module contains:\n{}\n"""'
            },
            'javascript': {
                'function': '/**\n * {}\n * @param {{{}}}} {}\n * @returns {{{}}}} {}\n */',
                'class': '/**\n * {}\n * @class\n * {}\n */',
                'module': '/**\n * {}\n * @module {}\n * {}\n */'
            }
        }

    async def execute(self, task: Task) -> Dict[str, Any]:
        """Execute a documentation task using CrewAI's task system
        
        Args:
            task: CrewAI Task object with task details
            
        Returns:
            Dict containing execution result and status
        """
        try:
            # Analyze the type of documentation task
            task_type = self._analyze_doc_task(task.description)
            target, doc_type = self._extract_doc_info(task.description)
            
            # Create specific task based on type
            execution_task = self.create_task(
                description=self._create_task_description(task.description, task_type, target, doc_type),
                expected_output=self._create_expected_output(task_type, doc_type)
            )
            
            # Execute the task using CrewAI's system
            result = await super().execute(execution_task)
            
            # For create/update tasks, generate documentation template
            if task_type in ['create', 'update']:
                lang = self._detect_language(target)
                if lang in self.doc_patterns:
                    template = self._generate_doc_template(target, doc_type, lang)
                    result['template'] = template
            
            return {
                'status': 'success',
                'type': task_type,
                'target': target,
                'doc_type': doc_type,
                'result': result
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': f'Documentation task execution failed: {str(e)}'
            }

    def _analyze_doc_task(self, task_description: str) -> str:
        """Determine the type of documentation task"""
        task = task_description.lower()
        
        if any(word in task for word in ['create', 'write', 'add']):
            return 'create'
        elif any(word in task for word in ['update', 'modify', 'improve']):
            return 'update'
        elif any(word in task for word in ['extract', 'get', 'read']):
            return 'extract'
        else:
            return 'unknown'

    def _create_task_description(self, base_description: str, task_type: str, target: str, doc_type: str) -> str:
        """Create detailed task description based on type"""
        if task_type == 'create':
            lang = self._detect_language(target)
            return f"""
            Documentation Creation Task:
            {base_description}
            
            Target: {target}
            Type: {doc_type}
            Language: {lang}
            
            1. Analyze the target code
            2. Identify key components to document
            3. Create comprehensive documentation
            4. Follow language-specific documentation standards
            5. Ensure clarity and completeness
            """
        elif task_type == 'update':
            return f"""
            Documentation Update Task:
            {base_description}
            
            Target: {target}
            Type: {doc_type}
            
            1. Review existing documentation
            2. Identify areas needing updates
            3. Implement documentation changes
            4. Ensure consistency with codebase
            5. Verify documentation accuracy
            """
        else:  # extract
            return f"""
            Documentation Extraction Task:
            {base_description}
            
            Target: {target}
            Type: {doc_type}
            
            1. Locate all documentation in the target
            2. Parse and extract documentation
            3. Format for readability
            4. Identify any missing documentation
            """

    def _create_expected_output(self, task_type: str, doc_type: str) -> str:
        """Define expected output based on task type"""
        if task_type == 'create':
            return f"""
            1. Complete {doc_type} documentation
            2. Documentation follows language standards
            3. All key components documented
            4. Clear and maintainable format
            """
        elif task_type == 'update':
            return f"""
            1. Updated {doc_type} documentation
            2. Maintained consistency
            3. Clear change explanations
            4. All components still documented
            """
        else:  # extract
            return f"""
            1. Extracted {doc_type} documentation
            2. Properly formatted output
            3. Documentation coverage report
            4. List of any gaps found
            """

    def _extract_doc_info(self, task_description: str) -> tuple[str, str]:
        """Extract documentation target and type from task"""
        target = self._extract_doc_target(task_description)
        task = task_description.lower()
        
        if 'class' in task:
            doc_type = 'class'
        elif 'function' in task or 'method' in task:
            doc_type = 'function'
        else:
            doc_type = 'module'
            
        return target, doc_type

    def _extract_doc_target(self, task_description: str) -> str:
        """Extract documentation target from task"""
        words = task_description.split()
        for i, word in enumerate(words):
            if word in ['document', 'documentation'] and i + 1 < len(words):
                return words[i + 1]
        return 'unknown_target'

    def _detect_language(self, filename: str) -> str:
        """Detect programming language from file extension"""
        ext = os.path.splitext(filename)[1].lower()
        
        if ext in ['.py']:
            return 'python'
        elif ext in ['.js', '.ts']:
            return 'javascript'
        else:
            return 'unknown'

    def _generate_doc_template(self, target: str, doc_type: str, lang: str) -> str:
        """Generate documentation template based on language and type"""
        patterns = self.doc_patterns.get(lang, {})
        template = patterns.get(doc_type, '')
        
        if doc_type == 'function':
            return template.format(
                'Function description',
                'param_type param_name: Parameter description',
                'return_type: Return value description'
            )
        elif doc_type == 'class':
            return template.format(
                'Class description',
                'attribute_name (type): Attribute description'
            )
        else:  # module
            return template.format(
                'Module description',
                '- List of contents'
            )

    def _extract_documentation(self, content: str) -> List[str]:
        """Extract existing documentation from file content"""
        docs = []
        
        # Extract Python docstrings
        python_docs = re.findall(r'"""[\s\S]*?"""', content)
        docs.extend(python_docs)
        
        # Extract JavaScript/TypeScript JSDoc comments
        js_docs = re.findall(r'/\*\*[\s\S]*?\*/', content)
        docs.extend(js_docs)
        
        return docs
