import { useEffect } from 'react';
import { useStore } from '../store';
import styles from './StatusBar.module.css';

const StatusBar = () => {
  const {
    isConnected,
    currentMode,
    llmStatus,
    checkConnection,
    fetchLLMStatus,
  } = useStore();

  useEffect(() => {
    // Initial status check
    checkConnection();
    fetchLLMStatus();

    // Set up periodic status checks
    const connectionInterval = setInterval(checkConnection, 30000);
    const llmStatusInterval = setInterval(fetchLLMStatus, 30000);

    return () => {
      clearInterval(connectionInterval);
      clearInterval(llmStatusInterval);
    };
  }, [checkConnection, fetchLLMStatus]);

  const getLLMStatusClass = (status: string): string => {
    switch (status.toLowerCase()) {
      case 'ready':
        return styles.ready;
      case 'error':
        return styles.error;
      case 'loading':
        return styles.loading;
      default:
        return '';
    }
  };

  return (
    <div className={styles['status-bar']}>
      {/* Connection Status */}
      <div className={styles['connection-status']}>
        <span
          className={`${styles['status-indicator']} ${
            isConnected ? styles.connected : styles.disconnected
          }`}
        />
        {isConnected ? 'Connected' : 'Disconnected'}
      </div>

      <div className={styles.divider} />

      {/* Mode Status */}
      <div className={styles['mode-status']}>
        <span className={styles['mode-label']}>Mode:</span>
        <span className={styles['mode-value']}>{currentMode}</span>
      </div>

      <div className={styles.divider} />

      {/* LLM Status */}
      <div className={styles['llm-status']}>
        <span className={styles['llm-label']}>LLM:</span>
        <span className={`${styles['llm-value']} ${getLLMStatusClass(llmStatus)}`}>
          {llmStatus || 'Not Configured'}
        </span>
      </div>
    </div>
  );
};

export default StatusBar;