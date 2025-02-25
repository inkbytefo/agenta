export interface DebugEvent {
    timestamp: string;
    event_type: string;
    agent: string;
    action: string;
    details: Record<string, any>;
    status: string;
    correlation_id?: string;
}

export interface DebugResponse {
    type: 'debug_response';
    events: DebugEvent[];
    status?: string;
    message?: string;
    correlation_id?: string;
}

export interface TaskRequest {
    type: 'task';
    content: string;
    correlation_id?: string;
}

export interface ToolRequest {
    type: 'tool_request';
    tool: string;
    params: Record<string, any>;
    correlation_id?: string;
}

export interface DebugRequest {
    type: 'debug_request';
    action: 'get_events' | 'clear_logs';
    params?: Record<string, any>;
    correlation_id?: string;
}

export interface LLMRequest {
    type: 'llm_request';
    action: 'get_configs' | 'get_providers' | 'get_models' | 'save_config';
    provider?: string;
    agentName?: string;
    config?: LLMConfig;
    correlation_id?: string;
}

export interface LLMConfig {
    provider_name: string;
    model_name: string;
    api_key?: string;
    temperature: number;
    max_tokens?: number;
    additional_config?: Record<string, any>;
}

export interface LLMResponse {
    type: 'llm_response';
    configs?: Record<string, LLMConfig>;
    providers?: {
        [key: string]: {
            models: string[];
            description?: string;
        }
    };
    models?: string[];
    status: string;
    error?: string;
    correlation_id?: string;
}

export interface AgentResponse {
    type: 'agent_response';
    status: string;
    content?: any;
    error?: string;
    correlation_id?: string;
}

export interface ToolResponse {
    type: 'tool_response';
    status: string;
    result: Record<string, any>;
    correlation_id?: string;
}

export interface ErrorResponse {
    type: 'error';
    error: string;
    correlation_id?: string;
}

export type Message = 
    | TaskRequest
    | ToolRequest
    | DebugRequest
    | LLMRequest
    | AgentResponse
    | ToolResponse
    | DebugResponse
    | LLMResponse
    | ErrorResponse;
