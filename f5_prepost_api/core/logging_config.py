import logging
import os
import sys
from pathlib import Path

_logging_initialized = False

def setup_logging(log_level=logging.INFO):
    """
    Set up application-wide logging configuration.
    
    Args:
        log_level: The logging level to use (default: INFO)
    """
    global _logging_initialized
    
    if _logging_initialized:
        return logging.getLogger()
    
    # Ensure log directory exists
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "api.log"
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove any existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create handlers
    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set formatter for handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to the root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Log a test message
    root_logger.info("Logging system initialized")
    
    _logging_initialized = True
    
    return root_logger 