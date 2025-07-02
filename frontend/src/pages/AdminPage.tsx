import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  HardDrive,
  Trash2,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Clock,
  Folder,
  File
} from 'lucide-react';

interface DiskUsageInfo {
  path: string;
  size_mb: number;
  file_count: number;
  directory_count: number;
  disk_total_gb: number;
  disk_used_gb: number;
  disk_free_gb: number;
  disk_usage_percent: number;
}

interface DiskUsage {
  upload_dir: DiskUsageInfo;
  output_dir: DiskUsageInfo;
  timestamp: string;
}

interface FileInfo {
  path: string;
  size_mb: number;
  modified: string;
  is_directory: boolean;
  file_count?: number;
}

interface DirectoryListing {
  directory: string;
  total_size_mb: number;
  total_files: number;
  items: FileInfo[];
}

interface SystemHealth {
  status: 'healthy' | 'warning' | 'critical';
  disk_usage: DiskUsage;
  warnings: string[];
  timestamp: string;
}

interface CleanupResult {
  freed_space_mb: number;
  files_removed: number;
  directories_removed: number;
  errors: string[];
  cleanup_hours: number;
  timestamp: string;
}

const AdminPage: React.FC = () => {
  const [diskUsage, setDiskUsage] = useState<DiskUsage | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [uploadFiles, setUploadFiles] = useState<DirectoryListing | null>(null);
  const [resultFiles, setResultFiles] = useState<DirectoryListing | null>(null);
  const [loading, setLoading] = useState(false);
  const [cleanupLoading, setCleanupLoading] = useState(false);
  const [lastCleanup, setLastCleanup] = useState<CleanupResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchDiskUsage = async () => {
    try {
      const response = await fetch('/api/v1/admin/disk-usage');
      if (!response.ok) throw new Error('Failed to fetch disk usage');
      const data = await response.json();
      setDiskUsage(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch disk usage');
    }
  };

  const fetchSystemHealth = async () => {
    try {
      const response = await fetch('/api/v1/admin/system-health');
      if (!response.ok) throw new Error('Failed to fetch system health');
      const data = await response.json();
      setSystemHealth(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch system health');
    }
  };

  const fetchDirectoryListing = async (directory: 'uploads' | 'results') => {
    try {
      const response = await fetch(`/api/v1/admin/list-files?directory=${directory}&limit=50`);
      if (!response.ok) throw new Error(`Failed to fetch ${directory} listing`);
      const data = await response.json();
      
      if (directory === 'uploads') {
        setUploadFiles(data);
      } else {
        setResultFiles(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : `Failed to fetch ${directory} listing`);
    }
  };

  const triggerCleanup = async (hours: number = 24) => {
    setCleanupLoading(true);
    try {
      const response = await fetch('/api/v1/admin/cleanup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hours, dry_run: false })
      });
      
      if (!response.ok) throw new Error('Failed to trigger cleanup');
      const result = await response.json();
      setLastCleanup(result);
      
      // Refresh data after cleanup
      await fetchAllData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to trigger cleanup');
    } finally {
      setCleanupLoading(false);
    }
  };

  const deleteJobFiles = async (jobId: string) => {
    try {
      const response = await fetch(`/api/v1/admin/delete-job/${jobId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) throw new Error('Failed to delete job files');
      
      // Refresh listings after deletion
      await fetchDirectoryListing('uploads');
      await fetchDirectoryListing('results');
      await fetchDiskUsage();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete job files');
    }
  };

  const fetchAllData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      await Promise.all([
        fetchDiskUsage(),
        fetchSystemHealth(),
        fetchDirectoryListing('uploads'),
        fetchDirectoryListing('results')
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchAllData, 30000);
    return () => clearInterval(interval);
  }, []);

  const formatBytes = (bytes: number): string => {
    if (bytes < 1024) return `${bytes.toFixed(2)} MB`;
    return `${(bytes / 1024).toFixed(2)} GB`;
  };

  const formatDate = (timestamp: string): string => {
    return new Date(parseFloat(timestamp) * 1000).toLocaleString();
  };

  const getHealthBadgeVariant = (status: string) => {
    switch (status) {
      case 'healthy': return 'success';
      case 'warning': return 'warning';
      case 'critical': return 'destructive';
      default: return 'secondary';
    }
  };

  if (loading && !diskUsage) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="h-8 w-8 animate-spin" />
          <span className="ml-2">Loading admin dashboard...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">System Administration</h1>
        <Button 
          onClick={fetchAllData} 
          disabled={loading}
          variant="outline"
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* System Health Overview */}
      {systemHealth && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <HardDrive className="h-5 w-5" />
              System Health
              <Badge variant={getHealthBadgeVariant(systemHealth.status)}>
                {systemHealth.status}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {systemHealth.warnings.length > 0 && (
              <div className="space-y-2 mb-4">
                {systemHealth.warnings.map((warning, index) => (
                  <Alert key={index} variant="warning">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>{warning}</AlertDescription>
                  </Alert>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Disk Usage Cards */}
      {diskUsage && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Object.entries(diskUsage).map(([key, info]) => {
            if (key === 'timestamp' || !info.disk_total_gb) return null;
            
            return (
              <Card key={key}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Folder className="h-5 w-5" />
                    {key.replace('_dir', '').toUpperCase()} Directory
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Directory Size</p>
                      <p className="text-lg font-semibold">{formatBytes(info.size_mb)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">File Count</p>
                      <p className="text-lg font-semibold">{info.file_count}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Disk Usage</p>
                      <p className="text-lg font-semibold">{info.disk_usage_percent.toFixed(1)}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Free Space</p>
                      <p className="text-lg font-semibold">{formatBytes(info.disk_free_gb * 1024)}</p>
                    </div>
                  </div>
                  
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div 
                      className={`h-2.5 rounded-full ${
                        info.disk_usage_percent > 90 ? 'bg-red-600' :
                        info.disk_usage_percent > 80 ? 'bg-yellow-600' : 'bg-green-600'
                      }`}
                      style={{ width: `${Math.min(info.disk_usage_percent, 100)}%` }}
                    ></div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Cleanup Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trash2 className="h-5 w-5" />
            File Cleanup
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Button 
              onClick={() => triggerCleanup(24)}
              disabled={cleanupLoading}
              variant="outline"
            >
              {cleanupLoading ? (
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Trash2 className="h-4 w-4 mr-2" />
              )}
              Clean Files (24h)
            </Button>
            <Button 
              onClick={() => triggerCleanup(1)}
              disabled={cleanupLoading}
              variant="outline"
            >
              Clean Files (1h)
            </Button>
          </div>
          
          {lastCleanup && (
            <Alert>
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>
                Last cleanup: Freed {lastCleanup.freed_space_mb.toFixed(2)} MB, 
                removed {lastCleanup.files_removed} files and {lastCleanup.directories_removed} directories
                {lastCleanup.errors.length > 0 && ` (${lastCleanup.errors.length} errors)`}
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* File Listings */}
      <Card>
        <CardHeader>
          <CardTitle>File Management</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="uploads">
            <TabsList>
              <TabsTrigger value="uploads">Upload Files</TabsTrigger>
              <TabsTrigger value="results">Result Files</TabsTrigger>
            </TabsList>
            
            <TabsContent value="uploads" className="space-y-4">
              {uploadFiles && (
                <>
                  <div className="flex justify-between items-center">
                    <p className="text-sm text-gray-600">
                      {uploadFiles.total_files} files, {formatBytes(uploadFiles.total_size_mb)} total
                    </p>
                  </div>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {uploadFiles.items.map((item, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded">
                        <div className="flex items-center gap-3">
                          {item.is_directory ? <Folder className="h-4 w-4" /> : <File className="h-4 w-4" />}
                          <div>
                            <p className="font-medium">{item.path}</p>
                            <p className="text-sm text-gray-600">
                              {formatBytes(item.size_mb)} • {formatDate(item.modified)}
                              {item.file_count !== undefined && ` • ${item.file_count} files`}
                            </p>
                          </div>
                        </div>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => deleteJobFiles(item.path)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </TabsContent>
            
            <TabsContent value="results" className="space-y-4">
              {resultFiles && (
                <>
                  <div className="flex justify-between items-center">
                    <p className="text-sm text-gray-600">
                      {resultFiles.total_files} files, {formatBytes(resultFiles.total_size_mb)} total
                    </p>
                  </div>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {resultFiles.items.map((item, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded">
                        <div className="flex items-center gap-3">
                          {item.is_directory ? <Folder className="h-4 w-4" /> : <File className="h-4 w-4" />}
                          <div>
                            <p className="font-medium">{item.path}</p>
                            <p className="text-sm text-gray-600">
                              {formatBytes(item.size_mb)} • {formatDate(item.modified)}
                              {item.file_count !== undefined && ` • ${item.file_count} files`}
                            </p>
                          </div>
                        </div>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => deleteJobFiles(item.path)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminPage;