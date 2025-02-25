import * as vscode from 'vscode';
import { getNonce } from './utils';

export class LLMSettingsPanel {
    public static currentPanel: LLMSettingsPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;
        this._panel.webview.html = this._getWebviewContent(this._panel.webview, extensionUri);
        this._setWebviewMessageListener(this._panel.webview);
    }

    public static render(extensionUri: vscode.Uri) {
        if (LLMSettingsPanel.currentPanel) {
            LLMSettingsPanel.currentPanel._panel.reveal(vscode.ViewColumn.One);
        } else {
            const panel = vscode.window.createWebviewPanel(
                'llmSettings',
                'LLM Provider Settings',
                vscode.ViewColumn.One,
                {
                    enableScripts: true,
                    localResourceRoots: [extensionUri]
                }
            );

            LLMSettingsPanel.currentPanel = new LLMSettingsPanel(panel, extensionUri);
        }
    }

    private _getWebviewContent(webview: vscode.Webview, extensionUri: vscode.Uri) {
        const nonce = getNonce();

        return `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>LLM Provider Settings</title>
                <style>
                    body {
                        padding: 20px;
                        color: var(--vscode-foreground);
                        background-color: var(--vscode-editor-background);
                    }
                    .agent-config {
                        margin-bottom: 30px;
                        padding: 15px;
                        border: 1px solid var(--vscode-panel-border);
                        border-radius: 5px;
                    }
                    select, input {
                        width: 100%;
                        padding: 5px;
                        margin: 5px 0;
                        background-color: var(--vscode-input-background);
                        color: var(--vscode-input-foreground);
                        border: 1px solid var(--vscode-input-border);
                    }
                    button {
                        padding: 8px 15px;
                        margin: 5px;
                        background-color: var(--vscode-button-background);
                        color: var(--vscode-button-foreground);
                        border: none;
                        border-radius: 3px;
                        cursor: pointer;
                    }
                    button:hover {
                        background-color: var(--vscode-button-hoverBackground);
                    }
                    .header {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 20px;
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>LLM Provider Settings</h1>
                    <button onclick="saveAllConfigs()">Save All Changes</button>
                </div>
                <div id="agent-configs">
                    <!-- Agent configurations will be dynamically inserted here -->
                </div>
                <script nonce="${nonce}">
                    const vscode = acquireVsCodeApi();
                    let currentConfigs = {};
                    let providers = {};

                    // Initialize with current settings
                    vscode.postMessage({ type: 'getConfigs' });
                    
                    window.addEventListener('message', event => {
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

                    function renderConfigs() {
                        const container = document.getElementById('agent-configs');
                        container.innerHTML = '';

                        Object.keys(currentConfigs).forEach(agentName => {
                            const config = currentConfigs[agentName];
                            const div = document.createElement('div');
                            div.className = 'agent-config';
                            div.innerHTML = \`
                                <h2>\${agentName}</h2>
                                <div>
                                    <label>Provider:</label>
                                    <select onchange="providerChanged('\${agentName}', this.value)">
                                        \${Object.keys(providers).map(p => 
                                            \`<option value="\${p}" \${p === config.provider_name ? 'selected' : ''}>\${p}</option>\`
                                        ).join('')}
                                    </select>
                                </div>
                                <div>
                                    <label>Model:</label>
                                    <select id="model-\${agentName}">
                                        \${providers[config.provider_name].models.map(m => 
                                            \`<option value="\${m}" \${m === config.model_name ? 'selected' : ''}>\${m}</option>\`
                                        ).join('')}
                                    </select>
                                </div>
                                <div>
                                    <label>API Key:</label>
                                    <input type="password" 
                                           value="\${config.api_key || ''}" 
                                           placeholder="Enter API key or use environment variable"
                                           id="api-key-\${agentName}">
                                </div>
                                <div>
                                    <label>Temperature:</label>
                                    <input type="number" 
                                           min="0" 
                                           max="1" 
                                           step="0.1" 
                                           value="\${config.temperature}"
                                           id="temperature-\${agentName}">
                                </div>
                                <div>
                                    <label>Max Tokens:</label>
                                    <input type="number" 
                                           min="1" 
                                           value="\${config.max_tokens || ''}"
                                           id="max-tokens-\${agentName}">
                                </div>
                                <button onclick="saveConfig('\${agentName}')">Save Changes</button>
                            \`;
                            container.appendChild(div);
                        });
                    }

                    function providerChanged(agentName, provider) {
                        vscode.postMessage({
                            type: 'getModels',
                            agentName: agentName,
                            provider: provider
                        });
                    }

                    function updateModelsList(agentName, models) {
                        const select = document.getElementById(\`model-\${agentName}\`);
                        select.innerHTML = models.map(m => 
                            \`<option value="\${m}">\${m}</option>\`
                        ).join('');
                    }

                    function getConfigForAgent(agentName) {
                        return {
                            provider_name: document.querySelector(\`#agent-configs select\`).value,
                            model_name: document.getElementById(\`model-\${agentName}\`).value,
                            api_key: document.getElementById(\`api-key-\${agentName}\`).value,
                            temperature: parseFloat(document.getElementById(\`temperature-\${agentName}\`).value),
                            max_tokens: parseInt(document.getElementById(\`max-tokens-\${agentName}\`).value) || null
                        };
                    }

                    function saveConfig(agentName) {
                        const config = getConfigForAgent(agentName);
                        vscode.postMessage({
                            type: 'saveConfig',
                            agentName: agentName,
                            config: config
                        });
                    }

                    function saveAllConfigs() {
                        Object.keys(currentConfigs).forEach(agentName => {
                            saveConfig(agentName);
                        });
                    }
                </script>
            </body>
            </html>
        `;
    }

    private _setWebviewMessageListener(webview: vscode.Webview) {
        webview.onDidReceiveMessage(
            async (message) => {
                switch (message.type) {
                    case 'getConfigs':
                        // Request current configurations from backend
                        const configs = await vscode.commands.executeCommand('agenta.getLLMConfigs');
                        const providers = await vscode.commands.executeCommand('agenta.getLLMProviders');
                        webview.postMessage({ type: 'setConfigs', configs, providers });
                        break;

                    case 'getModels':
                        // Request models for selected provider
                        const models = await vscode.commands.executeCommand(
                            'agenta.getLLMModels',
                            message.provider
                        );
                        webview.postMessage({
                            type: 'updateModels',
                            agentName: message.agentName,
                            models
                        });
                        break;

                    case 'saveConfig':
                        // Save configuration for an agent
                        await vscode.commands.executeCommand(
                            'agenta.saveLLMConfig',
                            message.agentName,
                            message.config
                        );
                        vscode.window.showInformationMessage(
                            `LLM configuration saved for ${message.agentName}`
                        );
                        break;
                }
            },
            undefined,
            this._disposables
        );
    }
}
