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
                    localResourceRoots: [extensionUri],
                    retainContextWhenHidden: true
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
                <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
                <title>LLM Provider Settings</title>
                <style>
                    :root {
                        --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                        --primary-color: var(--vscode-button-background);
                        --primary-hover: var(--vscode-button-hoverBackground);
                        --text-color: var(--vscode-foreground);
                        --bg-color: var(--vscode-editor-background);
                        --input-bg: var(--vscode-input-background);
                        --input-border: var(--vscode-input-border);
                        --error-color: var(--vscode-errorForeground);
                        --focus-border: var(--vscode-focusBorder);
                    }

                    body {
                        padding: 20px;
                        color: var(--text-color);
                        background-color: var(--bg-color);
                        font-family: var(--font-family);
                        line-height: 1.6;
                        margin: 0;
                        font-size: 14px;
                    }

                    .container {
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 0 20px;
                    }

                    .agent-config {
                        margin-bottom: 30px;
                        padding: 20px;
                        border: 1px solid var(--vscode-panel-border);
                        border-radius: 6px;
                        transition: box-shadow 0.3s ease;
                    }

                    .agent-config:hover {
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                    }

                    .form-group {
                        margin-bottom: 20px;
                    }

                    label {
                        display: block;
                        margin-bottom: 8px;
                        font-weight: 500;
                        color: var(--text-color);
                    }

                    select, input {
                        width: 100%;
                        padding: 8px 12px;
                        margin: 5px 0;
                        background-color: var(--input-bg);
                        color: var(--text-color);
                        border: 1px solid var(--input-border);
                        border-radius: 4px;
                        font-size: 14px;
                        transition: border-color 0.3s ease;
                    }

                    select:focus, input:focus {
                        outline: none;
                        border-color: var(--focus-border);
                        box-shadow: 0 0 0 2px rgba(0, 122, 204, 0.25);
                    }

                    button {
                        padding: 8px 16px;
                        margin: 5px;
                        background-color: var(--primary-color);
                        color: var(--vscode-button-foreground);
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: 500;
                        transition: background-color 0.3s ease;
                    }

                    button:hover {
                        background-color: var(--primary-hover);
                    }

                    button:focus {
                        outline: none;
                        box-shadow: 0 0 0 2px var(--focus-border);
                    }

                    .header {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 30px;
                        flex-wrap: wrap;
                        gap: 20px;
                    }

                    .info-box {
                        padding: 16px;
                        margin: 20px 0;
                        background-color: var(--vscode-textBlockQuote-background);
                        border-left: 4px solid var(--vscode-textBlockQuote-border);
                        border-radius: 4px;
                    }

                    .error-message {
                        color: var(--error-color);
                        font-size: 14px;
                        margin-top: 4px;
                    }

                    @media (max-width: 600px) {
                        .header {
                            flex-direction: column;
                            align-items: flex-start;
                        }

                        button {
                            width: 100%;
                            margin: 5px 0;
                        }

                        .container {
                            padding: 0 10px;
                        }
                    }

                    /* Accessibility improvements */
                    .visually-hidden {
                        position: absolute;
                        width: 1px;
                        height: 1px;
                        padding: 0;
                        margin: -1px;
                        overflow: hidden;
                        clip: rect(0, 0, 0, 0);
                        border: 0;
                    }

                    [role="alert"] {
                        border-left: 4px solid var(--error-color);
                        padding: 12px;
                        margin: 12px 0;
                        background-color: var(--vscode-inputValidation-errorBackground);
                    }
                </style>
            </head>
            <body>
                <div class="container" role="main">
                    <div class="header">
                        <h1>LLM Provider Settings</h1>
                        <button onclick="saveAllConfigs()" aria-label="Save all configuration changes">
                            Save All Changes
                        </button>
                    </div>

                    <div class="info-box" role="note" aria-label="Security Notice">
                        <h2>⚠️ Security Notice</h2>
                        <p>API keys should be configured using environment variables for security. 
                        Add your API keys to your .env file or system environment variables.</p>
                        <p>Example format in .env:<br>
                        <code>OPENAI_API_KEY=your_key_here<br>
                        ANTHROPIC_API_KEY=your_key_here</code></p>
                    </div>

                    <div id="agent-configs" aria-label="Agent Configurations">
                        <!-- Agent configurations will be dynamically inserted here -->
                    </div>
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
                            div.setAttribute('role', 'region');
                            div.setAttribute('aria-label', \`Configuration for \${agentName}\`);
                            
                            div.innerHTML = \`
                                <h2>\${agentName}</h2>
                                <div class="form-group">
                                    <label for="provider-\${agentName}">Provider:</label>
                                    <select 
                                        id="provider-\${agentName}"
                                        onchange="providerChanged('\${agentName}', this.value)"
                                        aria-label="Select LLM provider">
                                        \${Object.keys(providers).map(p => 
                                            \`<option value="\${p}" \${p === config.provider_name ? 'selected' : ''}>\${p}</option>\`
                                        ).join('')}
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="model-\${agentName}">Model:</label>
                                    <select 
                                        id="model-\${agentName}"
                                        aria-label="Select model">
                                        \${providers[config.provider_name].models.map(m => 
                                            \`<option value="\${m}" \${m === config.model_name ? 'selected' : ''}>\${m}</option>\`
                                        ).join('')}
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="temperature-\${agentName}">Temperature:</label>
                                    <input 
                                        type="number" 
                                        id="temperature-\${agentName}"
                                        min="0" 
                                        max="1" 
                                        step="0.1" 
                                        value="\${config.temperature}"
                                        aria-label="Set temperature value between 0 and 1">
                                </div>
                                <div class="form-group">
                                    <label for="max-tokens-\${agentName}">Max Tokens:</label>
                                    <input 
                                        type="number" 
                                        id="max-tokens-\${agentName}"
                                        min="1" 
                                        value="\${config.max_tokens || ''}"
                                        aria-label="Set maximum tokens">
                                </div>
                                <button 
                                    onclick="saveConfig('\${agentName}')"
                                    aria-label="Save configuration for \${agentName}">
                                    Save Changes
                                </button>
                            \`;
                            container.appendChild(div);
                        });
                    }

                    function providerChanged(agentName, provider) {
                        const select = document.getElementById(\`model-\${agentName}\`);
                        select.setAttribute('aria-busy', 'true');
                        
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
                        select.setAttribute('aria-busy', 'false');
                    }

                    function getConfigForAgent(agentName) {
                        return {
                            provider_name: document.getElementById(\`provider-\${agentName}\`).value,
                            model_name: document.getElementById(\`model-\${agentName}\`).value,
                            temperature: parseFloat(document.getElementById(\`temperature-\${agentName}\`).value),
                            max_tokens: parseInt(document.getElementById(\`max-tokens-\${agentName}\`).value) || null
                        };
                    }

                    function saveConfig(agentName) {
                        const saveButton = document.querySelector(\`button[onclick="saveConfig('\${agentName}')"]\`);
                        saveButton.setAttribute('aria-busy', 'true');
                        
                        const config = getConfigForAgent(agentName);
                        vscode.postMessage({
                            type: 'saveConfig',
                            agentName: agentName,
                            config: config
                        });
                    }

                    function saveAllConfigs() {
                        const saveAllButton = document.querySelector('button[aria-label="Save all configuration changes"]');
                        saveAllButton.setAttribute('aria-busy', 'true');
                        
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
                        const configs = await vscode.commands.executeCommand('agenta.getLLMConfigs');
                        const providers = await vscode.commands.executeCommand('agenta.getLLMProviders');
                        webview.postMessage({ type: 'setConfigs', configs, providers });
                        break;

                    case 'getModels':
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
                        try {
                            await vscode.commands.executeCommand(
                                'agenta.saveLLMConfig',
                                message.agentName,
                                message.config
                            );
                            vscode.window.showInformationMessage(
                                `LLM configuration saved for ${message.agentName}`
                            );
                        } catch (error) {
                            vscode.window.showErrorMessage(
                                `Error saving configuration: ${error}`
                            );
                        }
                        break;
                }
            },
            undefined,
            this._disposables
        );
    }
}
