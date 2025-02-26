import { create } from 'zustand';
import { createBackendSlice } from './backend';

export interface LLMConfig {
  provider: string;
  model: string;
  apiKey?: string;
  settings?: Record<string, any>;
}

export interface DebugEvent {
  timestamp: string;
  level: string;
  message: string;
  details?: Record<string, any>;
}

interface StoreState {
  // Backend state
  isConnected: boolean;
  connecting: boolean;
  error: string | null;
  connect: () => Promise<void>;
  disconnect: () => Promise<void>;
  checkConnection: () => Promise<void>;
  sendCommand: (command: string, args?: any) => Promise<any>;

  // Task state
  taskStatus: string;
  sendTask: (task: string) => Promise<void>;

  // Application state
  currentMode: string;
  setMode: (mode: string) => Promise<void>;
  debugEvents: DebugEvent[];
  llmConfigs: Record<string, LLMConfig>;
  llmProviders: Record<string, any>;
  llmStatus: string;

  // Actions
  fetchDebugEvents: () => Promise<void>;
  clearDebugLogs: () => Promise<void>;
  fetchLLMConfigs: () => Promise<void>;
  fetchLLMProviders: () => Promise<void>;
  fetchLLMStatus: () => Promise<void>;
  saveLLMConfig: (config: LLMConfig) => Promise<void>;
}

export const useStore = create<StoreState>((set, get) => ({
  ...createBackendSlice(set, get),

  // Application state
  currentMode: 'default',
  debugEvents: [],
  llmConfigs: {},
  llmProviders: {},
  llmStatus: '',
  taskStatus: '',

  // Task management
  sendTask: async (task: string) => {
    try {
      const response = await get().sendCommand('handle_task', { task });
      set({ taskStatus: response.status || 'Task sent successfully' });
    } catch (error) {
      set({ taskStatus: `Error: ${error}` });
      console.error('Failed to send task:', error);
    }
  },

  // Mode management
  setMode: async (mode: string) => {
    try {
      await get().sendCommand('set_mode', { mode });
      set({ currentMode: mode });
    } catch (error) {
      console.error('Failed to set mode:', error);
    }
  },

  // Debug events management
  fetchDebugEvents: async () => {
    try {
      const events = await get().sendCommand('get_debug_events');
      set({ debugEvents: events });
    } catch (error) {
      console.error('Failed to fetch debug events:', error);
    }
  },

  clearDebugLogs: async () => {
    try {
      await get().sendCommand('clear_debug_logs');
      set({ debugEvents: [] });
    } catch (error) {
      console.error('Failed to clear debug logs:', error);
    }
  },

  // LLM configuration management
  fetchLLMConfigs: async () => {
    try {
      const configs = await get().sendCommand('get_llm_configs');
      set({ llmConfigs: configs });
    } catch (error) {
      console.error('Failed to fetch LLM configs:', error);
    }
  },

  fetchLLMProviders: async () => {
    try {
      const providers = await get().sendCommand('get_llm_providers');
      set({ llmProviders: providers });
    } catch (error) {
      console.error('Failed to fetch LLM providers:', error);
    }
  },

  fetchLLMStatus: async () => {
    try {
      const response = await get().sendCommand('get_llm_status');
      set({ llmStatus: response.status });
    } catch (error) {
      console.error('Failed to fetch LLM status:', error);
      set({ llmStatus: 'error' });
    }
  },

  saveLLMConfig: async (config: LLMConfig) => {
    try {
      await get().sendCommand('save_llm_config', { config });
      await get().fetchLLMConfigs();
    } catch (error) {
      console.error('Failed to save LLM config:', error);
      throw error;
    }
  },
}));