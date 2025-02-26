import { useEffect, useState } from 'react';
import { useStore } from './store';
import AgentPanel from './components/AgentPanel';
import DebugPanel from './components/DebugPanel';
import LLMSettingsPanel from './components/LLMSettingsPanel';
import StatusBar from './components/StatusBar';
import styles from './App.module.css'; // Import CSS Module
import { FaCog, FaTasks, FaBug, FaBrain } from 'react-icons/fa';

function App() {
  const {
    isConnected,
    checkConnection,
    fetchLLMConfigs,
    fetchLLMProviders,
  } = useStore();

  useEffect(() => {
    // Initial data loading
    const initializeApp = async () => {
      await checkConnection();
      if (isConnected) {
        await Promise.all([
          fetchLLMConfigs(),
          fetchLLMProviders(),
        ]);
      }
    };

    initializeApp();

    // Set up periodic connection checks
    const connectionInterval = setInterval(checkConnection, 30000);

    return () => {
      clearInterval(connectionInterval);
    };
  }, [checkConnection, isConnected, fetchLLMConfigs, fetchLLMProviders]);

  // Tabs configuration
  const tabs = [
    { id: 'agent', label: 'Agent', component: AgentPanel, icon: FaBrain },
    { id: 'debug', label: 'Debug Console', component: DebugPanel, icon: FaBug },
    { id: 'settings', label: 'LLM Settings', component: LLMSettingsPanel, icon: FaCog },
  ] as const;

  const [activeTab, setActiveTab] = useState<typeof tabs[number]['id']>('agent');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className={styles.appContainer}>
      <header className={styles.appHeader}>
        <div className={styles.logo}>
          {/* Replace with your logo */}
          CrewAI
        </div>
        <nav className={styles.topNav}>
          {/* Top navigation items if needed */}
        </nav>
      </header>

      <div className={styles.mainContent}>
        <aside className={`${styles.sidebar} ${isSidebarOpen ? styles.open : ''}`}>
          <button className={styles.sidebarToggle} onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
            {isSidebarOpen ? '<<' : '>>'}
          </button>
          <ul className={styles.sidebarNav}>
            {tabs.map(({ id, label, icon: Icon }) => (
              <li key={id} className={`${styles.sidebarItem} ${activeTab === id ? styles.active : ''}`}>
                <button onClick={() => setActiveTab(id)} className={styles.sidebarButton}>
                  <span className={styles.sidebarIcon}>{<Icon />}</span>
                  {isSidebarOpen && <span className={styles.sidebarLabel}>{label}</span>}
                </button>
              </li>
            ))}
          </ul>
        </aside>

        <main className={styles.appContent}>
          {tabs.map(({ id, component: Component }) => (
            activeTab === id && <Component key={id} />
          ))}
        </main>
      </div>

      <StatusBar />
    </div>
  );
}

export default App;
