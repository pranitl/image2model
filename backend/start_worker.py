#!/usr/bin/env python3
"""
Celery worker startup script with proper logging configuration.
"""

import os
import sys
import signal
import logging
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from app.core.celery_app import celery_app
from app.core.logging_config import setup_logging

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger = logging.getLogger(__name__)
    logger.info(f"Received signal {signum}, shutting down worker gracefully...")
    sys.exit(0)

def main():
    """Start the Celery worker with proper configuration."""
    
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting Celery worker for Image2Model AI 3D Generator")
    logger.info(f"Python path: {sys.path}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    
    # Worker configuration
    worker_options = {
        'loglevel': 'INFO',
        'concurrency': 2,  # Adjust based on server capacity
        'queues': ['default', 'batch_processing', 'model_generation', 'maintenance', 'priority'],
        'hostname': 'image2model-worker@%h',
        'pool': 'prefork',  # Use prefork pool for better isolation
        'optimization': 'fair',  # Fair task distribution
        'max_tasks_per_child': 1000,  # Restart workers after 1000 tasks to prevent memory leaks
        'max_memory_per_child': 200000,  # 200MB memory limit per child
    }
    
    try:
        logger.info(f"Starting worker with options: {worker_options}")
        
        # Start the worker
        celery_app.worker_main([
            'worker',
            f'--loglevel={worker_options["loglevel"]}',
            f'--concurrency={worker_options["concurrency"]}',
            f'--queues={",".join(worker_options["queues"])}',
            f'--hostname={worker_options["hostname"]}',
            f'--pool={worker_options["pool"]}',
            f'--optimization={worker_options["optimization"]}',
            f'--max-tasks-per-child={worker_options["max_tasks_per_child"]}',
            f'--max-memory-per-child={worker_options["max_memory_per_child"]}',
            '--without-gossip',  # Disable gossip for better performance
            '--without-mingle',  # Disable mingle for faster startup
            '--without-heartbeat',  # Disable heartbeat for simpler setup
        ])
        
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Worker failed to start: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()