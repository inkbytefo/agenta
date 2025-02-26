import { invoke } from '@tauri-apps/api/core';

// Command Types
export type CommandType =
  | 'handle_task'
  | 'get_mode'
  | 'get_llm_status'
  | 'get_debug_events'
  | 'clear_debug_logs'
  | 'get_llm_providers'
  | 'get_llm_configs'
  | 'save_llm_config';

// Response Types
export interface ApiResponse<T = any> {
  status: 'success' | 'error';
  data?: T;
  error?: string;
}

export interface LLMProvider {
  name: string;
  models: string[];
  requiresApiKey: boolean;
}

export interface LLMConfig {
  provider: string;
  model: string;
  apiKey: string;
  [key: string]: any;
}

export interface DebugEvent {
  timestamp: string;
  level: string;
  message: string;
  details?: Record<string, any>;
}

// API Service
class ApiService {
  private async sendCommand<T = any>(
    command: CommandType,
    args: Record<string, any> = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await invoke<string>('send_command', {
        command,
        args: JSON.stringify(args),
      });
      
      return JSON.parse(response) as ApiResponse<T>;
    } catch (error) {
      console.error('API Error:', error);
      return {
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  // Task Management
  async handleTask(task: string) {
    return this.sendCommand('handle_task', { task });
  }

  // Mode Management
  async getCurrentMode() {
    return this.sendCommand<{ mode: string }>('get_mode');
  }

  // LLM Management
  async getLLMStatus() {
    return this.sendCommand('get_llm_status');
  }

  async getLLMProviders() {
    return this.sendCommand<Record<string, LLMProvider>>('get_llm_providers');
  }

  async getLLMConfigs() {
    return this.sendCommand<Record<string, LLMConfig>>('get_llm_configs');
  }

  async saveLLMConfig(config: LLMConfig) {
    return this.sendCommand('save_llm_config', config);
  }

  // Debug Management
  async getDebugEvents() {
    return this.sendCommand<DebugEvent[]>('get_debug_events');
  }

  async clearDebugLogs() {
    return this.sendCommand('clear_debug_logs');
  }
}

export const api = new ApiService();