import * as vscode from 'vscode';
import { DebugPanel } from './webview/debug_panel';
import { AgentPanel } from './webview/panel';
import { LLMSettingsPanel } from './webview/llm_settings_panel';
import {
    DebugResponse,
    Message,
    LLMConfig,
    LLMResponse,
    LLMRequest,
    APIKeyStorage
} from './webview/types';

// Secret storage keys
const API_KEY_PREFIX = 'agenta.apiKey.';
const PROVIDER_LIST_KEY = 'agenta.providers';

// API key storage wrapper
export class SecureAPIKeyStorage implements APIKeyStorage {
    private context: vscode.ExtensionContext;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
    }

    async storeAPIKey(provider: string, key: string): Promise<void> {
        await this.context.secrets.store(`${API_KEY_PREFIX}${provider}`, key);
        // Update provider list in global state
        const providers = this.context.globalState.get<string[]>(PROVIDER_LIST_KEY, []);
        if (!providers.includes(provider)) {
            providers.push(provider);
            await this.context.globalState.update(PROVIDER_LIST_KEY, providers);
        }
    }

    async getAPIKey(provider: string): Promise<string | undefined> {
        return await this.context.secrets.get(`${API_KEY_PREFIX}${provider}`);
    }

    async deleteAPIKey(provider: string): Promise<void> {
        await this.context.secrets.delete(`${API_KEY_PREFIX}${provider}`);
        // Update provider list
        const providers = this.context.globalState.get<string[]>(PROVIDER_LIST_KEY, []);
        const updatedProviders = providers.filter(p => p !== provider);
        await this.context.globalState.update(PROVIDER_LIST_KEY, updatedProviders);
    }

    async listProviders(): Promise<string[]> {
        return this.context.globalState.get<string[]>(PROVIDER_LIST_KEY, []);
    }
}

export function activate(context: vscode.ExtensionContext) {
    // Initialize secure storage
    const apiKeyStorage = new SecureAPIKeyStorage(context);
    // Register debug panel commands
    context.subscriptions.push(
        vscode.commands.registerCommand('crewai.openDebugConsole', () => {
            DebugPanel.createOrShow(context.extensionUri);
        }),
        
        vscode.commands.registerCommand('crewai.getDebugEvents', async (params) => {
            try {
                const response = await vscode.commands.executeCommand('crewai.sendMessage', {
                    type: 'debug_request',
                    action: 'get_events',
                    params
                }) as DebugResponse;

                if (response.type !== 'debug_response') {
                    throw new Error('Invalid response type');
                }
                
                if (DebugPanel.currentPanel) {
                    DebugPanel.currentPanel.updateEvents(response.events);
                }
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to get debug events: ${error}`);
            }
        }),
        
        vscode.commands.registerCommand('crewai.clearDebugLogs', async () => {
            try {
                await vscode.commands.executeCommand('crewai.sendMessage', {
                    type: 'debug_request',
                    action: 'clear_logs'
                });
                vscode.window.showInformationMessage('Debug logs cleared');
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to clear debug logs: ${error}`);
            }
        })
    );

    // Register command to open agent panel
    context.subscriptions.push(
        vscode.commands.registerCommand('crewai.openAgent', () => {
            AgentPanel.createOrShow(context.extensionUri);
        })
    );

    // Register command to send task to agent
    context.subscriptions.push(
        vscode.commands.registerCommand('crewai.sendTask', async () => {
            const task = await vscode.window.showInputBox({
                prompt: 'Enter your task',
                placeHolder: 'e.g., Create a new file named example.js'
            });

            if (task) {
                AgentPanel.currentPanel?.sendTaskToAgent(task);
            }
        })
    );

    // Register LLM settings commands
    context.subscriptions.push(
        vscode.commands.registerCommand('crewai.openLLMSettings', () => {
            LLMSettingsPanel.render(context.extensionUri, context);
        }),

        vscode.commands.registerCommand('crewai.getLLMConfigs', async () => {
            try {
                const response = await vscode.commands.executeCommand('crewai.sendMessage', {
                    type: 'llm_request',
                    action: 'get_configs'
                } as LLMRequest) as LLMResponse;
                return response.configs || {};
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to get LLM configurations: ${error}`);
                return {};
            }
        }),

        vscode.commands.registerCommand('crewai.getLLMProviders', async () => {
            try {
                const response = await vscode.commands.executeCommand('crewai.sendMessage', {
                    type: 'llm_request',
                    action: 'get_providers'
                } as LLMRequest) as LLMResponse;
                return response.providers || {};
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to get LLM providers: ${error}`);
                return {};
            }
        }),

        vscode.commands.registerCommand('crewai.getLLMModels', async (provider: string) => {
            try {
                const response = await vscode.commands.executeCommand('crewai.sendMessage', {
                    type: 'llm_request',
                    action: 'get_models',
                    provider: provider
                } as LLMRequest) as LLMResponse;
                return response.models || [];
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to get models for ${provider}: ${error}`);
                return [];
            }
        }),

        vscode.commands.registerCommand('crewai.saveLLMConfig', async (agentName: string, config: LLMConfig) => {
            try {
                const response = await vscode.commands.executeCommand('crewai.sendMessage', {
                    type: 'llm_request',
                    action: 'save_config',
                    agentName: agentName,
                    config: config
                } as LLMRequest) as LLMResponse;
                return true;
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to save LLM configuration: ${error}`);
                return false;
            }
        })
    );

    // Register mode control commands
    context.subscriptions.push(
        vscode.commands.registerCommand('crewai.getMode', async () => {
            try {
                const response = await vscode.commands.executeCommand('crewai.sendMessage', {
                    type: 'mode_request',
                    action: 'get_mode'
                });
                return response; // Expecting ModeResponse
            } catch (error) {
                let errorMessage = 'Unknown error';
                if (error instanceof Error) {
                    errorMessage = error.message;
                }
                vscode.window.showErrorMessage(`Failed to get mode: ${errorMessage}`);
                return { status: 'error', error: errorMessage };
            }
        }),

        vscode.commands.registerCommand('crewai.switchMode', async (mode: string) => {
            try {
                const response = await vscode.commands.executeCommand('crewai.sendMessage', {
                    type: 'mode_request',
                    action: 'switch_mode',
                    mode: mode
                });
                return response; // Expecting ModeSwitchResult
            } catch (error) {
                let errorMessage = 'Unknown error';
                if (error instanceof Error) {
                    errorMessage = error.message;
                }
                vscode.window.showErrorMessage(`Failed to switch mode: ${errorMessage}`);
                return { status: 'error', error: errorMessage };
            }
        })
    );

    // Add command to open LLM settings to status bar
    const llmSettingsButton = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        100
    );
    llmSettingsButton.text = "$(gear) LLM Settings";
    llmSettingsButton.tooltip = "Configure LLM providers for agents";
    llmSettingsButton.command = 'crewai.openLLMSettings';
    llmSettingsButton.show();
    context.subscriptions.push(llmSettingsButton);

    console.log('CrewAI Extension is now active!');
}

export function deactivate() {
    // Clean up resources
}
