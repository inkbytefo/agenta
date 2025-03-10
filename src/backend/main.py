import json
import sys
import threading
import logging
from src.backend.agents.task_handler import handle_task
from typing import Any, Dict, Optional
from datetime import datetime
from queue import Queue
from src.backend.agents.mode_handler import get_mode
from src.backend.agents.llm_status_handler import get_llm_status
from src.backend.agents.debug_events_handler import get_debug_events
from src.backend.agents.clear_debug_logs_handler import clear_debug_logs
from src.backend.config.config_manager import init_config_manager, get_config_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Backend:
    def __init__(self):
        self.command_queue: Queue = Queue()
        self.current_mode: str = "default"
        self.llm_configs: Dict[str, Dict] = {}
        self.debug_events: list = []
        self.running: bool = True

    def start(self):
        """Start the backend server"""
        logger.info("Starting backend server...")
        
        # Start command processing thread
        threading.Thread(target=self._process_commands, daemon=True).start()
        
        # Main loop to read from stdin
        while self.running:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                # Parse command
                try:
                    command = json.loads(line)
                    self.command_queue.put(command)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse command: {e}")
                    self._send_error(f"Invalid JSON: {e}")
                except Exception as e:
                    logger.error(f"Error reading from stdin: {e}")
                    break
            except Exception as e:
                logger.error(f"Error reading from stdin: {e}")
                break

        logger.info("Backend server stopped")

    def _process_commands(self):
        """Process commands from the queue"""
        while self.running:
            try:
                command = self.command_queue.get()
                if not command:
                    continue

                cmd_type = command.get('command')
                args = command.get('args', {})

                if cmd_type == 'handle_task':
                    handle_task(args, self)
                elif cmd_type == 'get_mode':
                    get_mode(self)
                elif cmd_type == 'get_llm_status':
                    get_llm_status(self)
                elif cmd_type == 'get_debug_events':
                    get_debug_events(self)
                elif cmd_type == 'clear_debug_logs':
                    clear_debug_logs(self)
                elif cmd_type == 'get_llm_providers':
                    self._get_llm_providers()
                elif cmd_type == 'get_llm_configs':
                    self._get_llm_configs()
                elif cmd_type == 'save_llm_config':
                    self._save_llm_config(args)
                else:
                    self._send_error(f"Unknown command: {cmd_type}")

            except Exception as e:
                logger.error(f"Error processing command: {e}")
                self._send_error(str(e))

    def _send_response(self, data: Any = None, error: Optional[str] = None):
        """Send response to Tauri"""
        response = {
            'status': 'error' if error else 'success',
            'data': data,
            'error': error
        }
        print(json.dumps(response), flush=True)

    def _send_error(self, error: str):
        """Send error response"""
        self._send_response(error=error)

    def _add_debug_event(self, level: str, message: str, details: Dict = None):
        """Add a debug event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'details': details
        }
        self.debug_events.append(event)
        logger.log(
            getattr(logging, level.upper(), logging.INFO),
            message,
            extra={'details': details}
        )

    # Command handlers

    def _get_llm_providers(self):
        """Get available LLM providers"""
        # TODO: Implement actual provider detection
        providers = {
            'openai': {
                'name': 'OpenAI',
                'models': ['gpt-3.5-turbo', 'gpt-4'],
                'requiresApiKey': True
            },
            'anthropic': {
                'name': 'Anthropic',
                'models': ['claude-2', 'claude-instant'],
                'requiresApiKey': True
            }
        }
        self._send_response(providers)

    def _get_llm_configs(self):
        """Get LLM configurations"""
        self._send_response(self.llm_configs)

    def _save_llm_config(self, config: Dict):
        """Save LLM configuration"""
        provider = config.get('provider')
        if not provider:
            return self._send_error("No provider specified")

        self.llm_configs[provider] = config
        self._add_debug_event('info', f"Saved config for provider: {provider}")
        self._send_response()

if __name__ == '__main__':
    config_dir = os.path.join(os.getcwd(), "src/backend/config")
    init_config_manager(config_dir)
    backend = Backend()
    try:
        backend.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Backend error: {e}")
    finally:
        backend.running = False
