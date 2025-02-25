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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AgentPanel = void 0;
const vscode = __importStar(require("vscode"));
const ws_1 = __importDefault(require("ws"));
class AgentPanel {
    constructor(panel, extensionUri) {
        this._disposables = [];
        this._panel = panel;
        this._extensionUri = extensionUri;
        this._panel.webview.html = this._getWebviewContent();
        this._connectToBackend();
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
        this._panel.webview.onDidReceiveMessage((message) => {
            switch (message.command) {
                case 'sendTask':
                    this._sendMessageToBackend(message.text);
                    return;
            }
        }, null, this._disposables);
    }
    static createOrShow(extensionUri) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;
        if (AgentPanel.currentPanel) {
            AgentPanel.currentPanel._panel.reveal(column);
            return;
        }
        const panel = vscode.window.createWebviewPanel(AgentPanel.viewType, 'CrewAI Agent', column || vscode.ViewColumn.One, {
            enableScripts: true,
            retainContextWhenHidden: true
        });
        AgentPanel.currentPanel = new AgentPanel(panel, extensionUri);
    }
    sendTaskToAgent(task) {
        this._sendMessageToBackend(task);
    }
    _connectToBackend() {
        try {
            const ws = new ws_1.default('ws://localhost:3000');
            this._ws = ws;
            ws.on('open', () => {
                this._updateStatus('Connected to agent');
            });
            ws.on('message', (data) => {
                try {
                    const response = JSON.parse(data.toString());
                    this._updateResponse(response);
                }
                catch (e) {
                    console.error('Failed to parse message:', e);
                }
            });
            ws.on('error', (error) => {
                this._updateStatus(`Error: ${error.message}`);
            });
            ws.on('close', () => {
                this._updateStatus('Disconnected from agent');
            });
        }
        catch (error) {
            this._updateStatus(`Failed to connect: ${error}`);
        }
    }
    _sendMessageToBackend(text) {
        if (this._ws?.readyState === 1) { // WebSocket.OPEN is 1
            const message = {
                type: 'task',
                content: text,
                timestamp: Date.now()
            };
            this._ws.send(JSON.stringify(message));
        }
        else {
            this._updateStatus('Not connected to agent');
        }
    }
    _updateStatus(text) {
        const message = {
            type: 'status',
            text: text
        };
        this._panel.webview.postMessage(message);
    }
    _updateResponse(response) {
        const message = {
            type: 'response',
            data: response
        };
        this._panel.webview.postMessage(message);
    }
    _getWebviewContent() {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CrewAI Agent</title>
            <style>
                body {
                    padding: 20px;
                    font-family: var(--vscode-font-family);
                    color: var(--vscode-editor-foreground);
                }
                .container {
                    display: flex;
                    flex-direction: column;
                    gap: 20px;
                }
                #taskInput {
                    width: 100%;
                    padding: 8px;
                    background: var(--vscode-input-background);
                    color: var(--vscode-input-foreground);
                    border: 1px solid var(--vscode-input-border);
                }
                #response {
                    white-space: pre-wrap;
                    padding: 10px;
                    background: var(--vscode-editor-background);
                    border: 1px solid var(--vscode-panel-border);
                }
                #status {
                    color: var(--vscode-descriptionForeground);
                }
                button {
                    padding: 8px 16px;
                    background: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    cursor: pointer;
                }
                button:hover {
                    background: var(--vscode-button-hoverBackground);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div>
                    <input type="text" id="taskInput" placeholder="Enter your task here...">
                    <button id="sendButton">Send Task</button>
                </div>
                <div id="status">Initializing...</div>
                <pre id="response"></pre>
            </div>

            <script>
                const vscode = acquireVsCodeApi();
                const taskInput = document.getElementById('taskInput');
                const sendButton = document.getElementById('sendButton');
                const statusElement = document.getElementById('status');
                const responseElement = document.getElementById('response');

                sendButton.addEventListener('click', () => {
                    const text = taskInput.value;
                    if (text) {
                        vscode.postMessage({
                            command: 'sendTask',
                            text: text
                        });
                        taskInput.value = '';
                    }
                });

                taskInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        sendButton.click();
                    }
                });

                window.addEventListener('message', event => {
                    const message = event.data;
                    switch (message.type) {
                        case 'status':
                            statusElement.textContent = message.text;
                            break;
                        case 'response':
                            responseElement.textContent = JSON.stringify(message.data, null, 2);
                            break;
                    }
                });
            </script>
        </body>
        </html>`;
    }
    dispose() {
        AgentPanel.currentPanel = undefined;
        this._ws?.close();
        while (this._disposables.length) {
            const disposable = this._disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
        this._panel.dispose();
    }
}
exports.AgentPanel = AgentPanel;
AgentPanel.viewType = 'crewAIAgent';
//# sourceMappingURL=panel.js.map