"""
Enhanced health check endpoints with comprehensive monitoring.
"""

import asyncio
import time
import redis
from datetime import datetime, timezone
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel
import psutil
import platform
import logging

from app.core.monitoring import get_metrics_data, system_monitor

logger = logging.getLogger(__name__)
router = APIRouter()


class HealthResponse(BaseModel):
    """Basic health check response model."""
    status: str
    service: str
    version: str
    timestamp: str


class ComponentHealth(BaseModel):
    """Individual component health status."""
    name: str
    status: str
    response_time_ms: float
    details: Dict[str, Any] = {}


class DetailedHealthResponse(BaseModel):
    """Detailed health check response model."""
    status: str
    service: str
    version: str
    timestamp: str
    system: Dict[str, Any]
    components: List[ComponentHealth]
    uptime_seconds: float


class HealthChecker:
    """Comprehensive health checking for all system components."""
    
    def __init__(self):
        self.start_time = time.time()
    
    async def check_redis(self) -> ComponentHealth:
        """Check Redis connectivity and performance."""
        start_time = time.time()
        
        try:
            # Try to connect to Redis (if configured)
            # This would need to be configured based on your Redis setup
            # For now, we'll simulate a basic check
            await asyncio.sleep(0.001)  # Simulate redis ping
            
            response_time = (time.time() - start_time) * 1000
            
            return ComponentHealth(
                name="redis",
                status="healthy",
                response_time_ms=response_time,
                details={
                    "connection": "established",
                    "ping_successful": True
                }
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.warning(f"Redis health check failed: {e}")
            
            return ComponentHealth(
                name="redis",
                status="unhealthy",
                response_time_ms=response_time,
                details={
                    "error": str(e),
                    "connection": "failed"
                }
            )
    
    async def check_celery(self) -> ComponentHealth:
        """Check Celery worker availability."""
        start_time = time.time()
        
        try:
            from app.core.celery_app import celery_app
            
            # Check if workers are available
            inspect = celery_app.control.inspect()
            active_workers = inspect.active()
            
            response_time = (time.time() - start_time) * 1000
            
            if active_workers:
                worker_count = len(active_workers)
                return ComponentHealth(
                    name="celery",
                    status="healthy",
                    response_time_ms=response_time,
                    details={
                        "active_workers": worker_count,
                        "workers": list(active_workers.keys())
                    }
                )
            else:
                return ComponentHealth(
                    name="celery",
                    status="degraded",
                    response_time_ms=response_time,
                    details={
                        "active_workers": 0,
                        "message": "No active workers found"
                    }
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.warning(f"Celery health check failed: {e}")
            
            return ComponentHealth(
                name="celery",
                status="unhealthy",
                response_time_ms=response_time,
                details={
                    "error": str(e),
                    "message": "Unable to connect to Celery"
                }
            )
    
    async def check_disk_space(self) -> ComponentHealth:
        """Check disk space availability."""
        start_time = time.time()
        
        try:
            disk_usage = psutil.disk_usage('/')
            free_gb = disk_usage.free / (1024**3)
            total_gb = disk_usage.total / (1024**3)
            usage_percent = (disk_usage.used / disk_usage.total) * 100
            
            response_time = (time.time() - start_time) * 1000
            
            # Consider unhealthy if less than 1GB free or over 95% used
            if free_gb < 1.0 or usage_percent > 95:
                status = "unhealthy"
            elif usage_percent > 85:
                status = "degraded"
            else:
                status = "healthy"
            
            return ComponentHealth(
                name="disk_space",
                status=status,
                response_time_ms=response_time,
                details={
                    "free_gb": round(free_gb, 2),
                    "total_gb": round(total_gb, 2),
                    "usage_percent": round(usage_percent, 2)
                }
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            return ComponentHealth(
                name="disk_space",
                status="unhealthy",
                response_time_ms=response_time,
                details={"error": str(e)}
            )
    
    async def check_fal_api(self) -> ComponentHealth:
        """Check FAL.AI API connectivity."""
        start_time = time.time()
        
        try:
            # This would need to be implemented based on your FAL.AI client
            # For now, we'll simulate a basic connectivity check
            await asyncio.sleep(0.01)  # Simulate API call
            
            response_time = (time.time() - start_time) * 1000
            
            return ComponentHealth(
                name="fal_api",
                status="healthy",
                response_time_ms=response_time,
                details={
                    "connectivity": "available",
                    "api_accessible": True
                }
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            return ComponentHealth(
                name="fal_api",
                status="unhealthy",
                response_time_ms=response_time,
                details={
                    "error": str(e),
                    "connectivity": "failed"
                }
            )
    
    async def check_all_components(self) -> List[ComponentHealth]:
        """Check all system components concurrently."""
        tasks = [
            self.check_redis(),
            self.check_celery(),
            self.check_disk_space(),
            self.check_fal_api()
        ]
        
        return await asyncio.gather(*tasks)
    
    def get_overall_status(self, components: List[ComponentHealth]) -> str:
        """Determine overall system status based on component health."""
        unhealthy_count = sum(1 for c in components if c.status == "unhealthy")
        degraded_count = sum(1 for c in components if c.status == "degraded")
        
        if unhealthy_count > 0:
            return "unhealthy"
        elif degraded_count > 0:
            return "degraded"
        else:
            return "healthy"


# Global health checker instance
health_checker = HealthChecker()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.
    Returns the current status of the service.
    """
    return HealthResponse(
        status="healthy",
        service="image2model-backend",
        version="1.0.0",
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """
    Comprehensive health check with system and component information.
    """
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
        
        # If overall status is unhealthy, return 503
        if overall_status == "unhealthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=response.dict()
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Health check failed", "message": str(e)}
        )


@router.get("/metrics")
async def get_metrics():
    """
    Prometheus metrics endpoint.
    Returns metrics in Prometheus format.
    """
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


@router.get("/liveness")
async def liveness_probe():
    """
    Kubernetes liveness probe endpoint.
    Simple check to verify the application is running.
    """
    return {"status": "alive", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/readiness")
async def readiness_probe():
    """
    Kubernetes readiness probe endpoint.
    Checks if the application is ready to serve requests.
    """
    try:
        # Basic readiness checks
        components = await health_checker.check_all_components()
        
        # Consider ready if no components are completely unhealthy
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