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
exports.DebugPanel = void 0;
const vscode = __importStar(require("vscode"));
const utils_1 = require("./utils");
class DebugPanel {
    constructor(panel, extensionUri) {
        this._disposables = [];
        this._panel = panel;
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
        this._panel.webview.html = this._getWebviewContent(this._panel.webview, extensionUri);
        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(async (message) => {
            switch (message.command) {
                case 'getEvents':
                    // Request debug events from the server
                    vscode.commands.executeCommand('crewai.getDebugEvents', message.params);
                    break;
                case 'clearLogs':
                    // Clear debug logs
                    vscode.commands.executeCommand('crewai.clearDebugLogs');
                    break;
            }
        }, null, this._disposables);
    }
    static createOrShow(extensionUri) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;
        if (DebugPanel.currentPanel) {
            DebugPanel.currentPanel._panel.reveal(column);
            return;
        }
        const panel = vscode.window.createWebviewPanel('crewaiDebug', 'CrewAI Debug Console', column || vscode.ViewColumn.One, {
            enableScripts: true,
            retainContextWhenHidden: true,
            localResourceRoots: [
                vscode.Uri.joinPath(extensionUri, 'media')
            ]
        });
        DebugPanel.currentPanel = new DebugPanel(panel, extensionUri);
    }
    static revive(panel, extensionUri) {
        DebugPanel.currentPanel = new DebugPanel(panel, extensionUri);
    }
    updateEvents(events) {
        this._panel.webview.postMessage({
            command: 'updateEvents',
            events
        });
    }
    _getWebviewContent(webview, extensionUri) {
        const nonce = (0, utils_1.getNonce)();
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CrewAI Debug Console</title>
            <style>
                body {
                    padding: 20px;
                    color: var(--vscode-foreground);
                    background-color: var(--vscode-editor-background);
                    font-family: var(--vscode-font-family);
                }
                .event {
                    margin: 10px 0;
                    padding: 10px;
                    border: 1px solid var(--vscode-panel-border);
                    border-radius: 4px;
                }
                .event-header {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 5px;
                }
                .event-type {
                    font-weight: bold;
                    color: var(--vscode-symbolIcon-classForeground);
                }
                .event-agent {
                    color: var(--vscode-symbolIcon-methodForeground);
                }
                .event-action {
                    color: var(--vscode-symbolIcon-functionForeground);
                }
                .event-timestamp {
                    color: var(--vscode-descriptionForeground);
                    font-size: 0.9em;
                }
                .event-details {
                    font-family: var(--vscode-editor-font-family);
                    white-space: pre-wrap;
                }
                .event-status-success {
                    border-left: 4px solid var(--vscode-testing-iconPassed);
                }
                .event-status-error {
                    border-left: 4px solid var(--vscode-testing-iconFailed);
                }
                .toolbar {
                    margin-bottom: 20px;
                    display: flex;
                    gap: 10px;
                }
                button {
                    background-color: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    padding: 8px 12px;
                    cursor: pointer;
                    border-radius: 2px;
                }
                button:hover {
                    background-color: var(--vscode-button-hoverBackground);
                }
            </style>
        </head>
        <body>
            <div class="toolbar">
                <button onclick="clearLogs()">Clear Logs</button>
                <button onclick="refreshEvents()">Refresh</button>
            </div>
            <div id="events"></div>
            <script nonce="${nonce}">
                const vscode = acquireVsCodeApi();
                let events = [];

                function updateEvents(newEvents) {
                    events = newEvents;
                    renderEvents();
                }

                function renderEvents() {
                    const container = document.getElementById('events');
                    container.innerHTML = events.map(event => {
                        const statusClass = event.status === 'error' 
                            ? 'event-status-error' 
                            : 'event-status-success';
                            
                        return \`
                            <div class="event \${statusClass}">
                                <div class="event-header">
                                    <span>
                                        <span class="event-type">\${event.event_type}</span>
                                        <span class="event-agent">\${event.agent}</span>
                                        <span class="event-action">\${event.action}</span>
                                    </span>
                                    <span class="event-timestamp">\${new Date(event.timestamp).toLocaleString()}</span>
                                </div>
                                <div class="event-details">\${JSON.stringify(event.details, null, 2)}</div>
                            </div>
                        \`;
                    }).join('');
                }

                function clearLogs() {
                    vscode.postMessage({ command: 'clearLogs' });
                    events = [];
                    renderEvents();
                }

                function refreshEvents() {
                    vscode.postMessage({
                        command: 'getEvents',
                        params: { limit: 100 }
                    });
                }

                window.addEventListener('message', event => {
                    const message = event.data;
                    switch (message.command) {
                        case 'updateEvents':
                            updateEvents(message.events);
                            break;
                    }
                });

                // Initial load
                refreshEvents();
            </script>
        </body>
        </html>`;
    }
    dispose() {
        DebugPanel.currentPanel = undefined;
        this._panel.dispose();
        while (this._disposables.length) {
            const disposable = this._disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }
}
exports.DebugPanel = DebugPanel;
//# sourceMappingURL=debug_panel.js.map