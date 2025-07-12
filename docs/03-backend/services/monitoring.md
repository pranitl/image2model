# Monitoring and Observability

## Overview

The Image2Model backend implements essential monitoring and observability features focused on practical, reliable system monitoring. The implementation includes Prometheus metrics collection, structured logging with correlation IDs, comprehensive health endpoints, and system resource monitoring.

## Architecture Overview

```mermaid
graph TB
    subgraph "Application Layer"
        APP[FastAPI App]
        WORKER[Celery Workers]
        BG[System Monitor]
    end
    
    subgraph "Monitoring"
        MW[MonitoringMiddleware]
        METRICS[Prometheus Metrics]
        LOGS[Structured Logs]
        HEALTH[Health Endpoints]
    end
    
    subgraph "Storage"
        FILES[Log Files]
        PROM[/metrics Endpoint]
    end
    
    APP --> MW
    MW --> METRICS
    MW --> LOGS
    
    WORKER --> LOGS
    BG --> METRICS
    BG --> LOGS
    
    HEALTH --> METRICS
    METRICS --> PROM
    LOGS --> FILES
```

## Structured Logging

The Image2Model backend uses structured logging with correlation ID support and task-aware logging for Celery workers. The implementation uses both standard Python logging and structlog for enhanced structured output.

### Logging Configuration (`backend/app/core/logging_config.py`)

The logging system is configured with multiple formatters and handlers:

```python
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
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'detailed',
                'filters': ['correlation_id', 'task_info']
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'json',
                'filename': 'logs/celery_worker.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'json',
                'filename': 'logs/celery_errors.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            }
        }
    }
```

### Structlog Configuration

The application also uses structlog for enhanced structured logging, configured in `main.py`:

```python
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.CallsiteParameterAdder(
            parameters=[structlog.processors.CallsiteParameter.FILENAME,
                       structlog.processors.CallsiteParameter.FUNC_NAME,
                       structlog.processors.CallsiteParameter.LINENO]
        ),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer() if settings.DEBUG else structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

### Correlation ID Support

The system automatically tracks requests and tasks using correlation IDs:

```python
# Context variable for correlation ID tracking
correlation_id_var: contextvars.ContextVar[str] = contextvars.ContextVar('correlation_id', default='')

