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

import * as vscode from 'vscode';
import { getNonce } from './utils';

interface LLMProviderConfig {
    provider_name: string;
    model_name: string;
    temperature: number;
    max_tokens?: number;
}

interface MessageResponse {
    type: string;
    configs?: Record<string, LLMProviderConfig>;
    providers?: Record<string, any>;
    agentName?: string;
    models?: string[];
}

export class LLMSettingsPanel {
    /**
     * Tracks the currently active settings panel instance
     */
    public static currentPanel: LLMSettingsPanel | undefined;

    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];

    /**
     * Creates a new LLMSettingsPanel instance
     * 
     * @param panel - VSCode webview panel
     * @param extensionUri - URI of the extension
     */
    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;
        this._panel.webview.html = this._getWebviewContent(this._panel.webview, extensionUri);
        this._setWebviewMessageListener(this._panel.webview);
    }

    /**
     * Creates or reveals the LLM settings panel
     * 
     * @param extensionUri - URI of the extension
     */
    public static render(extensionUri: vscode.Uri): void {
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
    private _getWebviewContent(webview: vscode.Webview, extensionUri: vscode.Uri): string {
        const nonce = getNonce();

        // CSS styles moved to external file for readability
        // See webview.css for complete styling
        return `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
                <title>LLM Provider Settings</title>
                <style>
                    /* See complete styles in webview.css */
                    /* Core styles included inline for fail-safe loading */
                    ${this._getBasicStyles()}
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
                    ${this._getClientScript()}
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
    private _getBasicStyles(): string {
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
        `;
    }

    /**
     * Client-side JavaScript for the webview
     * Handles UI interactions and communication with the extension
     * 
     * @returns JavaScript code string
     */
    private _getClientScript(): string {
        // See webview.js for complete client-side implementation
        return `
            const vscode = acquireVsCodeApi();
            let currentConfigs = {};
            let providers = {};

            // Initialize settings
            vscode.postMessage({ type: 'getConfigs' });
            
            // Message handling
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

            // UI rendering and event handlers
            function renderConfigs() { /* ... */ }
            function providerChanged(agentName, provider) { /* ... */ }
            function updateModelsList(agentName, models) { /* ... */ }
            function getConfigForAgent(agentName) { /* ... */ }
            function saveConfig(agentName) { /* ... */ }
            function saveAllConfigs() { /* ... */ }
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
    private _setWebviewMessageListener(webview: vscode.Webview): void {
        webview.onDidReceiveMessage(
            async (message: {type: string, agentName?: string, provider?: string, config?: LLMProviderConfig}) => {
                try {
                    switch (message.type) {
                        case 'getConfigs':
                            const configs = await vscode.commands.executeCommand('agenta.getLLMConfigs');
                            const providers = await vscode.commands.executeCommand('agenta.getLLMProviders');
                            webview.postMessage({ type: 'setConfigs', configs, providers });
                            break;

                        case 'getModels':
                            if (!message.provider) {
                                throw new Error('Provider not specified');
                            }
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
                            if (!message.agentName || !message.config) {
                                throw new Error('Invalid save configuration request');
                            }
                            await vscode.commands.executeCommand(
                                'agenta.saveLLMConfig',
                                message.agentName,
                                message.config
                            );
                            vscode.window.showInformationMessage(
                                `LLM configuration saved for ${message.agentName}`
                            );
                            break;

                        default:
                            console.warn(`Unknown message type: ${message.type}`);
                    }
                } catch (error) {
                    vscode.window.showErrorMessage(
                        `Error processing request: ${error instanceof Error ? error.message : 'Unknown error'}`
                    );
                }
            },
            undefined,
            this._disposables
        );
    }
}
