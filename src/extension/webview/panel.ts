import * as vscode from 'vscode';
import { getNonce } from './utils';
import { 
    Message,
    TaskRequest,
    AgentResponse,
    ToolResponse,
    ErrorResponse 
} from './types';

export class AgentPanel {
    public static currentPanel: AgentPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
        this._panel.webview.html = this._getWebviewContent(this._panel.webview, extensionUri);

        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(
            async (message: Message) => {
                switch (message.type) {
                    case 'task':
                        this._handleTask(message);
                        break;
                }
            },
            null,
            this._disposables
        );
    }

    public static createOrShow(extensionUri: vscode.Uri) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        if (AgentPanel.currentPanel) {
            AgentPanel.currentPanel._panel.reveal(column);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            'crewaiAgent',
            'CrewAI Agent',
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true,
                localResourceRoots: [
                    vscode.Uri.joinPath(extensionUri, 'media')
                ]
            }
        );

        AgentPanel.currentPanel = new AgentPanel(panel, extensionUri);
    }

    public static revive(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        AgentPanel.currentPanel = new AgentPanel(panel, extensionUri);
    }

    public async sendTaskToAgent(task: string) {
        const message: TaskRequest = {
            type: 'task',
            content: task
        };
        await this._handleTask(message);
    }

    private async _handleTask(message: TaskRequest) {
        try {
            // Send task to backend
            const response = await vscode.commands.executeCommand('crewai.sendMessage', message) as Message;

            // Post response back to webview
            switch (response.type) {
                case 'agent_response':
                    this._panel.webview.postMessage({
                        type: 'status',
                        content: `Task ${response.status}: ${response.content || response.error}`
                    });
                    break;
                case 'error':
                    this._panel.webview.postMessage({
                        type: 'status',
                        content: `Error: ${response.error}`
                    });
                    break;
            }
        } catch (error) {
            this._panel.webview.postMessage({
                type: 'status',
                content: `Error: ${error}`
            });
        }
    }

    private _getWebviewContent(webview: vscode.Webview, extensionUri: vscode.Uri) {
        const nonce = getNonce();

        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CrewAI Agent</title>
            <style>
                body {
                    padding: 20px;
                    color: var(--vscode-foreground);
                    font-family: var(--vscode-font-family);
                }
                #task-input {
                    width: 100%;
                    padding: 10px;
                    margin-bottom: 10px;
                    background: var(--vscode-input-background);
                    color: var(--vscode-input-foreground);
                    border: 1px solid var(--vscode-input-border);
                }
                #submit-task {
                    padding: 8px 12px;
                    background: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    cursor: pointer;
                }
                #submit-task:hover {
                    background: var(--vscode-button-hoverBackground);
                }
                #status {
                    margin-top: 20px;
                    padding: 10px;
                    white-space: pre-wrap;
                    font-family: var(--vscode-editor-font-family);
                }
            </style>
        </head>
        <body>
            <div>
                <textarea id="task-input" rows="3" placeholder="Enter your task..."></textarea>
                <button id="submit-task">Submit Task</button>
            </div>
            <div id="status"></div>

            <script nonce="${nonce}">
                const vscode = acquireVsCodeApi();
                const taskInput = document.getElementById('task-input');
                const submitButton = document.getElementById('submit-task');
                const statusDiv = document.getElementById('status');

                submitButton.addEventListener('click', () => {
                    const task = taskInput.value.trim();
                    if (task) {
                        vscode.postMessage({
                            type: 'task',
                            content: task
                        });
                        taskInput.value = '';
                    }
                });

                taskInput.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        submitButton.click();
                    }
                });

                window.addEventListener('message', event => {
                    const message = event.data;
                    switch (message.type) {
                        case 'status':
                            statusDiv.textContent = message.content;
                            break;
                    }
                });
            </script>
        </body>
        </html>`;
    }

    public dispose() {
        AgentPanel.currentPanel = undefined;
        this._panel.dispose();
        while (this._disposables.length) {
            const disposable = this._disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }
}
