"""
Log management and monitoring endpoints.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, status, Query, BackgroundTasks
from pydantic import BaseModel
import logging

from app.core.log_management import log_manager, log_aggregator

logger = logging.getLogger(__name__)
router = APIRouter()


class LogStatisticsResponse(BaseModel):
    """Log statistics response model."""
    total_files: int
    total_size_mb: float
    oldest_file: Optional[str]
    newest_file: Optional[str]
    by_type: Dict[str, Any]
    log_directory: str
    disk_usage: Dict[str, Any]


class LogRotationResponse(BaseModel):
    """Log rotation response model."""
    rotated_files: List[str]
    skipped_files: List[str]
    errors: List[str]


class LogAnalysisResponse(BaseModel):
    """Log analysis response model."""
    time_range: Dict[str, Any]
    log_levels: Dict[str, int]
    error_patterns: Dict[str, int]
    request_patterns: Dict[str, int]
    performance_metrics: Dict[str, Any]
    lines_analyzed: int


class LogCleanupResponse(BaseModel):
    """Log cleanup response model."""
    status: str
    removed_files: int
    total_size_removed_mb: float
    errors: List[str]


@router.get("/statistics", response_model=LogStatisticsResponse)
async def get_log_statistics():
    """
    Get comprehensive statistics about log files.
    """
    try:
        stats = log_manager.get_log_statistics()
        return LogStatisticsResponse(**stats)
    except Exception as e:
        logger.error(f"Failed to get log statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to retrieve log statistics", "message": str(e)}
        )


@router.post("/rotate", response_model=LogRotationResponse)
async def rotate_logs():
    """
    Manually trigger log rotation for all log files that need it.
    """
    try:
        result = await log_manager.rotate_all_logs()
        return LogRotationResponse(**result)
    except Exception as e:
        logger.error(f"Failed to rotate logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to rotate logs", "message": str(e)}
        )


@router.delete("/cleanup", response_model=LogCleanupResponse)
async def cleanup_old_logs(
    older_than_days: int = Query(30, ge=1, le=365, description="Remove logs older than this many days")
):
    """
    Clean up old log files beyond the retention period.
    """
    try:
        # Temporarily update cleanup period
        original_period = log_manager.cleanup_older_than_days
        log_manager.cleanup_older_than_days = older_than_days
        
        result = log_manager.cleanup_old_logs()
        
        # Restore original period
        log_manager.cleanup_older_than_days = original_period
        
        return LogCleanupResponse(**result)
    except Exception as e:
        logger.error(f"Failed to cleanup logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to cleanup logs", "message": str(e)}
        )


@router.get("/analyze", response_model=LogAnalysisResponse)
async def analyze_log_patterns(
    log_type: str = Query("celery_worker", description="Type of log to analyze"),
    hours_back: int = Query(24, ge=1, le=168, description="Hours back to analyze")
):
    """
    Analyze log patterns for insights and anomalies.
    """
    try:
        result = await log_manager.analyze_log_patterns(log_type, hours_back)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": result["error"]}
            )
        
        return LogAnalysisResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze log patterns: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to analyze log patterns", "message": str(e)}
        )


@router.get("/summary/daily")
async def get_daily_summary(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format (default: today)")
):
    """
    Get daily log summary for analysis.
    """
    try:
        if date:
            target_date = datetime.fromisoformat(date)
        else:
            target_date = datetime.now()
        
        summary = await log_aggregator.create_daily_summary(target_date)
        return summary
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Invalid date format. Use YYYY-MM-DD format."}
        )
    except Exception as e:
        logger.error(f"Failed to get daily summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to get daily summary", "message": str(e)}
        )


@router.get("/types")
async def get_log_types():
    """
    Get available log types for analysis.
    """
    try:
        log_files = log_manager.get_log_files()
        return {
            "log_types": list(log_files.keys()),
            "total_types": len(log_files),
            "details": {
                log_type: {
                    "file_count": len(files),
                    "latest_file": str(files[0]) if files else None
                }
                for log_type, files in log_files.items()
            }
        }
    except Exception as e:
        logger.error(f"Failed to get log types: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to get log types", "message": str(e)}
        )


@router.post("/export")
async def export_logs(
    background_tasks: BackgroundTasks,
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    log_types: Optional[str] = Query(None, description="Comma-separated log types"),
    format: str = Query("json", regex="^(json|csv|txt)$", description="Export format")
):
    """
    Export logs for a date range (background task).
    """
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        if start_dt > end_dt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Start date must be before end date"}
            )
        
        # Parse log types
        log_type_list = None
        if log_types:
            log_type_list = [t.strip() for t in log_types.split(",")]
        
        # Start background export task
        background_tasks.add_task(
            _background_export_logs,
            start_dt, end_dt, log_type_list, format
        )
        
        return {
            "status": "export_started",
            "message": "Log export started in background",
            "parameters": {
                "start_date": start_date,
                "end_date": end_date,
                "log_types": log_type_list,
                "format": format
            }
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Invalid date format. Use YYYY-MM-DD format."}
        )
    except Exception as e:
        logger.error(f"Failed to start log export: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to start log export", "message": str(e)}
        )


@router.get("/health")
async def log_system_health():
    """
    Check the health of the logging system.
    """
    try:
        stats = log_manager.get_log_statistics()
        
        # Check for potential issues
        issues = []
        warnings = []
        
        # Check disk usage
        disk_usage = stats.get("disk_usage", {})
        if isinstance(disk_usage, dict) and "usage_percent" in disk_usage:
            if disk_usage["usage_percent"] > 95:
                issues.append("Critical: Disk usage over 95%")
            elif disk_usage["usage_percent"] > 85:
                warnings.append("Warning: Disk usage over 85%")
        
        # Check log file sizes
        for log_type, info in stats.get("by_type", {}).items():
            if info.get("total_size_mb", 0) > 500:  # 500MB threshold
                warnings.append(f"Large log files for {log_type}: {info['total_size_mb']}MB")
        
        # Check for old logs
        if stats.get("oldest_file"):
            oldest_date = datetime.fromisoformat(stats["oldest_file"])
            age_days = (datetime.now() - oldest_date).days
            if age_days > 60:  # 60 days threshold
                warnings.append(f"Old logs detected: {age_days} days old")
        
        # Determine overall health
        if issues:
            health_status = "critical"
        elif warnings:
            health_status = "warning"
        else:
            health_status = "healthy"
        
        return {
            "status": health_status,
            "timestamp": datetime.now().isoformat(),
            "statistics": stats,
            "issues": issues,
            "warnings": warnings,
            "recommendations": _get_health_recommendations(issues, warnings)
        }
        
    except Exception as e:
        logger.error(f"Failed to check log system health: {e}")
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


async def _background_export_logs(
    start_date: datetime,
    end_date: datetime,
    log_types: Optional[List[str]],
    format: str
):
    """Background task for log export."""
    try:
        export_path = await log_aggregator.export_logs(
            start_date, end_date, log_types, format
        )
        logger.info(f"Log export completed: {export_path}")
    except Exception as e:
        logger.error(f"Log export failed: {e}")


def _get_health_recommendations(issues: List[str], warnings: List[str]) -> List[str]:
    """Get recommendations based on health issues."""
    recommendations = []
    
    if any("disk usage" in issue.lower() for issue in issues + warnings):
        recommendations.append("Consider rotating logs more frequently or reducing retention period")
        recommendations.append("Clean up old logs using the cleanup endpoint")
    
    if any("large log files" in warning.lower() for warning in warnings):
        recommendations.append("Trigger manual log rotation")
        recommendations.append("Consider reducing log verbosity")
    
    if any("old logs" in warning.lower() for warning in warnings):
        recommendations.append("Run log cleanup to remove old files")
        recommendations.append("Review log retention policy")
    
    if not recommendations:
        recommendations.append("Log system is healthy - no actions needed")
    
    return recommendations