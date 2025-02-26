import { useState, useEffect } from 'react';
import { useStore } from '../store';
import styles from './AgentPanel.module.css';

const AgentPanel = () => {
  const [task, setTask] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const {
    isConnected,
    taskStatus,
    currentMode,
    sendTask,
    checkConnection,
  } = useStore();

  useEffect(() => {
    // Check connection status on mount and every 30 seconds
    checkConnection();
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, [checkConnection]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!task.trim() || !isConnected) return;

    setIsLoading(true);
    try {
      await sendTask(task.trim());
      setTask(''); // Clear input on successful submission
    } catch (error) {
      console.error('Failed to send task:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles['agent-panel']}>
      <div className={styles['panel-header']}>
        <h2>Agent Interface</h2>
        <div className={styles['connection-status']}>
          <span className={`${styles['status-indicator']} ${
            isConnected ? styles.connected : styles.disconnected
          }`} />
          {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      </div>

      <div className={styles['mode-indicator']}>
        Current Mode: <span className={styles['mode-name']}>{currentMode}</span>
      </div>

      <form onSubmit={handleSubmit} className={styles['task-form']}>
        <div className={styles['input-group']}>
          <textarea
            value={task}
            onChange={(e) => setTask(e.target.value)}
            placeholder="Enter your task..."
            rows={3}
            className={styles['task-input']}
            disabled={!isConnected || isLoading}
          />
          <div className={styles['input-help']}>
            Press Shift + Enter for new line, Enter to submit
          </div>
        </div>

        <button
          type="submit"
          className={styles['submit-button']}
          disabled={!isConnected || !task.trim() || isLoading}
        >
          {isLoading ? 'Submitting...' : 'Submit Task'}
        </button>
      </form>

      {taskStatus && (
        <div
          className={`${styles['status-output']} ${
            taskStatus.startsWith('Error') ? styles.error : styles.success
          }`}
        >
          {taskStatus.startsWith('Error') ? (
            <pre style={{ color: 'red' }}>{taskStatus}</pre>
          ) : (
            <pre style={{ color: 'green' }}>{taskStatus}</pre>
          )}
        </div>
      )}
    </div>
  );
};

export default AgentPanel;
