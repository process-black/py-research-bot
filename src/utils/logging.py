"""Structured logging setup for the application."""

import logging
import os


def setup_logging():
    """Configure structured logging for the application."""
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
        ]
    )
    
    return logging.getLogger('research_bot')