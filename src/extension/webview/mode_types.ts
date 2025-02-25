export interface ModeResponse {
    mode: string;
    description: string;
    status?: string;
    config?: ModeConfig;
}

export interface ModeSwitchResult {
    status: string;
    message: string;
    description: string;
    error?: string;
    config?: ModeConfig;
}

export interface ModeConfig {
    allow_file_operations: boolean;
    allow_execution: boolean;
    require_confirmation: boolean;
    max_tokens?: number;
    temperature?: number;
}

export interface ModeMessage {
    type: 'getMode' | 'switchMode' | 'updateMode';
    mode?: string;
    description?: string;
}
