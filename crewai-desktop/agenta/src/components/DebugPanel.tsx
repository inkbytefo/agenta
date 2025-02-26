import { useEffect, useCallback } from 'react';
import { useStore } from '../store';
import styles from './DebugPanel.module.css';

const DebugPanel = () => {
  const {
    debugEvents,
    fetchDebugEvents,
    clearDebugLogs,
    isConnected,
  } = useStore();

  // Fetch debug events on mount and when connection status changes
  useEffect(() => {
    if (isConnected) {
      fetchDebugEvents();
      // Set up polling for new events
      const interval = setInterval(fetchDebugEvents, 5000);
      return () => clearInterval(interval);
    }
  }, [isConnected, fetchDebugEvents]);

  const handleRefresh = useCallback(() => {
    fetchDebugEvents();
  }, [fetchDebugEvents]);

  const handleClear = useCallback(() => {
    clearDebugLogs();
  }, [clearDebugLogs]);

  // Format timestamp to local time
  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  if (!isConnected) {
    return (
      <div className={styles['debug-panel']}>
        <div className={styles['empty-state']}>
          Not connected to backend server
        </div>
      </div>
    );
  }

  return (
    <div className={styles['debug-panel']}>
      <div className={styles.toolbar}>
        <button
          onClick={handleRefresh}
          className={styles['refresh-button']}
        >
          Refresh
        </button>
        <button
          onClick={handleClear}
          className={styles['clear-button']}
        >
          Clear Logs
        </button>
      </div>

      <div className={styles['events-container']}>
        {debugEvents.length === 0 ? (
          <div className={styles['empty-state']}>
            No debug events to display
          </div>
        ) : (
          debugEvents.map((event, index) => (
            <div
              key={`${event.timestamp}-${index}`}
              className={`${styles.event} ${styles[event.level.toLowerCase()]}`}
            >
              <div className={styles['event-header']}>
                <span className={styles.timestamp}>
                  {formatTimestamp(event.timestamp)}
                </span>
                <span className={`${styles.level} ${styles[event.level.toLowerCase()]}`}>
                  {event.level}
                </span>
              </div>
              <div className={styles.message}>{event.message}</div>
              {event.details && (
                <pre className={styles.details}>
                  {JSON.stringify(event.details, null, 2)}
                </pre>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default DebugPanel;