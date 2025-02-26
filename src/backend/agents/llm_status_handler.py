import logging

logger = logging.getLogger(__name__)

def get_llm_status(backend):
    """Get LLM status"""
    # TODO: Implement actual LLM status check
    backend._send_response({
        'status': 'ready',
        'provider': 'default'
    })