class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to log records for request tracking."""
    
    def filter(self, record):
        record.correlation_id = correlation_id_var.get() or 'no-correlation-id'
        return True

def set_correlation_id(correlation_id: str = None) -> str:
    """Set correlation ID for the current context."""
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    correlation_id_var.set(correlation_id)
    return correlation_id
```

### Task-Aware Logging

The `TaskLogger` provides enhanced logging for Celery tasks:

```python
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
```

## Prometheus Metrics Collection

The Image2Model backend uses Prometheus for comprehensive metrics collection covering HTTP requests, Celery tasks, system resources, and FAL.AI API interactions.

### Metrics Registry (`backend/app/core/monitoring.py`)

All metrics are collected in a custom registry for clean separation:

```python
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest

# Custom metrics registry
REGISTRY = CollectorRegistry()

# HTTP Request metrics
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

# Celery task metrics
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

# System resource metrics
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
```

### Metrics Export

Metrics are exposed via the `/health/metrics` endpoint:

```python
def get_metrics_data() -> str:
    """Get Prometheus metrics data."""
    return generate_latest(REGISTRY)
```

### Structured Data Classes

The monitoring system uses structured data classes for metrics collection:

```python
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
```

## Monitoring Middleware

The `MonitoringMiddleware` provides comprehensive request monitoring, automatically collecting metrics and structured logs for all HTTP requests.

### Implementation

```python
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
            # Log the error
            self.logger.log_error(e, {
                "request_method": method,
                "request_path": path,
                "client_ip": client_ip
            })
            raise
        finally:
            # Calculate duration and create metrics
            duration_ms = (time.time() - start_time) * 1000
            
            metrics = RequestMetrics(
                method=method,
                path=path,
                status_code=status_code,
                duration_ms=duration_ms,
                user_agent=user_agent,
                ip_address=client_ip,
                content_length=int(content_length) if content_length else None
            )
            
            # Log request and update metrics
            self.logger.log_request(metrics)
        
        return response
```

### Integration

The middleware is integrated in `main.py`:

```python
# Add monitoring middleware
monitoring_middleware = MonitoringMiddleware()
app.middleware("http")(monitoring_middleware)
```

## System Monitoring

Background system monitoring collects resource usage metrics automatically.

### System Monitor Implementation

```python
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
```

### Background Task Setup

System monitoring is started during application lifespan:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    
    # Start background system monitoring
    monitoring_task = asyncio.create_task(system_monitor.start_background_monitoring())
    
    yield
    
    # Shutdown
    monitoring_task.cancel()
    try:
        await monitoring_task
    except asyncio.CancelledError:
        pass
```

## Task Monitoring

Celery task monitoring provides comprehensive tracking of background job execution.

### Task Monitor Implementation

```python
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
        self.logger.log_error(error, {
            "task_name": task_name,
            "task_id": task_id,
            "correlation_id": correlation_id
        })
        ACTIVE_JOBS.dec()
```

### Task Decorator

A convenience decorator is provided for automatic task monitoring:

```python
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
```

## FAL.AI API Monitoring

Specialized monitoring for FAL.AI API interactions using context managers.

### Context Manager Implementation

```python
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
```

### Usage Example

```python
async def generate_model(prompt: str):
    async with monitor_fal_api_call("model_generation") as logger:
        logger.logger.info("Starting model generation", prompt=prompt)
        # FAL.AI API call here
        result = await fal_client.generate(prompt)
        return result
```

## Health Check Endpoints

Comprehensive health monitoring with multiple endpoints for different use cases.

### Available Endpoints

- **`/health`** - Basic health check
- **`/health/detailed`** - Comprehensive system status
- **`/health/metrics`** - Prometheus metrics
- **`/health/liveness`** - Kubernetes liveness probe
- **`/health/readiness`** - Kubernetes readiness probe

### Health Check Implementation (`backend/app/api/endpoints/health.py`)

```python
class HealthChecker:
    """Comprehensive health checking for all system components."""
    
    def __init__(self):
        self.start_time = time.time()
    
    async def check_redis(self) -> ComponentHealth:
        """Check Redis connectivity and performance."""
        # Implementation details...
    
    async def check_celery(self) -> ComponentHealth:
        """Check Celery worker availability."""
        # Check if workers are available
        from app.core.celery_app import celery_app
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        
        if active_workers:
            return ComponentHealth(
                name="celery",
                status="healthy",
                response_time_ms=response_time,
                details={
                    "active_workers": len(active_workers),
                    "workers": list(active_workers.keys())
                }
            )
    
    async def check_disk_space(self) -> ComponentHealth:
        """Check disk space availability."""
        disk_usage = psutil.disk_usage('/')
        usage_percent = (disk_usage.used / disk_usage.total) * 100
        
        if usage_percent > 95:
            status = "unhealthy"
        elif usage_percent > 85:
            status = "degraded"
        else:
            status = "healthy"
    
    async def check_all_components(self) -> List[ComponentHealth]:
        """Check all system components concurrently."""
        tasks = [
            self.check_redis(),
            self.check_celery(),
            self.check_disk_space(),
            self.check_fal_api()
        ]
        return await asyncio.gather(*tasks)
```

### Detailed Health Response

```python
@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """Comprehensive health check with system and component information."""
    try:
        # Get system information
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        system_info = {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "cpu_usage_percent": cpu_percent,
            "memory_usage_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "disk_usage_percent": round((disk.used / disk.total) * 100, 2),
            "disk_free_gb": round(disk.free / (1024**3), 2),
            "load_average": list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else None
        }
        
        # Check all components
        components = await health_checker.check_all_components()
        overall_status = health_checker.get_overall_status(components)
        
        # Calculate uptime
        uptime_seconds = time.time() - health_checker.start_time
        
        response = DetailedHealthResponse(
            status=overall_status,
            service="image2model-backend",
            version="1.0.0",
            timestamp=datetime.now(timezone.utc).isoformat(),
            system=system_info,
            components=components,
            uptime_seconds=uptime_seconds
        )
        
        # Return 503 if unhealthy
        if overall_status == "unhealthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=response.dict()
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Health check failed", "message": str(e)}
        )
```

### Metrics Endpoint

```python
@router.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint. Returns metrics in Prometheus format."""
    try:
        metrics_data = get_metrics_data()
        return Response(
            content=metrics_data,
            media_type="text/plain; version=0.0.4; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"Failed to generate metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to generate metrics"}
        )
