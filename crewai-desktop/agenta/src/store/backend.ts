import { invoke } from '@tauri-apps/api/core';

interface BackendResponse {
  status: 'success' | 'error';
  data?: any;
  error?: string;
}

interface BackendState {
  isConnected: boolean;
  connecting: boolean;
  error: string | null;
  connect: () => Promise<void>;
  disconnect: () => Promise<void>;
  checkConnection: () => Promise<void>;
  sendCommand: (command: string, args?: any) => Promise<any>;
}

export const createBackendSlice = (set: any, get: any): BackendState => ({
  isConnected: false,
  connecting: false,
  error: null,

  connect: async () => {
    try {
      set({ connecting: true, error: null });
      await invoke('start_backend');
      set({ isConnected: true });
    } catch (error) {
      set({ error: String(error) });
      console.error('Failed to connect to backend:', error);
    } finally {
      set({ connecting: false });
    }
  },

  disconnect: async () => {
    try {
      await invoke('stop_backend');
      set({ isConnected: false });
    } catch (error) {
      set({ error: String(error) });
      console.error('Failed to disconnect from backend:', error);
    }
  },

  checkConnection: async () => {
    try {
      const isRunning = await invoke<boolean>('check_backend');
      set({ isConnected: isRunning, error: null });
    } catch (error) {
      set({ isConnected: false, error: String(error) });
      console.error('Failed to check backend connection:', error);
    }
  },

  sendCommand: async (command: string, args: any = {}) => {
    if (!get().isConnected) {
      throw new Error('Not connected to backend');
    }

    try {
      const response = await invoke<BackendResponse>('send_to_backend', {
        command,
        args,
      });

      if (response.error) {
        throw new Error(response.error);
      }

      return response.data;
    } catch (error) {
      console.error(`Failed to execute command ${command}:`, error);
      throw error;
    }
  },
});