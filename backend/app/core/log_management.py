"""
Advanced log management, rotation, and aggregation for Image2Model application.
"""

import os
import gzip
import shutil
import time
import logging
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
import psutil

logger = logging.getLogger(__name__)


class LogManager:
    """Comprehensive log management with rotation, compression, and analysis."""
    
    def __init__(self, 
                 log_directory: str = "logs",
                 max_file_size_mb: int = 50,
                 max_files_per_type: int = 10,
                 compression_enabled: bool = True,
                 cleanup_older_than_days: int = 30):
        """
        Initialize log manager.
        
        Args:
            log_directory: Directory where logs are stored
            max_file_size_mb: Maximum size of log files before rotation
            max_files_per_type: Maximum number of rotated files to keep
            compression_enabled: Whether to compress rotated logs
            cleanup_older_than_days: Age in days after which logs are cleaned up
        """
        self.log_directory = Path(log_directory)
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.max_files_per_type = max_files_per_type
        self.compression_enabled = compression_enabled
        self.cleanup_older_than_days = cleanup_older_than_days
        
        # Ensure log directory exists
        self.log_directory.mkdir(exist_ok=True)
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=2)
        
    def get_log_files(self) -> Dict[str, List[Path]]:
        """Get all log files organized by type."""
        log_files = {}
        
        for log_file in self.log_directory.glob("*.log*"):
            # Extract base name (e.g., "celery_worker" from "celery_worker.log")
            base_name = log_file.name.split('.')[0]
            
            if base_name not in log_files:
                log_files[base_name] = []
            
            log_files[base_name].append(log_file)
        
        # Sort files by modification time (newest first)
        for base_name in log_files:
            log_files[base_name].sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        return log_files
    
    def check_rotation_needed(self, log_file: Path) -> bool:
        """Check if a log file needs rotation."""
        if not log_file.exists():
            return False
        
        file_size = log_file.stat().st_size
        return file_size >= self.max_file_size_bytes
    
    def rotate_log_file(self, log_file: Path) -> bool:
        """
        Rotate a log file, optionally compressing old versions.
        
        Args:
            log_file: Path to the log file to rotate
            
        Returns:
            True if rotation was successful, False otherwise
        """
        try:
            if not log_file.exists():
                return False
            
            base_name = log_file.stem
            log_dir = log_file.parent
            
            # Find the next rotation number
            rotation_num = 1
            while True:
                rotated_name = f"{base_name}.{rotation_num}.log"
                rotated_path = log_dir / rotated_name
                
                if not rotated_path.exists():
                    break
                rotation_num += 1
            
            # Move current log to rotated name
            shutil.move(str(log_file), str(rotated_path))
            
            # Compress if enabled
            if self.compression_enabled:
                self._compress_log_file(rotated_path)
            
            # Create new empty log file
            log_file.touch()
            
            # Cleanup old rotated files
            self._cleanup_rotated_files(base_name, log_dir)
            
            logger.info(f"Rotated log file: {log_file} -> {rotated_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rotate log file {log_file}: {e}")
            return False
    
    def _compress_log_file(self, log_file: Path) -> bool:
        """Compress a log file using gzip."""
        try:
            compressed_file = log_file.with_suffix(log_file.suffix + '.gz')
            
            with open(log_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove uncompressed file
            log_file.unlink()
            
            logger.info(f"Compressed log file: {log_file} -> {compressed_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to compress log file {log_file}: {e}")
            return False
    
    def _cleanup_rotated_files(self, base_name: str, log_dir: Path):
        """Remove old rotated files beyond the retention limit."""
        pattern = f"{base_name}.*.log*"
        rotated_files = list(log_dir.glob(pattern))
        
        # Sort by modification time (oldest first)
        rotated_files.sort(key=lambda x: x.stat().st_mtime)
        
        # Remove excess files
        while len(rotated_files) > self.max_files_per_type:
            old_file = rotated_files.pop(0)
            try:
                old_file.unlink()
                logger.info(f"Removed old log file: {old_file}")
            except Exception as e:
                logger.error(f"Failed to remove old log file {old_file}: {e}")
    
    def cleanup_old_logs(self) -> Dict[str, Any]:
        """Remove logs older than the retention period."""
        cutoff_date = datetime.now() - timedelta(days=self.cleanup_older_than_days)
        cutoff_timestamp = cutoff_date.timestamp()
        
        removed_files = []
        total_size_removed = 0
        errors = []
        
        try:
            for log_file in self.log_directory.rglob("*.log*"):
                try:
                    file_mtime = log_file.stat().st_mtime
                    
                    if file_mtime < cutoff_timestamp:
                        file_size = log_file.stat().st_size
                        log_file.unlink()
                        
                        removed_files.append(str(log_file))
                        total_size_removed += file_size
                        
                except Exception as e:
                    errors.append(f"Failed to remove {log_file}: {e}")
            
            return {
                "status": "success",
                "removed_files": len(removed_files),
                "total_size_removed_bytes": total_size_removed,
                "total_size_removed_mb": round(total_size_removed / (1024 * 1024), 2),
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Error during log cleanup: {e}")
            return {
                "status": "error",
                "error": str(e),
                "removed_files": len(removed_files),
                "total_size_removed_bytes": total_size_removed
            }
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about log files."""
        log_files = self.get_log_files()
        total_files = 0
        total_size = 0
        oldest_file = None
        newest_file = None
        
        file_stats = {}
        
        for base_name, files in log_files.items():
            base_stats = {
                "file_count": len(files),
                "total_size_bytes": 0,
                "oldest_file": None,
                "newest_file": None,
                "files": []
            }
            
            for file_path in files:
                try:
                    stat = file_path.stat()
                    file_size = stat.st_size
                    file_mtime = stat.st_mtime
                    
                    file_info = {
                        "name": file_path.name,
                        "size_bytes": file_size,
                        "size_mb": round(file_size / (1024 * 1024), 2),
                        "modified_time": datetime.fromtimestamp(file_mtime).isoformat(),
                        "age_days": (time.time() - file_mtime) / (24 * 3600)
                    }
                    
                    base_stats["files"].append(file_info)
                    base_stats["total_size_bytes"] += file_size
                    
                    if base_stats["oldest_file"] is None or file_mtime < base_stats["oldest_file"]:
                        base_stats["oldest_file"] = file_mtime
                    
                    if base_stats["newest_file"] is None or file_mtime > base_stats["newest_file"]:
                        base_stats["newest_file"] = file_mtime
                    
                    total_files += 1
                    total_size += file_size
                    
                    if oldest_file is None or file_mtime < oldest_file:
                        oldest_file = file_mtime
                    
                    if newest_file is None or file_mtime > newest_file:
                        newest_file = file_mtime
                        
                except Exception as e:
                    logger.warning(f"Could not get stats for {file_path}: {e}")
            
            base_stats["total_size_mb"] = round(base_stats["total_size_bytes"] / (1024 * 1024), 2)
            file_stats[base_name] = base_stats
        
        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "oldest_file": datetime.fromtimestamp(oldest_file).isoformat() if oldest_file else None,
            "newest_file": datetime.fromtimestamp(newest_file).isoformat() if newest_file else None,
            "by_type": file_stats,
            "log_directory": str(self.log_directory),
            "disk_usage": self._get_disk_usage()
        }
    
    def _get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage statistics for the log directory."""
        try:
            usage = psutil.disk_usage(str(self.log_directory))
            return {
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "usage_percent": round((usage.used / usage.total) * 100, 2)
            }
        except Exception as e:
            logger.warning(f"Could not get disk usage: {e}")
            return {"error": str(e)}
    
    async def rotate_all_logs(self) -> Dict[str, Any]:
        """Rotate all logs that need rotation."""
        log_files = self.get_log_files()
        results = {
            "rotated_files": [],
            "skipped_files": [],
            "errors": []
        }
        
        for base_name, files in log_files.items():
            # Check the main log file (should be first after sorting)
            if files:
                main_log = files[0]
                
                # Only rotate if it's actually the main log file (no rotation number)
                if '.' not in main_log.name or main_log.name.endswith('.log'):
                    if self.check_rotation_needed(main_log):
                        # Rotate in thread pool to avoid blocking
                        loop = asyncio.get_event_loop()
                        try:
                            success = await loop.run_in_executor(
                                self.executor, self.rotate_log_file, main_log
                            )
                            
                            if success:
                                results["rotated_files"].append(str(main_log))
                            else:
                                results["errors"].append(f"Failed to rotate {main_log}")
                                
                        except Exception as e:
                            results["errors"].append(f"Error rotating {main_log}: {e}")
                    else:
                        results["skipped_files"].append(str(main_log))
        
        return results
    
    async def analyze_log_patterns(self, 
                                 log_type: str = "celery_worker", 
                                 hours_back: int = 24) -> Dict[str, Any]:
        """
        Analyze log patterns for insights and anomalies.
        
        Args:
            log_type: Type of log to analyze
            hours_back: How many hours back to analyze
            
        Returns:
            Analysis results
        """
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        log_files = self.get_log_files()
        
        if log_type not in log_files:
            return {"error": f"No log files found for type: {log_type}"}
        
        analysis = {
            "time_range": {
                "start": cutoff_time.isoformat(),
                "end": datetime.now().isoformat(),
                "hours_analyzed": hours_back
            },
            "log_levels": {"DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0},
            "error_patterns": {},
            "request_patterns": {},
            "performance_metrics": {
                "avg_response_time": 0,
                "slow_requests": [],
                "error_rate": 0
            },
            "lines_analyzed": 0
        }
        
        try:
            for log_file in log_files[log_type]:
                if not log_file.exists():
                    continue
                
                # Skip if file is too old
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_mtime < cutoff_time:
                    continue
                
                # Analyze file
                await self._analyze_log_file(log_file, analysis, cutoff_time)
            
            # Calculate derived metrics
            total_requests = sum(analysis["request_patterns"].values())
            total_errors = analysis["log_levels"]["ERROR"] + analysis["log_levels"]["CRITICAL"]
            
            if total_requests > 0:
                analysis["performance_metrics"]["error_rate"] = (total_errors / total_requests) * 100
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing log patterns: {e}")
            return {"error": str(e)}
    
    async def _analyze_log_file(self, log_file: Path, analysis: Dict, cutoff_time: datetime):
        """Analyze a single log file."""
        try:
            # Handle compressed files
            if log_file.suffix == '.gz':
                import gzip
                file_opener = gzip.open
                mode = 'rt'
            else:
                file_opener = open
                mode = 'r'
            
            response_times = []
            
            with file_opener(log_file, mode, encoding='utf-8', errors='ignore') as f:
                for line in f:
                    try:
                        analysis["lines_analyzed"] += 1
                        
                        # Try to parse as JSON (structured logs)
                        if line.strip().startswith('{'):
                            log_entry = json.loads(line.strip())
                            
                            # Check timestamp
                            if 'timestamp' in log_entry:
                                log_time = datetime.fromisoformat(log_entry['timestamp'].replace('Z', '+00:00'))
                                if log_time < cutoff_time:
                                    continue
                            
                            # Count log levels
                            level = log_entry.get('level', 'INFO')
                            if level in analysis["log_levels"]:
                                analysis["log_levels"][level] += 1
                            
                            # Analyze error patterns
                            if level in ['ERROR', 'CRITICAL']:
                                error_msg = log_entry.get('message', '')
                                if error_msg:
                                    if error_msg not in analysis["error_patterns"]:
                                        analysis["error_patterns"][error_msg] = 0
                                    analysis["error_patterns"][error_msg] += 1
                            
                            # Analyze request patterns
                            if 'method' in log_entry and 'path' in log_entry:
                                endpoint = f"{log_entry['method']} {log_entry['path']}"
                                if endpoint not in analysis["request_patterns"]:
                                    analysis["request_patterns"][endpoint] = 0
                                analysis["request_patterns"][endpoint] += 1
                                
                                # Track response times
                                if 'duration_ms' in log_entry:
                                    duration = log_entry['duration_ms']
                                    response_times.append(duration)
                                    
                                    # Flag slow requests (>5 seconds)
                                    if duration > 5000:
                                        analysis["performance_metrics"]["slow_requests"].append({
                                            "endpoint": endpoint,
                                            "duration_ms": duration,
                                            "timestamp": log_entry.get('timestamp')
                                        })
                        
                        else:
                            # Parse traditional log format
                            self._parse_traditional_log_line(line, analysis, cutoff_time)
                            
                    except (json.JSONDecodeError, ValueError):
                        # Skip malformed lines
                        continue
            
            # Calculate average response time
            if response_times:
                analysis["performance_metrics"]["avg_response_time"] = sum(response_times) / len(response_times)
                
        except Exception as e:
            logger.warning(f"Error analyzing log file {log_file}: {e}")
    
    def _parse_traditional_log_line(self, line: str, analysis: Dict, cutoff_time: datetime):
        """Parse traditional log format lines."""
        # Basic pattern matching for traditional logs
        if " ERROR " in line:
            analysis["log_levels"]["ERROR"] += 1
        elif " WARNING " in line:
            analysis["log_levels"]["WARNING"] += 1
        elif " INFO " in line:
            analysis["log_levels"]["INFO"] += 1
        elif " DEBUG " in line:
            analysis["log_levels"]["DEBUG"] += 1
        elif " CRITICAL " in line:
            analysis["log_levels"]["CRITICAL"] += 1


class LogAggregator:
    """Aggregate logs from multiple sources for centralized analysis."""
    
    def __init__(self, log_manager: LogManager):
        self.log_manager = log_manager
    
    async def create_daily_summary(self, date: datetime = None) -> Dict[str, Any]:
        """Create a daily summary of log activity."""
        if date is None:
            date = datetime.now().date()
        
        summary = {
            "date": date.isoformat(),
            "total_log_entries": 0,
            "log_levels": {"DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0},
            "top_errors": {},
            "top_endpoints": {},
            "performance_summary": {
                "avg_response_time": 0,
                "slowest_requests": [],
                "total_requests": 0
            },
            "system_events": []
        }
        
        # Analyze logs for the specific date
        analysis = await self.log_manager.analyze_log_patterns(hours_back=24)
        
        if "error" not in analysis:
            summary.update({
                "total_log_entries": analysis["lines_analyzed"],
                "log_levels": analysis["log_levels"],
                "top_errors": dict(sorted(analysis["error_patterns"].items(), 
                                        key=lambda x: x[1], reverse=True)[:10]),
                "top_endpoints": dict(sorted(analysis["request_patterns"].items(), 
                                           key=lambda x: x[1], reverse=True)[:10]),
                "performance_summary": analysis["performance_metrics"]
            })
        
        return summary
    
    async def export_logs(self, 
                         start_date: datetime, 
                         end_date: datetime, 
                         log_types: List[str] = None,
                         format: str = "json") -> str:
        """
        Export logs for a date range.
        
        Args:
            start_date: Start of export range
            end_date: End of export range
            log_types: Types of logs to export (None for all)
            format: Export format ('json', 'csv', 'txt')
            
        Returns:
            Path to exported file
        """
        export_filename = f"logs_export_{start_date.date()}_{end_date.date()}.{format}"
        export_path = self.log_manager.log_directory / "exports" / export_filename
        
        # Ensure export directory exists
        export_path.parent.mkdir(exist_ok=True)
        
        # Implementation would depend on the format
        # This is a placeholder for the actual export logic
        with open(export_path, 'w') as f:
            f.write(f"# Log export from {start_date} to {end_date}\n")
            f.write(f"# Generated on {datetime.now().isoformat()}\n")
        
        return str(export_path)


# Global log manager instance
log_manager = LogManager()
log_aggregator = LogAggregator(log_manager)