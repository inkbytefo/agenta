import logging

logger = logging.getLogger(__name__)

def get_debug_events(backend):
    """Get debug events"""
    backend._send_response(backend.debug_events)