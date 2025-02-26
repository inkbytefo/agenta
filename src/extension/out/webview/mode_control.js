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
exports.ModeControlPanel = void 0;
const vscode = __importStar(require("vscode"));
const utils_1 = require("./utils");
class ModeControlPanel {
    constructor(panel, extensionUri) {
        this._disposables = [];
        this._panel = panel;
        this._panel.webview.html = this._getWebviewContent(this._panel.webview, extensionUri);
        this._setWebviewMessageListener(this._panel.webview);
    }
    static render(extensionUri) {
        if (ModeControlPanel.currentPanel) {
            ModeControlPanel.currentPanel._panel.reveal(vscode.ViewColumn.Two);
        }
        else {
            const panel = vscode.window.createWebviewPanel('modeControl', 'Operation Mode', vscode.ViewColumn.Two, {
                enableScripts: true,
                localResourceRoots: [extensionUri]
            });
            ModeControlPanel.currentPanel = new ModeControlPanel(panel, extensionUri);
        }
    }
    _getWebviewContent(webview, extensionUri) {
        const nonce = (0, utils_1.getNonce)();
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
    _setWebviewMessageListener(webview) {
        webview.onDidReceiveMessage(async (message) => {
            switch (message.type) {
                case 'getMode':
                    const currentMode = await vscode.commands.executeCommand('crewai.getMode');
                    webview.postMessage({
                        type: 'updateMode',
                        mode: currentMode.mode,
                        description: currentMode.description
                    });
                    break;
                case 'switchMode':
                    const result = await vscode.commands.executeCommand('crewai.switchMode', message.mode);
                    if (result.status === 'success') {
                        webview.postMessage({
                            type: 'updateMode',
                            mode: message.mode,
                            description: result.description
                        });
                        // Show mode change notification
                        vscode.window.showInformationMessage(`Switched to ${message.mode.toUpperCase()} mode`);
                    }
                    else {
                        vscode.window.showErrorMessage(`Failed to switch mode: ${result.error}`);
                    }
                    break;
            }
        }, undefined, this._disposables);
    }
}
exports.ModeControlPanel = ModeControlPanel;
//# sourceMappingURL=mode_control.js.map