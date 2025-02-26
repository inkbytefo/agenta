import logging

logger = logging.getLogger(__name__)

def clear_debug_logs(backend):
    """Clear debug logs"""
    backend.debug_events.clear()
    backend._send_response()