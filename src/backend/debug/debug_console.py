import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import os

@dataclass
class DebugEvent:
    timestamp: str
    event_type: str
    agent: str
    action: str
    details: Dict[str, Any]
    status: str
    correlation_id: Optional[str] = None

class DebugConsole:
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.debug_dir = os.path.join(workspace_path, '.crewai_debug')
        self.event_log_path = os.path.join(self.debug_dir, 'event_log.jsonl')
        self.subscribers = []
        self._setup_debug_directory()

    def _setup_debug_directory(self) -> None:
        """Create debug directory if it doesn't exist"""
        os.makedirs(self.debug_dir, exist_ok=True)
        if not os.path.exists(self.event_log_path):
            with open(self.event_log_path, 'w', encoding='utf-8') as f:
                pass  # Create empty file

    def subscribe(self, callback) -> None:
        """Subscribe to debug events"""
        self.subscribers.append(callback)

    def unsubscribe(self, callback) -> None:
        """Unsubscribe from debug events"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)

    async def log_event(self, 
                       event_type: str,
                       agent: str,
                       action: str,
                       details: Dict[str, Any],
                       status: str = 'info',
                       correlation_id: Optional[str] = None) -> None:
        """Log a debug event and notify subscribers"""
        event = DebugEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            agent=agent,
            action=action,
            details=details,
            status=status,
            correlation_id=correlation_id
        )
        
        # Log to file
        await self._write_event(event)
        
        # Notify subscribers
        await self._notify_subscribers(event)

    async def _write_event(self, event: DebugEvent) -> None:
        """Write event to log file"""
        try:
            event_dict = {
                'timestamp': event.timestamp,
                'event_type': event.event_type,
                'agent': event.agent,
                'action': event.action,
                'details': event.details,
                'status': event.status,
                'correlation_id': event.correlation_id
            }
            
            async with aiofiles.open(self.event_log_path, 'a', encoding='utf-8') as f:
                await f.write(json.dumps(event_dict) + '\n')
        except Exception as e:
            print(f"Error writing debug event: {e}")

    async def _notify_subscribers(self, event: DebugEvent) -> None:
        """Notify all subscribers of new event"""
        event_dict = {
            'timestamp': event.timestamp,
            'event_type': event.event_type,
            'agent': event.agent,
            'action': event.action,
            'details': event.details,
            'status': event.status,
            'correlation_id': event.correlation_id
        }
        
        for callback in self.subscribers:
            try:
                await callback(event_dict)
            except Exception as e:
                print(f"Error notifying subscriber: {e}")

    async def get_events(self,
                        start_time: Optional[str] = None,
                        end_time: Optional[str] = None,
                        event_types: Optional[List[str]] = None,
                        agents: Optional[List[str]] = None,
                        correlation_id: Optional[str] = None,
                        limit: int = 100) -> List[Dict[str, Any]]:
        """Query debug events with filters"""
        events = []
        try:
            async with aiofiles.open(self.event_log_path, 'r', encoding='utf-8') as f:
                async for line in f:
                    if line.strip():
                        event = json.loads(line)
                        
                        # Apply filters
                        if start_time and event['timestamp'] < start_time:
                            continue
                        if end_time and event['timestamp'] > end_time:
                            continue
                        if event_types and event['event_type'] not in event_types:
                            continue
                        if agents and event['agent'] not in agents:
                            continue
                        if correlation_id and event['correlation_id'] != correlation_id:
                            continue
                        
                        events.append(event)
                        
                        if len(events) >= limit:
                            break
                            
        except Exception as e:
            print(f"Error reading debug events: {e}")
            
        return events

    def clear_logs(self) -> None:
        """Clear all debug logs"""
        try:
            with open(self.event_log_path, 'w', encoding='utf-8') as f:
                pass  # Truncate file
        except Exception as e:
            print(f"Error clearing debug logs: {e}")

class DebugSubscriber:
    """Base class for debug event subscribers"""
    async def handle_event(self, event: Dict[str, Any]) -> None:
        """Handle debug event - override in subclasses"""
        raise NotImplementedError()

class ConsoleSubscriber(DebugSubscriber):
    """Subscriber that prints events to console"""
    async def handle_event(self, event: Dict[str, Any]) -> None:
        print(f"[{event['timestamp']}] {event['agent']}.{event['action']} - {event['status']}")
        print(f"Details: {json.dumps(event['details'], indent=2)}")
        print("-" * 80)

class WebSocketSubscriber(DebugSubscriber):
    """Subscriber that forwards events to WebSocket clients"""
    def __init__(self, websocket_handler):
        self.websocket_handler = websocket_handler

    async def handle_event(self, event: Dict[str, Any]) -> None:
        await self.websocket_handler.broadcast({
            'type': 'debug_event',
            'event': event
        })
