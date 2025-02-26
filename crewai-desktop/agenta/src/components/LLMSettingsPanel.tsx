import { useState, useEffect } from 'react';
import { useStore } from '../store';
import styles from './LLMSettingsPanel.module.css';

interface LLMConfig {
  provider: string;
  model: string;
  apiKey?: string;
  settings?: Record<string, any>;
}

const LLMSettingsPanel = () => {
  const {
    isConnected,
    llmConfigs,
    llmProviders,
    fetchLLMConfigs,
    fetchLLMProviders,
    saveLLMConfig,
  } = useStore();

  const [selectedProvider, setSelectedProvider] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [status, setStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Fetch configs and providers on mount
  useEffect(() => {
    if (isConnected) {
      fetchLLMConfigs();
      fetchLLMProviders();
    }
  }, [isConnected, fetchLLMConfigs, fetchLLMProviders]);

  const handleProviderChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const provider = e.target.value;
    setSelectedProvider(provider);
    setSelectedModel(''); // Reset model when provider changes
    setApiKey(''); // Reset API key when provider changes
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProvider || !selectedModel) {
      setStatus({
        type: 'error',
        message: 'Please select both provider and model',
      });
      return;
    }

    const config: LLMConfig = {
      provider: selectedProvider,
      model: selectedModel,
      ...(apiKey && { apiKey }),
    };

    try {
      await saveLLMConfig(config);
      setStatus({
        type: 'success',
        message: 'Configuration saved successfully',
      });
      // Reset form
      setSelectedProvider('');
      setSelectedModel('');
      setApiKey('');
    } catch (error) {
      setStatus({
        type: 'error',
        message: `Failed to save configuration: ${error}`,
      });
    }
  };

  if (!isConnected) {
    return (
      <div className={styles['llm-settings']}>
        <div className={styles['error-message']}>
          Not connected to backend server
        </div>
      </div>
    );
  }

  return (
    <div className={styles['llm-settings']}>
      {/* Current Configurations */}
      <section className={styles.section}>
        <div className={styles['section-header']}>
          <h2>Current Configurations</h2>
        </div>
        <div className={styles['configs-list']}>
          {Object.entries(llmConfigs).length === 0 ? (
            <div>No configurations found</div>
          ) : (
            Object.entries(llmConfigs).map(([provider, config]) => (
              <div key={provider} className={styles['config-item']}>
                <div className={styles['config-details']}>
                  <span className={styles['config-provider']}>{provider}</span>
                  <span className={styles['config-model']}>{config.model}</span>
                </div>
                <button
                  className={styles['delete-button']}
                  onClick={() => {
                    // TODO: Implement delete functionality
                    console.log('Delete config:', provider);
                  }}
                >
                  Delete
                </button>
              </div>
            ))
          )}
        </div>
      </section>

      {/* New Configuration Form */}
      <section className={styles.section}>
        <div className={styles['section-header']}>
          <h2>Add New Configuration</h2>
        </div>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles['form-group']}>
            <label className={styles.label} htmlFor="provider">
              Provider
            </label>
            <select
              id="provider"
              className={styles.select}
              value={selectedProvider}
              onChange={handleProviderChange}
              required
            >
              <option value="">Select Provider</option>
              {Object.entries(llmProviders).map(([id, provider]) => (
                <option key={id} value={id}>
                  {provider.name}
                </option>
              ))}
            </select>
          </div>

          <div className={styles['form-group']}>
            <label className={styles.label} htmlFor="model">
              Model
            </label>
            <select
              id="model"
              className={styles.select}
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              required
              disabled={!selectedProvider}
            >
              <option value="">Select Model</option>
              {selectedProvider &&
                llmProviders[selectedProvider]?.models.map((model: string) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
            </select>
          </div>

          {selectedProvider && llmProviders[selectedProvider]?.requiresApiKey && (
            <div className={styles['form-group']}>
              <label className={styles.label} htmlFor="apiKey">
                API Key
              </label>
              <input
                id="apiKey"
                type="password"
                className={styles.input}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                required
              />
              <div className={styles['api-key-info']}>
                Your API key will be securely stored
              </div>
            </div>
          )}

          <button
            type="submit"
            className={styles['save-button']}
            disabled={!selectedProvider || !selectedModel}
          >
            Save Configuration
          </button>
        </form>
      </section>

      {status && (
        <div
          className={
            status.type === 'success'
              ? styles['success-message']
              : styles['error-message']
          }
        >
          {status.message}
        </div>
      )}
    </div>
  );
};

export default LLMSettingsPanel;