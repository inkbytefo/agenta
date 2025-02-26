import logging

logger = logging.getLogger(__name__)

def get_mode(backend):
    """Get current mode"""
    backend._send_response({
        'mode': backend.current_mode,
        'status': 'success'
    })