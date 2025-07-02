"""
Advanced monitoring and metrics collection for Image2Model application.
"""

import logging
import time
import json
import psutil
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from functools import wraps
from contextlib import asynccontextmanager
from dataclasses import dataclass, asdict
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
import structlog

# Metrics collectors
REGISTRY = CollectorRegistry()

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code'],
    registry=REGISTRY
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint'],
    registry=REGISTRY
)

# Application metrics
ACTIVE_JOBS = Gauge(
    'active_jobs_total',
    'Number of active processing jobs',
    registry=REGISTRY
)

CELERY_TASK_COUNT = Counter(
    'celery_tasks_total',
    'Total Celery tasks',
    ['task_name', 'status'],
    registry=REGISTRY
)

CELERY_TASK_DURATION = Histogram(
    'celery_task_duration_seconds',
    'Celery task duration',
    ['task_name'],
    registry=REGISTRY
)

# System metrics
CPU_USAGE = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage',
    registry=REGISTRY
)

MEMORY_USAGE = Gauge(
    'system_memory_usage_percent',
    'System memory usage percentage',
    registry=REGISTRY
)

DISK_USAGE = Gauge(
    'system_disk_usage_percent',
    'System disk usage percentage',
    registry=REGISTRY
)

# FAL.AI API metrics
FAL_API_REQUESTS = Counter(
    'fal_api_requests_total',
    'Total FAL.AI API requests',
    ['operation', 'status'],
    registry=REGISTRY
)

FAL_API_DURATION = Histogram(
    'fal_api_request_duration_seconds',
    'FAL.AI API request duration',
    ['operation'],
    registry=REGISTRY
)

@dataclass
class RequestMetrics:
    """Metrics data for HTTP requests."""
    method: str
    path: str
    status_code: int
    duration_ms: float
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    content_length: Optional[int] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

@dataclass
class TaskMetrics:
    """Metrics data for Celery tasks."""
    task_name: str
    task_id: str
    status: str
    duration_ms: Optional[float] = None
    correlation_id: Optional[str] = None
    worker_name: Optional[str] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

