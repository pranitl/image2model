"""
Background tasks for log management and system monitoring.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import signal
import sys

from app.core.log_management import log_manager, log_aggregator

logger = logging.getLogger(__name__)


class BackgroundTaskManager:
    """Manages background tasks for log management and monitoring."""
    
    def __init__(self):
        self.tasks = {}
        self.running = False
        self.shutdown_event = asyncio.Event()
        
        # Task intervals (in seconds)
        self.intervals = {
            "log_rotation_check": 300,    # 5 minutes
            "log_cleanup": 86400,         # 24 hours
            "system_health_check": 600,   # 10 minutes
            "metrics_collection": 60      # 1 minute
        }
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.shutdown_event.set()
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    async def start_all_tasks(self):
        """Start all background tasks."""
        if self.running:
            logger.warning("Background tasks are already running")
            return
        
        self.running = True
        logger.info("Starting background task manager...")
        
        # Start individual tasks
        self.tasks["log_rotation_check"] = asyncio.create_task(
            self._periodic_task("log_rotation_check", self._check_log_rotation)
        )
        
        self.tasks["log_cleanup"] = asyncio.create_task(
            self._periodic_task("log_cleanup", self._perform_log_cleanup)
        )
        
        self.tasks["system_health_check"] = asyncio.create_task(
            self._periodic_task("system_health_check", self._check_system_health)
        )
        
        self.tasks["metrics_collection"] = asyncio.create_task(
            self._periodic_task("metrics_collection", self._collect_metrics)
        )
        
        logger.info(f"Started {len(self.tasks)} background tasks")
        
        # Wait for shutdown signal
        await self.shutdown_event.wait()
        await self.stop_all_tasks()
    
    async def stop_all_tasks(self):
        """Stop all background tasks gracefully."""
        if not self.running:
            return
        
        logger.info("Stopping background tasks...")
        self.running = False
        
        # Cancel all tasks
        for task_name, task in self.tasks.items():
            logger.info(f"Cancelling task: {task_name}")
            task.cancel()
            
            try:
                await task
            except asyncio.CancelledError:
                logger.info(f"Task {task_name} cancelled successfully")
            except Exception as e:
                logger.error(f"Error stopping task {task_name}: {e}")
        
        self.tasks.clear()
        logger.info("All background tasks stopped")
    
    async def _periodic_task(self, task_name: str, task_func):
        """Run a task periodically."""
        interval = self.intervals.get(task_name, 300)
        
        logger.info(f"Starting periodic task '{task_name}' with {interval}s interval")
        
        while self.running and not self.shutdown_event.is_set():
            try:
                await task_func()
                
                # Wait for the interval or shutdown event
                try:
                    await asyncio.wait_for(
                        self.shutdown_event.wait(),
                        timeout=interval
                    )
                    break  # Shutdown event was set
                except asyncio.TimeoutError:
                    continue  # Continue with next iteration
                    
            except asyncio.CancelledError:
                logger.info(f"Periodic task '{task_name}' was cancelled")
                break
            except Exception as e:
                logger.error(f"Error in periodic task '{task_name}': {e}")
                # Wait a bit before retrying to avoid tight error loops
                await asyncio.sleep(60)
    
    async def _check_log_rotation(self):
        """Check if any logs need rotation."""
        try:
            result = await log_manager.rotate_all_logs()
            
            if result["rotated_files"]:
                logger.info(f"Rotated {len(result['rotated_files'])} log files: {result['rotated_files']}")
            
            if result["errors"]:
                logger.warning(f"Log rotation errors: {result['errors']}")
                
        except Exception as e:
            logger.error(f"Error checking log rotation: {e}")
    
    async def _perform_log_cleanup(self):
        """Perform automated log cleanup."""
        try:
            result = log_manager.cleanup_old_logs()
            
            if result["status"] == "success" and result["removed_files"] > 0:
                logger.info(
                    f"Cleaned up {result['removed_files']} old log files, "
                    f"freed {result['total_size_removed_mb']}MB"
                )
            
            if result.get("errors"):
                logger.warning(f"Log cleanup errors: {result['errors']}")
                
        except Exception as e:
            logger.error(f"Error performing log cleanup: {e}")
    
    async def _check_system_health(self):
        """Perform system health checks."""
        try:
            stats = log_manager.get_log_statistics()
            
            # Check for potential issues
            issues = []
            
            # Check disk usage
            disk_usage = stats.get("disk_usage", {})
            if isinstance(disk_usage, dict) and "usage_percent" in disk_usage:
                usage_pct = disk_usage["usage_percent"]
                
                if usage_pct > 95:
                    issues.append(f"CRITICAL: Disk usage at {usage_pct}%")
                    # Trigger emergency cleanup
                    await self._emergency_log_cleanup()
                elif usage_pct > 85:
                    issues.append(f"WARNING: Disk usage at {usage_pct}%")
            
            # Check for large log files
            for log_type, info in stats.get("by_type", {}).items():
                size_mb = info.get("total_size_mb", 0)
                if size_mb > 500:  # 500MB threshold
                    issues.append(f"Large log files for {log_type}: {size_mb}MB")
            
            # Log issues if any
            if issues:
                logger.warning(f"System health issues detected: {'; '.join(issues)}")
            else:
                logger.debug("System health check passed")
                
        except Exception as e:
            logger.error(f"Error checking system health: {e}")
    
    async def _collect_metrics(self):
        """Collect and log system metrics."""
        try:
            stats = log_manager.get_log_statistics()
            
            # Log key metrics
            logger.info(
                "System metrics",
                extra={
                    "total_log_files": stats["total_files"],
                    "total_log_size_mb": stats["total_size_mb"],
                    "disk_usage_percent": stats.get("disk_usage", {}).get("usage_percent", 0),
                    "available_disk_gb": stats.get("disk_usage", {}).get("free_gb", 0)
                }
            )
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
    
    async def _emergency_log_cleanup(self):
        """Perform emergency log cleanup when disk space is critically low."""
        try:
            logger.warning("Performing emergency log cleanup due to low disk space")
            
            # More aggressive cleanup - remove logs older than 7 days
            original_period = log_manager.cleanup_older_than_days
            log_manager.cleanup_older_than_days = 7
            
            result = log_manager.cleanup_old_logs()
            
            # Restore original period
            log_manager.cleanup_older_than_days = original_period
            
            if result["status"] == "success":
                logger.info(
                    f"Emergency cleanup completed: removed {result['removed_files']} files, "
                    f"freed {result['total_size_removed_mb']}MB"
                )
            else:
                logger.error(f"Emergency cleanup failed: {result.get('error', 'Unknown error')}")
            
            # Force log rotation
            rotation_result = await log_manager.rotate_all_logs()
            if rotation_result["rotated_files"]:
                logger.info(f"Emergency rotation completed: {len(rotation_result['rotated_files'])} files rotated")
                
        except Exception as e:
            logger.error(f"Error performing emergency log cleanup: {e}")


class LogMonitor:
    """Monitor log patterns and alert on anomalies."""
    
    def __init__(self):
        self.baseline_metrics = {}
        self.alert_thresholds = {
            "error_rate": 10.0,        # Error rate percentage
            "response_time": 5000,     # Response time in ms
            "log_volume": 1000         # Log entries per hour
        }
    
    async def analyze_and_alert(self, hours_back: int = 1):
        """Analyze recent logs and generate alerts if needed."""
        try:
            analysis = await log_manager.analyze_log_patterns(hours_back=hours_back)
            
            if "error" in analysis:
                logger.warning(f"Log analysis failed: {analysis['error']}")
                return
            
            alerts = []
            
            # Check error rate
            total_logs = sum(analysis["log_levels"].values())
            if total_logs > 0:
                error_count = analysis["log_levels"]["ERROR"] + analysis["log_levels"]["CRITICAL"]
                error_rate = (error_count / total_logs) * 100
                
                if error_rate > self.alert_thresholds["error_rate"]:
                    alerts.append(f"High error rate: {error_rate:.1f}% ({error_count}/{total_logs})")
            
            # Check response times
            avg_response_time = analysis["performance_metrics"]["avg_response_time"]
            if avg_response_time > self.alert_thresholds["response_time"]:
                alerts.append(f"High average response time: {avg_response_time:.1f}ms")
            
            # Check for repeated errors
            error_patterns = analysis["error_patterns"]
            for error_msg, count in error_patterns.items():
                if count > 10:  # More than 10 occurrences of the same error
                    alerts.append(f"Repeated error ({count} times): {error_msg[:100]}...")
            
            # Log alerts
            if alerts:
                logger.warning(f"Log monitoring alerts: {'; '.join(alerts)}")
                
                # Here you could integrate with external alerting systems
                # e.g., send to Slack, PagerDuty, email, etc.
                await self._send_alerts(alerts, analysis)
            
        except Exception as e:
            logger.error(f"Error in log monitoring: {e}")
    
    async def _send_alerts(self, alerts: list, analysis: dict):
        """Send alerts to external systems (placeholder)."""
        # This is where you would integrate with external alerting systems
        logger.info(f"Would send {len(alerts)} alerts to external systems")
        
        # Example: could send to webhook, email, Slack, etc.
        # For now, just log the alert details
        for alert in alerts:
            logger.warning(f"ALERT: {alert}")


# Global instances
background_task_manager = BackgroundTaskManager()
log_monitor = LogMonitor()