"""
Logging configuration for quant-fundamentals.
Provides structured logging across all modules.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: str = None,
    console: bool = True
) -> logging.Logger:
    """
    Set up a logger with consistent formatting.
    
    Parameters:
    -----------
    name : str
        Logger name (typically __name__)
    level : int
        Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    log_file : str, optional
        Path to log file. If None, no file logging.
    console : bool
        Whether to log to console
    
    Returns:
    --------
    logging.Logger : Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_default_logger(module_name: str) -> logging.Logger:
    """
    Get a default logger for a module.
    
    Parameters:
    -----------
    module_name : str
        Name of the module (use __name__)
    
    Returns:
    --------
    logging.Logger : Configured logger
    """
    # Create logs directory
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # Log file with date
    log_file = log_dir / f'quant_fundamentals_{datetime.now().strftime("%Y%m%d")}.log'
    
    return setup_logger(
        name=module_name,
        level=logging.INFO,
        log_file=str(log_file),
        console=False  # Don't spam console by default
    )


# Performance logger for timing operations
class PerformanceLogger:
    """Context manager for logging performance metrics."""
    
    def __init__(self, logger: logging.Logger, operation: str):
        """
        Initialize performance logger.
        
        Parameters:
        -----------
        logger : logging.Logger
            Logger to use
        operation : str
            Description of operation being timed
        """
        self.logger = logger
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        """Start timing."""
        import time
        self.start_time = time.time()
        self.logger.debug(f"Starting: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log duration."""
        import time
        duration = time.time() - self.start_time
        
        if exc_type is None:
            self.logger.info(f"Completed: {self.operation} in {duration:.4f}s")
        else:
            self.logger.error(f"Failed: {self.operation} after {duration:.4f}s - {exc_val}")
        
        return False  # Don't suppress exceptions


# Example usage
if __name__ == "__main__":
    # Test logger
    logger = setup_logger("test", level=logging.DEBUG, console=True)
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning")
    logger.error("This is an error")
    
    # Test performance logger
    with PerformanceLogger(logger, "Test operation"):
        import time
        time.sleep(0.1)
    
    print("Logger test complete")
