import { create } from 'zustand';
import { api, LLMConfig, LLMProvider, DebugEvent } from '../services/api';

interface StoreState {
  // Backend state
  isConnected: boolean;
  connecting: boolean;
  error: string | null;

  // Task state
  taskStatus: string;
  currentTask: string | null;
  sendTask: (task: string) => Promise<void>;

  // Application state
  currentMode: string;
  debugEvents: DebugEvent[];
  llmConfigs: Record<string, LLMConfig>;
  llmProviders: Record<string, LLMProvider>;
  llmStatus: 'idle' | 'loading' | 'ready' | 'error';

  // Connection management
  checkConnection: () => Promise<void>;
  initialize: () => Promise<void>;

  // Mode management
  setMode: (mode: string) => Promise<void>;

  // Debug management
  fetchDebugEvents: () => Promise<void>;
  clearDebugLogs: () => Promise<void>;

  // LLM configuration management
  fetchLLMConfigs: () => Promise<void>;
  fetchLLMProviders: () => Promise<void>;
  fetchLLMStatus: () => Promise<void>;
  saveLLMConfig: (config: LLMConfig) => Promise<void>;
}

export const useStore = create<StoreState>((set, get) => ({
  // Initial state
  isConnected: false,
  connecting: false,
  error: null,
  currentMode: 'default',
  debugEvents: [],
  llmConfigs: {},
  llmProviders: {},
  llmStatus: 'idle',
  taskStatus: '',
  currentTask: null,

  // Connection management
  checkConnection: async () => {
    try {
      set({ connecting: true });
      const response = await api.getLLMStatus();
      set({ 
        isConnected: response.status === 'success',
        error: response.error || null,
        connecting: false
      });
    } catch (error) {
      set({ 
        isConnected: false, 
        error: error instanceof Error ? error.message : 'Connection failed',
        connecting: false
      });
    }
  },

  initialize: async () => {
    await get().checkConnection();
    if (get().isConnected) {
      await Promise.all([
        get().fetchLLMConfigs(),
        get().fetchLLMProviders(),
        get().fetchLLMStatus(),
        get().fetchDebugEvents()
      ]);
    }
  },

  // Task management
  sendTask: async (task: string) => {
    try {
      set({ taskStatus: 'sending', currentTask: task });
      const response = await api.handleTask(task);
      set({
        taskStatus: response.status === 'success' ? 'completed' : 'error',
        error: response.error || null
      });
    } catch (error) {
      set({
        taskStatus: 'error',
        error: error instanceof Error ? error.message : 'Failed to send task'
      });
    }
  },

  // Mode management
  setMode: async (mode: string) => {
    const response = await api.getCurrentMode();
    if (response.status === 'success') {
      set({ currentMode: mode });
    }
  },

  // Debug events management
  fetchDebugEvents: async () => {
    const response = await api.getDebugEvents();
    if (response.status === 'success' && response.data) {
      set({ debugEvents: response.data });
    }
  },

  clearDebugLogs: async () => {
    const response = await api.clearDebugLogs();
    if (response.status === 'success') {
      set({ debugEvents: [] });
    }
  },

  // LLM configuration management
  fetchLLMConfigs: async () => {
    const response = await api.getLLMConfigs();
    if (response.status === 'success' && response.data) {
      set({ llmConfigs: response.data });
    }
  },

  fetchLLMProviders: async () => {
    const response = await api.getLLMProviders();
    if (response.status === 'success' && response.data) {
      set({ llmProviders: response.data });
    }
  },

  fetchLLMStatus: async () => {
    const response = await api.getLLMStatus();
    if (response.status === 'success') {
      set({ llmStatus: 'ready' });
    } else {
      set({ llmStatus: 'error' });
    }
  },

  saveLLMConfig: async (config: LLMConfig) => {
    const response = await api.saveLLMConfig(config);
    if (response.status === 'success') {
      await get().fetchLLMConfigs();
    } else {
      throw new Error(response.error || 'Failed to save LLM config');
    }
  }
}));