import * as vscode from 'vscode';
import { getNonce } from './utils';
import { ModeResponse, ModeSwitchResult, ModeMessage } from './mode_types';

export class ModeControlPanel {
    public static currentPanel: ModeControlPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;
        this._panel.webview.html = this._getWebviewContent(this._panel.webview, extensionUri);
        this._setWebviewMessageListener(this._panel.webview);
    }

    public static render(extensionUri: vscode.Uri) {
        if (ModeControlPanel.currentPanel) {
            ModeControlPanel.currentPanel._panel.reveal(vscode.ViewColumn.Two);
        } else {
            const panel = vscode.window.createWebviewPanel(
                'modeControl',
                'Operation Mode',
                vscode.ViewColumn.Two,
                {
                    enableScripts: true,
                    localResourceRoots: [extensionUri]
                }
            );

            ModeControlPanel.currentPanel = new ModeControlPanel(panel, extensionUri);
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
                <title>Operation Mode Control</title>
                <style>
                    body {
                        padding: 20px;
                        color: var(--vscode-foreground);
                        background-color: var(--vscode-editor-background);
                    }
                    .mode-container {
                        display: flex;
                        flex-direction: column;
                        gap: 20px;
                        align-items: center;
                    }
                    .mode-toggle {
                        display: flex;
                        gap: 10px;
                        padding: 10px;
                        border: 1px solid var(--vscode-panel-border);
                        border-radius: 5px;
                    }
                    .mode-button {
                        padding: 8px 16px;
                        background-color: var(--vscode-button-background);
                        color: var(--vscode-button-foreground);
                        border: none;
                        border-radius: 3px;
                        cursor: pointer;
                        opacity: 0.7;
                    }
                    .mode-button.active {
                        opacity: 1;
                        font-weight: bold;
                    }
                    .mode-button:hover {
                        background-color: var(--vscode-button-hoverBackground);
                    }
                    .mode-description {
                        padding: 15px;
                        border: 1px solid var(--vscode-panel-border);
                        border-radius: 5px;
                        white-space: pre-wrap;
                    }
                    .mode-status {
                        font-size: 0.9em;
                        color: var(--vscode-descriptionForeground);
                    }
                </style>
            </head>
            <body>
                <div class="mode-container">
                    <h2>Operation Mode</h2>
                    <div class="mode-toggle">
                        <button id="planMode" class="mode-button active" onclick="switchMode('plan')">PLAN</button>
                        <button id="actMode" class="mode-button" onclick="switchMode('act')">ACT</button>
                    </div>
                    <div class="mode-status">
                        Current Mode: <span id="currentMode">PLAN</span>
                    </div>
                    <div id="modeDescription" class="mode-description">
                        <!-- Mode description will be inserted here -->
                    </div>
                </div>
                <script nonce="${nonce}">
                    const vscode = acquireVsCodeApi();
                    let currentMode = 'plan';

                    // Initialize with current mode
                    vscode.postMessage({ type: 'getMode' });
                    
                    window.addEventListener('message', event => {
                        const message = event.data;
                        switch (message.type) {
                            case 'updateMode':
                                updateModeUI(message.mode, message.description);
                                break;
                        }
                    });

                    function switchMode(mode) {
                        if (mode === currentMode) return;
                        
                        vscode.postMessage({
                            type: 'switchMode',
                            mode: mode
                        });
                    }

                    function updateModeUI(mode, description) {
                        currentMode = mode;
                        
                        // Update buttons
                        document.querySelectorAll('.mode-button').forEach(btn => {
                            btn.classList.remove('active');
                        });
                        document.getElementById(mode + 'Mode').classList.add('active');
                        
                        // Update status and description
                        document.getElementById('currentMode').textContent = mode.toUpperCase();
                        document.getElementById('modeDescription').textContent = description;
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
                    case 'getMode':
                        const currentMode = await vscode.commands.executeCommand('crewai.getMode') as ModeResponse;
                        webview.postMessage({
                            type: 'updateMode',
                            mode: currentMode.mode,
                            description: currentMode.description
                        });
                        break;
                        
                    case 'switchMode':
                        const result = await vscode.commands.executeCommand('crewai.switchMode', message.mode) as ModeSwitchResult;
                        if (result.status === 'success') {
                            webview.postMessage({
                                type: 'updateMode',
                                mode: message.mode,
                                description: result.description
                            });
                            
                            // Show mode change notification
                            vscode.window.showInformationMessage(`Switched to ${message.mode.toUpperCase()} mode`);
                        } else {
                            vscode.window.showErrorMessage(`Failed to switch mode: ${result.error}`);
                        }
                        break;
                }
            },
            undefined,
            this._disposables
        );
    }
}
