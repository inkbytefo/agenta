import React, { useState, useCallback } from 'react';
import styles from './TaskExecution.module.css';

interface TaskTemplate {
  id: string;
  name: string;
  description: string;
}

interface TaskFormData {
  name: string;
  template: string;
  parameters: string;
}

interface ValidationErrors {
  name?: string;
  template?: string;
  parameters?: string;
}

const TASK_TEMPLATES: TaskTemplate[] = [
  { 
    id: 'todo',
    name: 'To-Do List',
    description: 'Create a task list with priorities and deadlines'
  },
  {
    id: 'report',
    name: 'Generate Report',
    description: 'Generate a detailed analysis report'
  }
];

const TaskExecution: React.FC = () => {
  const [formData, setFormData] = useState<TaskFormData>({
    name: '',
    template: 'default',
    parameters: ''
  });
  
  const [errors, setErrors] = useState<ValidationErrors>({});
  const [isExecuting, setIsExecuting] = useState(false);
  const [output, setOutput] = useState<string>('');

  const validateForm = (): boolean => {
    const newErrors: ValidationErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Task name is required';
    }
    
    if (formData.template === 'default') {
      newErrors.template = 'Please select a template';
    }
    
    if (!formData.parameters.trim()) {
      newErrors.parameters = 'Parameters are required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = event.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name as keyof ValidationErrors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const handleExecute = async () => {
    if (!validateForm()) return;

    setIsExecuting(true);
    setOutput('Executing task...\n');

    try {
      // Simulate task execution
      await new Promise(resolve => setTimeout(resolve, 2000));
      setOutput(prev => prev + `Task "${formData.name}" executed successfully.`);
    } catch (error) {
      setOutput(prev => prev + `Error: ${error instanceof Error ? error.message : 'Unknown error occurred'}`);
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className={styles.taskExecution}>
      <h1 className={styles.heading}>Execute Task</h1>
      
      <div className={styles.inputGroup}>
        <label htmlFor="taskName" className={styles.label}>
          Task Name:
        </label>
        <input 
          id="taskName"
          name="name"
          type="text" 
          className={styles.inputField}
          placeholder="Enter task name"
          value={formData.name}
          onChange={handleInputChange}
          aria-invalid={!!errors.name}
          aria-describedby={errors.name ? 'nameError' : undefined}
        />
        {errors.name && (
          <span id="nameError" className={styles.error} role="alert">
            {errors.name}
          </span>
        )}
      </div>

      <div className={styles.inputGroup}>
        <label htmlFor="taskTemplate" className={styles.label}>
          Task Template:
        </label>
        <select 
          id="taskTemplate"
          name="template"
          className={styles.dropdown}
          value={formData.template}
          onChange={handleInputChange}
          aria-invalid={!!errors.template}
          aria-describedby={errors.template ? 'templateError' : undefined}
        >
          <option value="default">Select a template</option>
          {TASK_TEMPLATES.map(template => (
            <option key={template.id} value={template.id}>
              {template.name}
            </option>
          ))}
        </select>
        {errors.template && (
          <span id="templateError" className={styles.error} role="alert">
            {errors.template}
          </span>
        )}
      </div>

      <div className={styles.inputGroup}>
        <label htmlFor="taskParams" className={styles.label}>
          Parameters:
        </label>
        <textarea 
          id="taskParams"
          name="parameters"
          className={styles.inputField}
          rows={4}
          placeholder="Enter task parameters"
          value={formData.parameters}
          onChange={handleInputChange}
          aria-invalid={!!errors.parameters}
          aria-describedby={errors.parameters ? 'paramsError' : undefined}
        />
        {errors.parameters && (
          <span id="paramsError" className={styles.error} role="alert">
            {errors.parameters}
          </span>
        )}
      </div>

      <button 
        className={`${styles.button} ${isExecuting ? styles.loading : ''}`}
        onClick={handleExecute}
        disabled={isExecuting}
        aria-busy={isExecuting}
      >
        {isExecuting && (
          <svg 
            className={styles.spinner} 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2"
          >
            <circle cx="12" cy="12" r="10" />
          </svg>
        )}
        {isExecuting ? 'Executing...' : 'Execute'}
      </button>

      <div 
        className={styles.outputArea}
        role="log"
        aria-live="polite"
        aria-label="Task execution output"
      >
        <h3 className={styles.outputHeading}>Output:</h3>
        <div className={styles.outputContent}>
          {output || 'No output yet. Execute a task to see results.'}
        </div>
      </div>
    </div>
  );
};

export default TaskExecution;