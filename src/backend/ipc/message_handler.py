import json
from typing import Dict, Any, Callable, Set, Optional
import asyncio
import websockets

from ..agents.prompt_agent import PromptAgent
from ..agents.supervisor_agent import SupervisorAgent
from ..llm.providers import LLMProviderConfig
from ..debug.debug_console import DebugConsole, WebSocketSubscriber
from ..modes.mode_manager import ModeManager

class MessageHandler:
    def __init__(self, prompt_agent: PromptAgent, supervisor_agent: SupervisorAgent):
        self.prompt_agent = prompt_agent
        self.supervisor_agent = supervisor_agent
        self.debug_console = DebugConsole(prompt_agent.project_path)
        self.websocket_subscriber = None
        self.active_connections: Set[websockets.WebSocketServerProtocol] = set()
        
        self.mode_manager = ModeManager()  # Instantiate ModeManager
        
        self.message_handlers: Dict[str, Callable] = {
            'task': self._handle_task,
            'tool_request': self._handle_tool_request,
            'debug_request': self._handle_debug_request,
            'mode_request': self._handle_mode_request,
            'llm_request': self._handle_llm_request
        }

    async def handle_message(self, message: str, websocket) -> str:
        """Handle incoming messages and return response"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            correlation_id = data.get('correlation_id')
            
            if message_type not in self.message_handlers:
                return self._create_error_response('Unknown message type')
            
            # Log incoming message
            await self.debug_console.log_event(
                event_type='message_received',
                agent='message_handler',
                action=message_type,
                details=data,
                correlation_id=correlation_id
            )
            
            handler = self.message_handlers[message_type]
            response = await handler(data)
            
            # Log response
            await self.debug_console.log_event(
                event_type='message_sent',
                agent='message_handler',
                action=f'{message_type}_response',
                details=response,
                correlation_id=correlation_id
            )
            
            return json.dumps(response)
            
        except json.JSONDecodeError:
            return self._create_error_response('Invalid JSON format')
        except Exception as e:
            error_response = self._create_error_response(str(e))
            
            # Log error
            await self.debug_console.log_event(
                event_type='error',
                agent='message_handler',
                action='handle_message',
                details={'error': str(e)},
                status='error'
            )
            
            return error_response

    async def _handle_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task execution through prompt analysis and supervisor coordination"""
        task = data.get('content')
        correlation_id = data.get('correlation_id')
        
        if not task:
            return self._create_error_response('No task content provided')
        
        try:
            # First, analyze task through prompt agent
            prompt_task = self.prompt_agent.create_task(
                description=task,
                expected_output="Structured and enhanced task description"
            )
            
            # Log prompt analysis start
            await self.debug_console.log_event(
                event_type='task_start',
                agent=self.prompt_agent.name,
                action='analyze_prompt',
                details={'task': task},
                correlation_id=correlation_id
            )
            
            prompt_result = await self.prompt_agent.execute(prompt_task)
            
            if prompt_result['status'] != 'success':
                return {
                    'type': 'agent_response',
                    'status': 'error',
                    'error': 'Prompt analysis failed',
                    'correlation_id': correlation_id
                }
            
            # Extract enhanced prompt and context
            enhanced_prompt = prompt_result['enhanced_prompt']
            context = prompt_result.get('context', {})
            
            # Log prompt analysis completion
            await self.debug_console.log_event(
                event_type='task_complete',
                agent=self.prompt_agent.name,
                action='analyze_prompt',
                details={'enhanced_prompt': enhanced_prompt, 'context': context},
                status='success',
                correlation_id=correlation_id
            )
            
            # Forward enhanced task to supervisor
            supervisor_task = self.supervisor_agent.create_task(
                description=str(enhanced_prompt),
                expected_output="Coordinated task execution result"
            )
            
            # Log supervisor task start
            await self.debug_console.log_event(
                event_type='task_start',
                agent=self.supervisor_agent.name,
                action='coordinate_task',
                details={'enhanced_prompt': enhanced_prompt},
                correlation_id=correlation_id
            )
            
            result = await self.supervisor_agent.execute(supervisor_task)
            
            # Log supervisor task completion
            await self.debug_console.log_event(
                event_type='task_complete',
                agent=self.supervisor_agent.name,
                action='coordinate_task',
                details=result,
                status=result['status'],
                correlation_id=correlation_id
            )
            
            return {
                'type': 'agent_response',
                'status': result['status'],
                'content': result.get('result'),
                'prompt_analysis': {
                    'enhanced_prompt': enhanced_prompt,
                    'context': context
                },
                'error': result.get('error'),
                'correlation_id': correlation_id
            }
            
        except Exception as e:
            error_msg = f'Task execution failed: {str(e)}'
            
            # Log error
            await self.debug_console.log_event(
                event_type='task_error',
                agent='message_handler',
                action='handle_task',
                details={'error': error_msg},
                status='error',
                correlation_id=correlation_id
            )
            
            return {
                'type': 'agent_response',
                'status': 'error',
                'error': error_msg,
                'correlation_id': correlation_id
            }

    async def _handle_tool_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution requests"""
        tool = data.get('tool')
        params = data.get('params', {})
        correlation_id = data.get('correlation_id')
        
        if not tool:
            return self._create_error_response('No tool specified')
        
        file_ops = self.prompt_agent.tools[0]  # Assuming FileOperations is the first tool
        
        # Dynamically find the FileOperations tool
        file_ops = None
        for tool in self.prompt_agent.tools:
            if isinstance(tool, FileOperations):
                file_ops = tool
                break

        if file_ops is None:
            return self._create_error_response("FileOperations tool not found")

        tool_mapping = {
            'read_file': file_ops.read_file,
            'create_file': file_ops.create_file,
            'list_files': file_ops.list_files,
            'delete_file': file_ops.delete_file,
            'rename_file': file_ops.rename_file,
            'copy_file': file_ops.copy_file,
            'get_file_info': file_ops.get_file_info,
            'create_directory': file_ops.create_directory
        }
        
        if tool not in tool_mapping:
            return self._create_error_response(f'Unknown tool: {tool}')
            
        try:
            # Log tool request
            await self.debug_console.log_event(
                event_type='tool_start',
                agent=self.prompt_agent.name,
                action=tool,
                details={'params': params},
                correlation_id=correlation_id
            )
            
            result = tool_mapping[tool](**params)
            
            # Log tool completion
            await self.debug_console.log_event(
                event_type='tool_complete',
                agent=self.prompt_agent.name,
                action=tool,
                details=result,
                status=result.get('status', 'unknown'),
                correlation_id=correlation_id
            )
            
            return {
                'type': 'tool_response',
                'status': result.get('status'),
                'result': result,
                'correlation_id': correlation_id
            }
        except Exception as e:
            # Log tool error
            await self.debug_console.log_event(
                event_type='tool_error',
                agent=self.prompt_agent.name,
                action=tool,
                details={'error': str(e)},
                status='error',
                correlation_id=correlation_id
            )
            
            return self._create_error_response(f'Tool execution failed: {str(e)}')

    async def _handle_debug_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle debug-related requests"""
        action = data.get('action')
        params = data.get('params', {})
        correlation_id = data.get('correlation_id')
        
        if action == 'get_events':
            events = await self.debug_console.get_events(**params)
            return {
                'type': 'debug_response',
                'events': events,
                'correlation_id': correlation_id
            }
        elif action == 'clear_logs':
            self.debug_console.clear_logs()
            return {
                'type': 'debug_response',
                'status': 'success',
                'message': 'Debug logs cleared',
                'correlation_id': correlation_id
            }
        else:
            return self._create_error_response(f'Unknown debug action: {action}')

    async def _handle_mode_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle mode-related requests"""
        action = data.get('action')
        mode_str = data.get('mode') # for switch_mode action
        correlation_id = data.get('correlation_id')

        if action == 'get_mode':
            current_mode = self.mode_manager.get_current_mode()
            description = self.mode_manager.get_mode_description()
            return {
                'type': 'mode_response',
                'mode': current_mode.value,
                'description': description,
                'status': 'success',
                'correlation_id': correlation_id
            }
        elif action == 'switch_mode':
            if not mode_str:
                return self._create_error_response('Mode value is required for switch_mode action')
            try:
                from ..modes.mode_manager import AgentMode # Import here to avoid circular dependency
                target_mode = AgentMode(mode_str)
                result = self.mode_manager.switch_mode(target_mode)
                return {
                    'type': 'mode_response',
                    'status': result['status'],
                    'message': result['message'],
                    'mode': target_mode.value,
                    'description': result['description'],
                    'correlation_id': correlation_id
                }
            except ValueError:
                return self._create_error_response(f'Invalid mode value: {mode_str}')
        else:
            return self._create_error_response(f'Unknown mode action: {action}')

    async def _handle_llm_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle LLM-related requests"""
        action = data.get('action')
        agent_name = data.get('agentName')
        provider = data.get('provider')
        config = data.get('config')
        correlation_id = data.get('correlation_id')

        if action == 'get_configs':
            configs = self.prompt_agent.llm_manager.get_all_agent_configs()
            return {
                'type': 'llm_response',
                'configs': configs,
                'correlation_id': correlation_id
            }
        elif action == 'get_providers':
            providers = self.prompt_agent.llm_manager.get_available_providers()
            return {
                'type': 'llm_response',
                'providers': {name: {'models': self.prompt_agent.llm_manager.get_available_models(name)} for name in providers},
                'correlation_id': correlation_id
            }
        elif action == 'get_models':
            if not provider:
                return self._create_error_response('Provider is required for get_models')
            models = self.prompt_agent.llm_manager.get_available_models(provider)
            return {
                'type': 'llm_response',
                'models': models,
                'correlation_id': correlation_id
            }
        elif action == 'save_config':
            if not agent_name or not config:
                return self._create_error_response('Agent name and config are required for save_config')
            self.prompt_agent.llm_manager.configure_agent_llm(agent_name, config)
            return {
                'type': 'llm_response',
                'status': 'success',
                'correlation_id': correlation_id
            }
        else:
            return self._create_error_response(f'Unknown LLM action: {action}')

    def _create_error_response(self, error_message: str) -> str:
        """Create error response message"""
        return json.dumps({
            'type': 'error',
            'error': error_message
        })

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Broadcast message to all connected clients"""
        if self.active_connections:
            message_str = json.dumps(message)
            await asyncio.gather(
                *[conn.send(message_str) for conn in self.active_connections]
            )

class WebSocketServer:
    def __init__(self, host: str, port: int, message_handler: MessageHandler):
        self.host = host
        self.port = port
        self.message_handler = message_handler
        
        # Set up WebSocket subscriber for debug events
        self.message_handler.websocket_subscriber = WebSocketSubscriber(self.message_handler)
        self.message_handler.debug_console.subscribe(
            self.message_handler.websocket_subscriber.handle_event
        )

    async def handle_connection(self, websocket, path):
        """Handle WebSocket connection"""
        try:
            # Add connection to active set
            self.message_handler.active_connections.add(websocket)
            
            async for message in websocket:
                response = await self.message_handler.handle_message(message, websocket)
                await websocket.send(response)
                
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            error_response = self.message_handler._create_error_response(str(e))
            await websocket.send(error_response)
        finally:
            # Remove connection from active set
            self.message_handler.active_connections.remove(websocket)

    async def start(self):
        """Start WebSocket server"""
        server = await websockets.serve(
            self.handle_connection,
            self.host,
            self.port
        )
        print(f"WebSocket server running on ws://{self.host}:{self.port}")
        await server.wait_closed()