```

### Kubernetes Probes

```python
@router.get("/liveness")
async def liveness_probe():
    """Kubernetes liveness probe endpoint."""
    return {"status": "alive", "timestamp": datetime.now(timezone.utc).isoformat()}

@router.get("/readiness")
async def readiness_probe():
    """Kubernetes readiness probe endpoint."""
    try:
        components = await health_checker.check_all_components()
        
        # Consider ready if no critical components are unhealthy
        critical_failures = [c for c in components if c.status == "unhealthy" and c.name in ["celery", "disk_space"]]
        
        if critical_failures:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "status": "not_ready",
                    "failed_components": [c.name for c in critical_failures]
                }
            )
        
        return {
            "status": "ready",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": [{"name": c.name, "status": c.status} for c in components]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness check failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "error": str(e)}
        )
```

## Structured Logger

The `StructuredLogger` class provides enhanced logging with automatic metrics integration.

### Implementation

```python
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
```

## Log Management

Basic log management using Python's `RotatingFileHandler`.

### Configuration

Logs are automatically rotated when they reach 10MB with 5 backup files retained:

```python
'file': {
    'class': 'logging.handlers.RotatingFileHandler',
    'level': 'DEBUG',
    'formatter': 'json',
    'filename': 'logs/celery_worker.log',
    'maxBytes': 10485760,  # 10MB
    'backupCount': 5
},
'error_file': {
    'class': 'logging.handlers.RotatingFileHandler',
    'level': 'ERROR',
    'formatter': 'json',
    'filename': 'logs/celery_errors.log',
    'maxBytes': 10485760,  # 10MB
    'backupCount': 5
}
```

### Log Structure

Logs are written in JSON format with structured data:

```json
{
  "timestamp": "2024-01-15T10:30:45",
  "level": "INFO",
  "logger": "app.middleware.monitoring",
  "correlation_id": "123e4567-e89b-12d3-a456-426614174000",
  "task_name": "generate_model",
  "task_id": "456e7890-e89b-12d3-a456-426614174001",
  "message": "HTTP request processed",
  "module": "monitoring",
  "function": "log_request",
  "line": 142
}
```

## Available Metrics

The following Prometheus metrics are collected and exposed via `/health/metrics`:

### HTTP Request Metrics
- `http_requests_total` - Total HTTP requests by method, endpoint, and status code
- `http_request_duration_seconds` - HTTP request duration histogram

### Celery Task Metrics
- `celery_tasks_total` - Total Celery tasks by name and status
- `celery_task_duration_seconds` - Celery task duration histogram
- `active_jobs_total` - Number of currently active processing jobs

### System Resource Metrics
- `system_cpu_usage_percent` - Current CPU usage percentage
- `system_memory_usage_percent` - Current memory usage percentage
- `system_disk_usage_percent` - Current disk usage percentage

### FAL.AI API Metrics
- `fal_api_requests_total` - Total FAL.AI API requests by operation and status
- `fal_api_request_duration_seconds` - FAL.AI API request duration histogram

## Best Practices

### 1. Logging Guidelines
- Use structured logging with correlation IDs
- Log at appropriate levels (DEBUG for development, INFO+ for production)
- Avoid logging sensitive data (API keys, user data)
- Use context variables for request tracking

### 2. Metrics Collection
- Monitor essential business metrics (model generations, request rates)
- Use meaningful metric names and labels
- Avoid high cardinality labels
- Regular monitoring of resource usage

### 3. Health Monitoring
- Use different endpoints for different purposes:
  - `/health` - Basic status check
  - `/health/detailed` - Comprehensive system status
  - `/health/liveness` - For Kubernetes liveness probes
  - `/health/readiness` - For Kubernetes readiness probes

### 4. Performance Considerations
- Monitoring middleware adds minimal overhead
- System metrics collected every 60 seconds
- Structured logging uses efficient JSON formatting
- Metrics exposed via single endpoint

### 5. Operational Notes
- Logs automatically rotate at 10MB with 5 backups
- All monitoring components start automatically with the application
- Health checks include component-level status reporting
- Correlation IDs enable request tracing across services

## Integration Points

### With Main Application
- Monitoring middleware integrated in `main.py`
- Background monitoring started during application lifespan
- Health endpoints available via API router

### With External Systems
- Prometheus metrics exposed for external collection
- Health endpoints suitable for load balancer checks
- Kubernetes-compatible liveness and readiness probes
- Structured logs suitable for log aggregation systems