class StructuredLogger:
    """Enhanced structured logger with monitoring capabilities."""
    
    def __init__(self, name: str):
        self.logger = structlog.get_logger(name)
    
    def log_request(self, metrics: RequestMetrics):
        """Log HTTP request with structured data."""
        self.logger.info(
            "HTTP request processed",
            **asdict(metrics)
        )
        
        # Update Prometheus metrics
        REQUEST_COUNT.labels(
            method=metrics.method,
            endpoint=metrics.path,
            status_code=metrics.status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=metrics.method,
            endpoint=metrics.path
        ).observe(metrics.duration_ms / 1000.0)
    
    def log_task(self, metrics: TaskMetrics):
        """Log Celery task with structured data."""
        self.logger.info(
            "Celery task processed",
            **asdict(metrics)
        )
        
        # Update Prometheus metrics
        CELERY_TASK_COUNT.labels(
            task_name=metrics.task_name,
            status=metrics.status
        ).inc()
        
        if metrics.duration_ms:
            CELERY_TASK_DURATION.labels(
                task_name=metrics.task_name
            ).observe(metrics.duration_ms / 1000.0)
    
    def log_fal_api_call(self, operation: str, status: str, duration_ms: float, **kwargs):
        """Log FAL.AI API calls with metrics."""
        self.logger.info(
            "FAL.AI API call",
            operation=operation,
            status=status,
            duration_ms=duration_ms,
            timestamp=datetime.now(timezone.utc).isoformat(),
            **kwargs
        )
        
        # Update Prometheus metrics
        FAL_API_REQUESTS.labels(
            operation=operation,
            status=status
        ).inc()
        
        FAL_API_DURATION.labels(
            operation=operation
        ).observe(duration_ms / 1000.0)
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log errors with full context."""
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if context:
            error_data.update(context)
        
        self.logger.error(
            "Application error occurred",
            **error_data,
            exc_info=True
        )

class MonitoringMiddleware:
    """FastAPI middleware for comprehensive request monitoring."""
    
    def __init__(self):
        self.logger = StructuredLogger("app.middleware.monitoring")
    
    async def __call__(self, request: Request, call_next):
        """Process request with monitoring."""
        start_time = time.time()
        
        # Extract request information
        method = request.method
        path = request.url.path
        user_agent = request.headers.get("user-agent")
        client_ip = request.client.host if request.client else None
        content_length = request.headers.get("content-length")
        
        status_code = 500  # Default for exceptions
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
        except Exception as e:
            # Log the error and return 500
            self.logger.log_error(e, {
                "request_method": method,
                "request_path": path,
                "client_ip": client_ip
            })
            raise
        finally:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Create metrics
            metrics = RequestMetrics(
                method=method,
                path=path,
                status_code=status_code,
                duration_ms=duration_ms,
                user_agent=user_agent,
                ip_address=client_ip,
                content_length=int(content_length) if content_length else None
            )
            
            # Log request
            self.logger.log_request(metrics)
        
        return response

class SystemMonitor:
    """System resource monitoring."""
    
    def __init__(self):
        self.logger = StructuredLogger("app.monitoring.system")
    
    async def collect_system_metrics(self):
        """Collect and update system metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            CPU_USAGE.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            MEMORY_USAGE.set(memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            DISK_USAGE.set(disk.percent)
            
            # Log system metrics
            self.logger.logger.info(
                "System metrics collected",
                cpu_usage_percent=cpu_percent,
                memory_usage_percent=memory.percent,
                memory_available_gb=memory.available / (1024**3),
                disk_usage_percent=disk.percent,
                disk_free_gb=disk.free / (1024**3),
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
        except Exception as e:
            self.logger.log_error(e, {"context": "system_metrics_collection"})
    
    async def start_background_monitoring(self):
        """Start background system monitoring."""
        while True:
            await self.collect_system_metrics()
            await asyncio.sleep(60)  # Collect every minute

class TaskMonitor:
    """Celery task monitoring."""
    
    def __init__(self):
        self.logger = StructuredLogger("app.monitoring.tasks")
    
    def task_started(self, task_name: str, task_id: str, correlation_id: str = None):
        """Log task start."""
        metrics = TaskMetrics(
            task_name=task_name,
            task_id=task_id,
            status="started",
            correlation_id=correlation_id
        )
        self.logger.log_task(metrics)
        
        # Update active jobs
        ACTIVE_JOBS.inc()
    
    def task_completed(self, task_name: str, task_id: str, duration_ms: float, 
                      correlation_id: str = None, worker_name: str = None):
        """Log task completion."""
        metrics = TaskMetrics(
            task_name=task_name,
            task_id=task_id,
            status="completed",
            duration_ms=duration_ms,
            correlation_id=correlation_id,
            worker_name=worker_name
        )
        self.logger.log_task(metrics)
        
        # Update active jobs
        ACTIVE_JOBS.dec()
    
    def task_failed(self, task_name: str, task_id: str, error: Exception, 
                   correlation_id: str = None, worker_name: str = None):
        """Log task failure."""
        metrics = TaskMetrics(
            task_name=task_name,
            task_id=task_id,
            status="failed",
            correlation_id=correlation_id,
            worker_name=worker_name
        )
        self.logger.log_task(metrics)
        
        # Log the error
        self.logger.log_error(error, {
            "task_name": task_name,
            "task_id": task_id,
            "correlation_id": correlation_id
        })
        
        # Update active jobs
        ACTIVE_JOBS.dec()

def monitor_task(task_name: str):
    """Decorator for monitoring Celery tasks."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            task_monitor = TaskMonitor()
            task_id = kwargs.get('task_id', 'unknown')
            correlation_id = kwargs.get('correlation_id')
            
            start_time = time.time()
            task_monitor.task_started(task_name, task_id, correlation_id)
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                task_monitor.task_completed(task_name, task_id, duration_ms, correlation_id)
                return result
                
            except Exception as e:
                task_monitor.task_failed(task_name, task_id, e, correlation_id)
                raise
        
        return wrapper
    return decorator

@asynccontextmanager
async def monitor_fal_api_call(operation: str):
    """Context manager for monitoring FAL.AI API calls."""
    logger = StructuredLogger("app.monitoring.fal_api")
    start_time = time.time()
    
    try:
        yield logger
        duration_ms = (time.time() - start_time) * 1000
        logger.log_fal_api_call(operation, "success", duration_ms)
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.log_fal_api_call(operation, "error", duration_ms, error=str(e))
        logger.log_error(e, {"operation": operation})
        raise

def get_metrics_data() -> str:
    """Get Prometheus metrics data."""
    return generate_latest(REGISTRY)

# Global monitors
system_monitor = SystemMonitor()
task_monitor = TaskMonitor()