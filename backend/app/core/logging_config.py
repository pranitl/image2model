"""
Logging configuration for Celery workers and tasks.
"""

import logging
import logging.config
import sys
from typing import Dict, Any
import uuid
import contextvars
from datetime import datetime

# Context variable for correlation ID tracking
correlation_id_var: contextvars.ContextVar[str] = contextvars.ContextVar('correlation_id', default='')

class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to log records for request tracking."""
    
    def filter(self, record):
        record.correlation_id = correlation_id_var.get() or 'no-correlation-id'
        return True

class TaskFilter(logging.Filter):
    """Add task information to log records."""
    
    def filter(self, record):
        # Add task name and ID if available
        task_name = getattr(record, 'task_name', 'unknown-task')
        task_id = getattr(record, 'task_id', 'unknown-id')
        record.task_name = task_name
        record.task_id = task_id
        return True

def setup_logging() -> None:
    """Configure structured logging for Celery workers."""
    
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] [%(correlation_id)s] [%(task_name)s:%(task_id)s] %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '[%(asctime)s] %(levelname)s %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'json': {
                'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "correlation_id": "%(correlation_id)s", "task_name": "%(task_name)s", "task_id": "%(task_id)s", "message": "%(message)s", "module": "%(module)s", "function": "%(funcName)s", "line": %(lineno)d}',
                'datefmt': '%Y-%m-%dT%H:%M:%S'
            }
        },
        'filters': {
            'correlation_id': {
                '()': CorrelationIdFilter,
            },
            'task_info': {
                '()': TaskFilter,
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'detailed',
                'filters': ['correlation_id', 'task_info'],
                'stream': sys.stdout
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'json',
                'filters': ['correlation_id', 'task_info'],
                'filename': 'logs/celery_worker.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'json',
                'filters': ['correlation_id', 'task_info'],
                'filename': 'logs/celery_errors.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            }
        },
        'loggers': {
            'app.workers': {
                'level': 'DEBUG',
                'handlers': ['console', 'file', 'error_file'],
                'propagate': False
            },
            'celery': {
                'level': 'INFO',
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'celery.task': {
                'level': 'INFO',
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'celery.worker': {
                'level': 'INFO',
                'handlers': ['console', 'file'],
                'propagate': False
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console']
        }
    }
    
    # Create logs directory if it doesn't exist
    import os
    os.makedirs('logs', exist_ok=True)
    
    logging.config.dictConfig(logging_config)

def set_correlation_id(correlation_id: str = None) -> str:
    """Set correlation ID for the current context."""
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    correlation_id_var.set(correlation_id)
    return correlation_id

def get_correlation_id() -> str:
    """Get the current correlation ID."""
    return correlation_id_var.get()

class TaskLogger:
    """Enhanced logger for tasks with correlation ID and task context."""
    
    def __init__(self, task_name: str = None, task_id: str = None):
        self.logger = logging.getLogger('app.workers.tasks')
        self.task_name = task_name
        self.task_id = task_id
    
    def _log(self, level: int, message: str, *args, **kwargs):
        """Enhanced logging with task context."""
        extra = kwargs.get('extra', {})
        extra.update({
            'task_name': self.task_name or 'unknown-task',
            'task_id': self.task_id or 'unknown-id'
        })
        kwargs['extra'] = extra
        self.logger.log(level, message, *args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        self._log(logging.DEBUG, message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        self._log(logging.INFO, message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        self._log(logging.WARNING, message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        self._log(logging.ERROR, message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        self._log(logging.CRITICAL, message, *args, **kwargs)

def get_task_logger(task_name: str = None, task_id: str = None) -> TaskLogger:
    """Get a task-aware logger."""
    return TaskLogger(task_name, task_id)