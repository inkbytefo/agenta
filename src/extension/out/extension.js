"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.SecureAPIKeyStorage = void 0;
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const debug_panel_1 = require("./webview/debug_panel");
const panel_1 = require("./webview/panel");
const llm_settings_panel_1 = require("./webview/llm_settings_panel");
// Secret storage keys
const API_KEY_PREFIX = 'agenta.apiKey.';
const PROVIDER_LIST_KEY = 'agenta.providers';
// API key storage wrapper
class SecureAPIKeyStorage {
    constructor(context) {
        this.context = context;
    }
    async storeAPIKey(provider, key) {
        await this.context.secrets.store(`${API_KEY_PREFIX}${provider}`, key);
        // Update provider list in global state
        const providers = this.context.globalState.get(PROVIDER_LIST_KEY, []);
        if (!providers.includes(provider)) {
            providers.push(provider);
            await this.context.globalState.update(PROVIDER_LIST_KEY, providers);
        }
    }
    async getAPIKey(provider) {
        return await this.context.secrets.get(`${API_KEY_PREFIX}${provider}`);
    }
    async deleteAPIKey(provider) {
        await this.context.secrets.delete(`${API_KEY_PREFIX}${provider}`);
        // Update provider list
        const providers = this.context.globalState.get(PROVIDER_LIST_KEY, []);
        const updatedProviders = providers.filter(p => p !== provider);
        await this.context.globalState.update(PROVIDER_LIST_KEY, updatedProviders);
    }
    async listProviders() {
        return this.context.globalState.get(PROVIDER_LIST_KEY, []);
    }
}
exports.SecureAPIKeyStorage = SecureAPIKeyStorage;
function activate(context) {
    // Initialize secure storage
    const apiKeyStorage = new SecureAPIKeyStorage(context);
    // Register debug panel commands
    context.subscriptions.push(vscode.commands.registerCommand('crewai.openDebugConsole', () => {
        debug_panel_1.DebugPanel.createOrShow(context.extensionUri);
    }), vscode.commands.registerCommand('crewai.getDebugEvents', async (params) => {
        try {
            const response = await vscode.commands.executeCommand('crewai.sendMessage', {
                type: 'debug_request',
                action: 'get_events',
                params
            });
            if (response.type !== 'debug_response') {
                throw new Error('Invalid response type');
            }
            if (debug_panel_1.DebugPanel.currentPanel) {
                debug_panel_1.DebugPanel.currentPanel.updateEvents(response.events);
            }
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to get debug events: ${error}`);
        }
    }), vscode.commands.registerCommand('crewai.clearDebugLogs', async () => {
        try {
            await vscode.commands.executeCommand('crewai.sendMessage', {
                type: 'debug_request',
                action: 'clear_logs'
            });
            vscode.window.showInformationMessage('Debug logs cleared');
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to clear debug logs: ${error}`);
        }
    }));
    // Register command to open agent panel
    context.subscriptions.push(vscode.commands.registerCommand('crewai.openAgent', () => {
        panel_1.AgentPanel.createOrShow(context.extensionUri);
    }));
    // Register command to send task to agent
    context.subscriptions.push(vscode.commands.registerCommand('crewai.sendTask', async () => {
        const task = await vscode.window.showInputBox({
            prompt: 'Enter your task',
            placeHolder: 'e.g., Create a new file named example.js'
        });
        if (task) {
            panel_1.AgentPanel.currentPanel?.sendTaskToAgent(task);
        }
    }));
    // Register LLM settings commands
    context.subscriptions.push(vscode.commands.registerCommand('crewai.openLLMSettings', () => {
        llm_settings_panel_1.LLMSettingsPanel.render(context.extensionUri, context);
    }), vscode.commands.registerCommand('crewai.getLLMConfigs', async () => {
        try {
            const response = await vscode.commands.executeCommand('crewai.sendMessage', {
                type: 'llm_request',
                action: 'get_configs'
            });
            return response.configs || {};
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to get LLM configurations: ${error}`);
            return {};
        }
    }), vscode.commands.registerCommand('crewai.getLLMProviders', async () => {
        try {
            const response = await vscode.commands.executeCommand('crewai.sendMessage', {
                type: 'llm_request',
                action: 'get_providers'
            });
            return response.providers || {};
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to get LLM providers: ${error}`);
            return {};
        }
    }), vscode.commands.registerCommand('crewai.getLLMModels', async (provider) => {
        try {
            const response = await vscode.commands.executeCommand('crewai.sendMessage', {
                type: 'llm_request',
                action: 'get_models',
                provider: provider
            });
            return response.models || [];
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to get models for ${provider}: ${error}`);
            return [];
        }
    }), vscode.commands.registerCommand('crewai.saveLLMConfig', async (agentName, config) => {
        try {
            const response = await vscode.commands.executeCommand('crewai.sendMessage', {
                type: 'llm_request',
                action: 'save_config',
                agentName: agentName,
                config: config
            });
            return true;
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to save LLM configuration: ${error}`);
            return false;
        }
    }));
    // Register mode control commands
    context.subscriptions.push(vscode.commands.registerCommand('crewai.getMode', async () => {
        try {
            const response = await vscode.commands.executeCommand('crewai.sendMessage', {
                type: 'mode_request',
                action: 'get_mode'
            });
            return response; // Expecting ModeResponse
        }
        catch (error) {
            let errorMessage = 'Unknown error';
            if (error instanceof Error) {
                errorMessage = error.message;
            }
            vscode.window.showErrorMessage(`Failed to get mode: ${errorMessage}`);
            return { status: 'error', error: errorMessage };
        }
    }), vscode.commands.registerCommand('crewai.switchMode', async (mode) => {
        try {
            const response = await vscode.commands.executeCommand('crewai.sendMessage', {
                type: 'mode_request',
                action: 'switch_mode',
                mode: mode
            });
            return response; // Expecting ModeSwitchResult
        }
        catch (error) {
            let errorMessage = 'Unknown error';
            if (error instanceof Error) {
                errorMessage = error.message;
            }
            vscode.window.showErrorMessage(`Failed to switch mode: ${errorMessage}`);
            return { status: 'error', error: errorMessage };
        }
    }));
    // Add command to open LLM settings to status bar
    const llmSettingsButton = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    llmSettingsButton.text = "$(gear) LLM Settings";
    llmSettingsButton.tooltip = "Configure LLM providers for agents";
    llmSettingsButton.command = 'crewai.openLLMSettings';
    llmSettingsButton.show();
    context.subscriptions.push(llmSettingsButton);
    console.log('CrewAI Extension is now active!');
}
function deactivate() {
    // Clean up resources
}
//# sourceMappingURL=extension.js.map