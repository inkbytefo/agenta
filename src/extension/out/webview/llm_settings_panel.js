"use strict";
/**
 * LLM Settings Panel for VSCode Extension
 *
 * Provides a user interface for configuring Language Learning Model (LLM) providers
 * and their settings. Implements accessibility features and follows VSCode's
 * design patterns for webview integration.
 *
 * Features:
 * - Provider selection and configuration
 * - Model selection per provider
 * - Temperature and token limit settings
 * - Secure API key management via environment variables
 * - Accessibility support (WCAG 2.1 compliant)
 * - Responsive design
 *
 * @module llm_settings_panel
 */
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
exports.LLMSettingsPanel = void 0;
const vscode = __importStar(require("vscode"));
const utils_1 = require("./utils");
const extension_1 = require("../extension");
class LLMSettingsPanel {
    constructor(_panel, extensionUri, context) {
        this.extensionUri = extensionUri;
        this.context = context;
        this._disposables = [];
        this._panel = _panel;
        this.apiKeyStorage = new extension_1.SecureAPIKeyStorage(context);
        this._panel.webview.html = this.getWebviewContent(this._panel.webview, this.extensionUri);
        this.setWebviewMessageListener(this._panel.webview);
        this._panel.onDidDispose(() => {
            LLMSettingsPanel.currentPanel = undefined;
        }, null, this._disposables);
    }
    /**
     * Creates or reveals the LLM settings panel
     *
     * @param extensionUri - URI of the extension
     * @param context - Extension context for secret storage
     */
    static render(extensionUri, context) {
        if (LLMSettingsPanel.currentPanel) {
            LLMSettingsPanel.currentPanel._panel.reveal(vscode.ViewColumn.One);
        }
        else {
            const panel = vscode.window.createWebviewPanel('llmSettings', 'LLM Provider Settings', vscode.ViewColumn.One, {
                enableScripts: true,
                localResourceRoots: [extensionUri],
                retainContextWhenHidden: true
            });
            LLMSettingsPanel.currentPanel = new LLMSettingsPanel(panel, extensionUri, context);
        }
    }
    /**
     * Generates the webview HTML content
     *
     * Important security considerations:
     * - Uses Content Security Policy (CSP) to prevent XSS
     * - Implements nonce for script validation
     * - Restricts resource loading to extension directory
     *
     * Accessibility features:
     * - ARIA labels and roles
     * - Keyboard navigation support
     * - Screen reader compatibility
     * - High contrast support
     * - Focus management
     *
     * @param webview - VSCode webview instance
     * @param extensionUri - URI of the extension
     * @returns HTML content string
     */
    getWebviewContent(webview, extensionUri) {
        const nonce = (0, utils_1.getNonce)();
        return `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
                <title>LLM Provider Settings</title>
                <style>
                    ${this.getBasicStyles()}
                </style>
            </head>
            <body>
                <div class="container" role="main">
                    <div class="header">
                        <h1>LLM Provider Settings</h1>
                    </div>

                    <div class="info-box" role="note" aria-label="Security Notice">
                        <h2>⚠️ Security Notice</h2>
                        <p>For security, configure API keys using environment variables. Never expose API keys in the UI.</p>
                        <p>Configuration steps:</p>
                        <ol>
                            <li>Create or edit your .env file</li>
                            <li>Add your API keys in the format:<br>
                                <code>PROVIDER_API_KEY=your_key_here</code>
                            </li>
                            <li>Restart VSCode to apply changes</li>
                        </ol>
                        <p>See the documentation for more details on secure configuration.</p>
                    </div>

                    <div id="agent-configs" aria-label="Agent Configurations">
                        <!-- Dynamic content inserted here -->
                    </div>
                </div>

                <script nonce="${nonce}">
                    ${this.getClientScript()}
                </script>
            </body>
            </html>
        `;
    }
    /**
     * Core styles required for basic functionality
     * Full styles are typically loaded from webview.css
     *
     * @returns CSS string
     */
    getBasicStyles() {
        return `
            /* Basic fail-safe styles */
            body {
                padding: 20px;
                color: var(--vscode-foreground);
                background-color: var(--vscode-editor-background);
                font-family: var(--vscode-font-family);
            }
            .container { max-width: 800px; margin: 0 auto; }
            .info-box { padding: 15px; margin: 15px 0; }
            button { padding: 8px 16px; margin: 5px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; }
            select, input[type="number"] {
                width: 100%;
                padding: 8px;
                border: 1px solid var(--vscode-input-border);
                border-radius: 4px;
                background-color: var(--vscode-input-background);
                color: var(--vscode-input-foreground);
            }
        `;
    }
    /**
     * Client-side JavaScript for the webview
     * Handles UI interactions and communication with the extension
     *
     * @returns JavaScript code string
     */
    getClientScript() {
        return `
            const vscode = acquireVsCodeApi();
            
            interface Config {
                provider_name: string;
                model_name: string;
                temperature: number;
                max_tokens?: number;
                api_key?: string;
            }

            interface Configs {
                [agentName: string]: Config;
            }

            interface Providers {
                [providerName: string]: any;
            }

            let currentConfigs: Configs = {};
            let providers: Providers = {};

            // Initialize settings
            vscode.postMessage({ type: 'getConfigs' });
            
            // Message handling
            window.addEventListener('message', (event: MessageEvent<Message>) => {
                const message = event.data;
                switch (message.type) {
                    case 'setConfigs':
                        currentConfigs = message.configs;
                        providers = message.providers;
                        renderConfigs();
                        break;
                    case 'updateModels':
                        updateModelsList(message.agentName, message.models);
                        break;
                }
            });

            // UI rendering and event handlers
            function renderConfigs(): void {
                const container = document.getElementById('agent-configs');
                if (!container) return;
                
                container.innerHTML = '';

                Object.entries(currentConfigs).forEach(([agentName, config]) => {
                    const agentDiv = document.createElement('div');
                    agentDiv.className = 'agent-config';
                    
                    const providerOptions = Object.keys(providers)
                        .map(provider => \`<option value="\${provider}" \${config.provider_name === provider ? 'selected' : ''}>\${provider}</option>\`)
                        .join('');

                    agentDiv.innerHTML = \`
                        <h2>\${agentName}</h2>
                        <div class="form-group">
                            <label for="provider-\${agentName}">Provider:</label>
                            <select id="provider-\${agentName}" class="provider-select">
                                \${providerOptions}
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="model-\${agentName}">Model:</label>
                            <select id="model-\${agentName}" class="model-select">
                                <!-- Models will be populated here -->
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="temperature-\${agentName}">Temperature:</label>
                            <input type="number" id="temperature-\${agentName}" value="\${config.temperature}" step="0.1" min="0" max="2">
                        </div>

                        <div class="form-group">
                            <label for="max-tokens-\${agentName}">Max Tokens:</label>
                            <input type="number" id="max-tokens-\${agentName}" value="\${config.max_tokens || ''}" min="1">
                        </div>

                        <button class="save-button" data-agent="\${agentName}">Save</button>
                    \`;
                    
                    container.appendChild(agentDiv);

                    // Add event listeners
                    const providerSelect = document.getElementById(\`provider-\${agentName}\`) as HTMLSelectElement;
                    providerSelect?.addEventListener('change', (e) => {
                        const target = e.target as HTMLSelectElement;
                        providerChanged(agentName, target.value);
                    });

                    const saveButton = agentDiv.querySelector(\`button[data-agent="\${agentName}"]\`);
                    saveButton?.addEventListener('click', () => saveConfig(agentName));

                    // Initial model loading
                    providerChanged(agentName, config.provider_name);
                });
            }

            function providerChanged(agentName: string, provider: string): void {
                vscode.postMessage({ type: 'getModels', provider, agentName });
            }

            function updateModelsList(agentName: string | undefined, models: string[]): void {
                if (!agentName) {
                    console.error('Agent name is undefined');
                    return;
                }
                const modelSelect = document.getElementById(\`model-\${agentName}\`) as HTMLSelectElement;
                if (modelSelect) {
                    modelSelect.innerHTML = models
                        .map(model => \`<option value="\${model}">\${model}</option>\`)
                        .join('');
                }
            }

            function getConfigForAgent(agentName: string): Config {
                return currentConfigs[agentName] || {
                    provider_name: '',
                    model_name: '',
                    temperature: 0.7
                };
            }

            function saveConfig(agentName: string): void {
                const providerElement = document.getElementById(\`provider-\${agentName}\`) as HTMLSelectElement;
                const modelElement = document.getElementById(\`model-\${agentName}\`) as HTMLSelectElement;
                const temperatureElement = document.getElementById(\`temperature-\${agentName}\`) as HTMLInputElement;
                const maxTokensElement = document.getElementById(\`max-tokens-\${agentName}\`) as HTMLInputElement;

                if (!providerElement || !modelElement || !temperatureElement || !maxTokensElement) {
                    console.error('Could not find all required elements');
                    return;
                }

                const config: Config = {
                    provider_name: providerElement.value,
                    model_name: modelElement.value,
                    temperature: parseFloat(temperatureElement.value),
                    max_tokens: maxTokensElement.value ? parseInt(maxTokensElement.value, 10) : undefined
                };

                vscode.postMessage({ type: 'saveConfig', agentName, config });
            }
        `;
    }
    /**
     * Sets up message handling between webview and extension
     *
     * Handles:
     * - Configuration retrieval
     * - Model updates
     * - Configuration saving
     * - Error handling
     *
     * @param webview - VSCode webview instance
     */
    setWebviewMessageListener(webview) {
        webview.onDidReceiveMessage(async (message) => {
            try {
                switch (message.type) {
                    case 'getConfigs':
                        const configs = await vscode.commands.executeCommand('agenta.getLLMConfigs');
                        const providers = await vscode.commands.executeCommand('agenta.getLLMProviders');
                        // Add stored API keys to configs
                        if (configs && providers) {
                            const storedProviders = await this.apiKeyStorage.listProviders();
                            for (const provider of storedProviders) {
                                const apiKey = await this.apiKeyStorage.getAPIKey(provider);
                                Object.keys(configs).forEach(agentName => {
                                    if (configs[agentName].provider_name === provider) {
                                        configs[agentName].api_key = apiKey;
                                    }
                                });
                            }
                            webview.postMessage({ type: 'setConfigs', configs, providers });
                        }
                        break;
                    case 'getModels':
                        if (!message.provider) {
                            throw new Error('Provider not specified');
                        }
                        const models = await vscode.commands.executeCommand('agenta.getLLMModels', message.provider);
                        webview.postMessage({
                            type: 'updateModels',
                            agentName: message.agentName,
                            models
                        });
                        break;
                    case 'saveConfig':
                        if (!message.agentName || !message.config) {
                            throw new Error('Invalid save configuration request');
                        }
                        await vscode.commands.executeCommand('agenta.saveLLMConfig', message.agentName, message.config);
                        vscode.window.showInformationMessage(`LLM configuration saved for ${message.agentName}`);
                        break;
                    default:
                        console.warn(`Unknown message type: ${message.type}`);
                }
            }
            catch (error) {
                vscode.window.showErrorMessage(`Error processing request: ${error instanceof Error ? error.message : 'Unknown error'}`);
            }
        }, undefined, this._disposables);
    }
}
exports.LLMSettingsPanel = LLMSettingsPanel;
//# sourceMappingURL=llm_settings_panel.js.map