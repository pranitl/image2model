"""
Celery application for background tasks with Redis configuration.
"""

import os
import logging
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure, task_retry, worker_ready
from celery.schedules import crontab
from app.core.config import settings
from app.core.logging_config import setup_logging, set_correlation_id, get_task_logger

# Create Celery app instance
celery_app = Celery(
    "ai_3d_generator",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks", "app.workers.cleanup"]
)

# Configure Celery
celery_app.conf.update(
    # Serialization settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Timezone settings
    timezone="UTC",
    enable_utc=True,
    
    # Task tracking and state
    task_track_started=True,
    task_send_sent_event=True,
    
    # Task time limits (30 minutes hard, 25 minutes soft)
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    
    # Result expiration
    result_expires=3600,  # 1 hour
    
    # Worker settings optimized for parallel processing
    worker_prefetch_multiplier=1,  # Disable prefetching for fair distribution
    worker_max_tasks_per_child=50,  # Restart workers more frequently to avoid memory leaks
    task_acks_on_failure_or_timeout=True,  # Acknowledge failed tasks
    
    # Task routing (can be expanded later)
    task_routes={
        'app.workers.tasks.process_batch': {'queue': 'batch_processing'},
        'app.workers.tasks.process_file_in_batch': {'queue': 'model_generation'},  # Distribute file processing across workers
        'app.workers.tasks.generate_3d_model_task': {'queue': 'model_generation'},
        'app.workers.cleanup.cleanup_old_files': {'queue': 'maintenance'},
        'app.workers.cleanup.get_disk_usage': {'queue': 'maintenance'},
        'app.workers.cleanup.cleanup_job_files': {'queue': 'maintenance'},
    },
    
    # Celery Beat schedule for periodic tasks
    beat_schedule={
        'cleanup-old-files': {
            'task': 'app.workers.cleanup.cleanup_old_files',
            'schedule': crontab(hour=2, minute=0),  # Run daily at 2 AM
        },
        'disk-usage-monitoring': {
            'task': 'app.workers.cleanup.get_disk_usage',
            'schedule': crontab(minute=0),  # Run hourly
        },
    },
    
    # Default queue configurations
    task_default_queue='default',
    task_default_exchange='default',
    task_default_exchange_type='direct',
    task_default_routing_key='default',
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_acks_late=True,
    
    # Connection pool settings for Redis
    broker_pool_limit=10,  # Redis connection pool size
    result_backend_pool_limit=10,  # Result backend pool size
    broker_connection_retry_on_startup=True,  # Retry broker connection on startup
    
    # Monitoring
    worker_send_task_events=True,
    task_send_events=True,
)

# Additional queue configuration for different types of tasks
celery_app.conf.task_routes = {
    # High priority tasks
    'app.workers.tasks.health_check_task': {'queue': 'priority'},
    
    # Batch processing tasks
    'app.workers.tasks.process_batch': {'queue': 'batch_processing'},
    
    # Model generation tasks - distributed across workers
    'app.workers.tasks.process_file_in_batch': {'queue': 'model_generation'},
    'app.workers.tasks.generate_3d_model_task': {'queue': 'model_generation'},
    
    # Maintenance tasks
    'app.workers.cleanup.cleanup_old_files': {'queue': 'maintenance'},
    'app.workers.cleanup.get_disk_usage': {'queue': 'maintenance'},
    'app.workers.cleanup.cleanup_job_files': {'queue': 'maintenance'},
}

# Configure logging
celery_app.conf.worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
celery_app.conf.worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'

# Celery signal handlers for comprehensive error handling and logging

@worker_ready.connect
def setup_worker_logging(sender=None, **kwargs):
    """Set up logging when worker starts."""
    setup_logging()
    logger = get_task_logger('worker', 'startup')
    logger.info(f"Worker ready: {sender}")

@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Handle task start - set up logging context."""
    correlation_id = set_correlation_id()
    logger = get_task_logger(task.name, task_id)
    logger.info(f"Starting task {task.name} with ID {task_id} (correlation: {correlation_id})")

@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, 
                        retval=None, state=None, **kwds):
    """Handle task completion."""
    logger = get_task_logger(task.name, task_id)
    logger.info(f"Task {task.name} completed with state: {state}")

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwds):
    """Handle task failures with detailed logging."""
    logger = get_task_logger(sender.name if sender else 'unknown', task_id)
    logger.error(
        f"Task {sender.name if sender else 'unknown'} failed with exception: {exception}",
        exc_info=einfo if einfo else True,
        extra={
            'task_id': task_id,
            'exception_type': type(exception).__name__ if exception else 'Unknown',
            'exception_message': str(exception) if exception else 'No message',
            'traceback': traceback
        }
    )

@task_retry.connect
def task_retry_handler(sender=None, task_id=None, reason=None, einfo=None, **kwds):
    """Handle task retries."""
    logger = get_task_logger(sender.name if sender else 'unknown', task_id)
    logger.warning(f"Task {sender.name if sender else 'unknown'} retry: {reason}")

# Dead letter queue configuration for failed tasks
# Note: task_reject_on_worker_lost and task_acks_late are already set above

# Error handling configuration
celery_app.conf.update(
    # Task error handling
    task_publish_retry=True,
    task_publish_retry_policy={
        'max_retries': 3,
        'interval_start': 0,
        'interval_step': 0.2,
        'interval_max': 0.2,
    },
    
    # Worker error handling
    worker_disable_rate_limits=False,
    worker_max_memory_per_child=200000,  # 200MB per child process
)

if __name__ == '__main__':
    celery_app.start()
