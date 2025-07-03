import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  Wifi, 
  WifiOff, 
  RotateCcw,
  Activity,
  Timer,
  FileText,
  Download,
  Image,
  FileX
} from 'lucide-react'
import { useTaskStream, TaskStatus } from '@/hooks'
// import ModelViewer from './ModelViewer' // Removed - using image preview instead

// File status interface for individual file tracking
interface FileStatus {
  filename: string
  status: 'queued' | 'processing' | 'completed' | 'failed'
  thumbnail?: string
  downloadUrl?: string
  error?: string
  progress?: number
}

const ProcessingPage: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>()
  const [processingStartTime] = useState(Date.now())
  const [files, setFiles] = useState<FileStatus[]>([])
  const [jobResults, setJobResults] = useState<any>(null)
  
  const {
    status,
    isConnected,
    isConnecting,
    error,
    connectionAttempts,
    lastStatus,
    reconnect
  } = useTaskStream(taskId || null, {
    timeout: 3600, // 1 hour
    autoReconnect: true,
    maxReconnectAttempts: 5,
    reconnectInterval: 2000
  })

  const getStatusIcon = (taskStatus: TaskStatus | null) => {
    if (!taskStatus) return <Clock className="h-6 w-6 text-gray-500 animate-pulse" />
    
    switch (taskStatus.status) {
      case 'completed':
        return <CheckCircle className="h-6 w-6 text-green-500" />
      case 'processing':
        return <Activity className="h-6 w-6 text-blue-500 animate-pulse" />
      case 'failed':
      case 'error':
        return <AlertCircle className="h-6 w-6 text-red-500" />
      case 'retrying':
        return <RotateCcw className="h-6 w-6 text-yellow-500 animate-spin" />
      case 'cancelled':
        return <AlertCircle className="h-6 w-6 text-gray-500" />
      default:
        return <Clock className="h-6 w-6 text-gray-500" />
    }
  }

  const getStatusText = (taskStatus: TaskStatus | null) => {
    if (!taskStatus) return 'Connecting...'
    
    switch (taskStatus.status) {
      case 'completed':
        return 'Completed'
      case 'processing':
        return 'Processing'
      case 'failed':
        return 'Failed'
      case 'error':
        return 'Error'
      case 'retrying':
        return 'Retrying'
      case 'cancelled':
        return 'Cancelled'
      case 'queued':
        return 'Queued'
      default:
        return 'Unknown'
    }
  }

  const getStatusColor = (taskStatus: TaskStatus | null) => {
    if (!taskStatus) return 'text-gray-500'
    
    switch (taskStatus.status) {
      case 'completed':
        return 'text-green-600'
      case 'processing':
        return 'text-blue-600'
      case 'failed':
      case 'error':
        return 'text-red-600'
      case 'retrying':
        return 'text-yellow-600'
      case 'cancelled':
        return 'text-gray-600'
      default:
        return 'text-gray-600'
    }
  }

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    
    if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`
    }
    return `${remainingSeconds}s`
  }

  const formatETA = (etaSeconds: number) => {
    if (etaSeconds < 60) {
      return `${Math.round(etaSeconds)}s remaining`
    } else if (etaSeconds < 3600) {
      const minutes = Math.round(etaSeconds / 60)
      return `${minutes}m remaining`
    } else {
      const hours = Math.round(etaSeconds / 3600)
      return `${hours}h remaining`
    }
  }

  if (!taskId) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="container mx-auto px-4 max-w-4xl text-center">
          <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Invalid Task</h1>
          <p className="text-gray-600 mb-8">No task ID provided.</p>
          <Link to="/upload" className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors">
            Upload New Images
          </Link>
        </div>
      </div>
    )
  }

  const isCompleted = status?.status === 'completed'
  const isFailed = status?.status === 'failed' || status?.status === 'error'
  const isProcessing = status?.status === 'processing'

  // Update file statuses when job results are available
  useEffect(() => {
    if (status?.status === 'completed' && status.result && !jobResults) {
      setJobResults(status.result)
      
      // Extract file results and update file status
      if (status.result.results && Array.isArray(status.result.results)) {
        console.log('Processing results:', status.result.results)
        const updatedFiles = status.result.results.map((result: any, index: number) => {
          const file = {
            filename: result.filename || (result.file_path ? result.file_path.split('/').pop() : `file_${index + 1}`),
            status: (result.status === 'success' || result.status === 'completed') ? 'completed' as const : 'failed' as const,
            downloadUrl: result.download_url || result.model_url || undefined,  // Use direct FAL.AI URL
            error: result.error || undefined,
            thumbnail: result.rendered_image?.url || undefined
          }
          console.log('Processed file:', file)
          console.log('Rendered image URL:', result.rendered_image?.url)
          return file
        })
        setFiles(updatedFiles)
        
        // Save job data to localStorage for ResultsPage
        if (status.result.job_id || status.job_id) {
          const jobId = status.result.job_id || status.job_id
          const jobData = {
            taskId: taskId,
            fileId: status.result.file_id || status.file_id,
            filename: status.result.filename || status.filename || updatedFiles[0]?.filename || 'uploaded_image.jpg',
            uploadPath: status.result.input_image || status.inputImage || '/api/placeholder/300/300'
          }
          localStorage.setItem(`job_${jobId}`, JSON.stringify(jobData))
          console.log('Saved job data to localStorage:', jobData)
        }
      }
    }
  }, [status, taskId, jobResults])

  // Initialize files from job metadata if available  
  useEffect(() => {
    if (status?.total && files.length === 0) {
      // Try to get actual filenames from status message or use generic names
      const getFilename = (index: number) => {
        if (status?.message && status.message.includes('Processing')) {
          const match = status.message.match(/Processing (.+)/)
          if (match) return match[1]
        }
        return `file_${index + 1}.jpg`
      }

      const initialFiles = Array.from({ length: status.total }, (_, index) => ({
        filename: getFilename(index),
        status: 'queued' as const,
        progress: 0
      }))
      setFiles(initialFiles)
    }
  }, [status?.total, files.length, status?.message])

  // Update file progress during processing
  useEffect(() => {
    if (status?.status === 'processing' && status.current !== undefined && files.length > 0) {
      setFiles(prevFiles => 
        prevFiles.map((file, index) => {
          if (index < (status.current || 0)) {
            return { ...file, status: 'completed' as const, progress: 100 }
          } else if (index === status.current) {
            // Update filename if we have more info from status message
            const currentFilename = status.message && status.message.includes('Processing') 
              ? status.message.match(/Processing (.+)/)?.[1] || file.filename
              : file.filename
            
            return { 
              ...file, 
              filename: currentFilename,
              status: 'processing' as const, 
              progress: Math.floor((status.progress || 0) / (status.total || 1)) // Individual file progress estimate
            }
          } else {
            return { ...file, status: 'queued' as const, progress: 0 }
          }
        })
      )
    }
  }, [status?.status, status?.current, status?.progress, status?.total, status?.message, files.length])

  // Update overall file status based on main status changes
  useEffect(() => {
    if (status?.status === 'queued' && files.length > 0) {
      setFiles(prevFiles => 
        prevFiles.map(file => ({ ...file, status: 'queued' as const, progress: 0 }))
      )
    }
  }, [status?.status, files.length])

  // Handle task failures and errors with file-level error reporting
  useEffect(() => {
    if ((status?.status === 'failed' || status?.status === 'error') && files.length > 0) {
      setFiles(prevFiles => 
        prevFiles.map((file, index) => {
          // If we have specific error info for individual files, use it
          const fileError = status?.error || 'Processing failed'
          
          // Mark files that were being processed as failed
          if (file.status === 'processing' || (status.current !== undefined && index === status.current)) {
            return { ...file, status: 'failed' as const, error: fileError, progress: 0 }
          }
          // Keep completed files as completed, mark others as failed
          else if (file.status !== 'completed') {
            return { ...file, status: 'failed' as const, error: 'Job cancelled due to error', progress: 0 }
          }
          return file
        })
      )
    }
  }, [status?.status, status?.error, status?.current, files.length])

  // Handle retry scenarios
  useEffect(() => {
    if (status?.status === 'retrying' && files.length > 0) {
      setFiles(prevFiles => 
        prevFiles.map((file, index) => {
          if (file.status === 'failed' || (status.current !== undefined && index >= status.current)) {
            return { ...file, status: 'queued' as const, error: undefined, progress: 0 }
          }
          return file
        })
      )
    }
  }, [status?.status, status?.current, files.length])

  // Download file helper function - now supports direct FAL.AI URLs
  const downloadFile = async (downloadUrl: string, filename: string) => {
    try {
      console.log('Attempting download:', { downloadUrl, filename })
      
      // For FAL.AI URLs, open in new tab (browser will handle the download)
      if (downloadUrl.includes('fal.ai') || downloadUrl.includes('fal.run')) {
        // Create a temporary link and trigger download
        const link = document.createElement('a')
        link.href = downloadUrl
        link.download = filename.replace(/\.[^/.]+$/, '.glb') // Ensure .glb extension
        link.target = '_blank'  // Open in new tab as fallback
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        return
      }
      
      // For local URLs, use the fetch approach
      const absoluteUrl = downloadUrl.startsWith('http') ? downloadUrl : `${window.location.origin}${downloadUrl}`
      console.log('Absolute URL:', absoluteUrl)
      
      const response = await fetch(absoluteUrl, {
        method: 'GET',
        credentials: 'same-origin'
      })
      
      console.log('Download response:', response.status, response.statusText)
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('Download error response:', errorText)
        throw new Error(`Download failed: ${response.status} ${response.statusText}`)
      }
      
      const blob = await response.blob()
      console.log('Blob size:', blob.size, 'type:', blob.type)
      
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename.replace(/\.[^/.]+$/, '.glb') // Ensure .glb extension
      document.body.appendChild(link)
      link.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(link)
    } catch (error) {
      console.error('Download failed:', error)
      alert('Failed to download file. Please try again.')
    }
  }

  // Retry failed job function
  const retryJob = async () => {
    try {
      // This would need to be implemented on the backend to retry a failed job
      const response = await fetch(`/api/retry/${taskId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      
      if (!response.ok) throw new Error('Retry failed')
      
      // Reset file states to queued for retry
      setFiles(prevFiles => 
        prevFiles.map(file => ({ 
          ...file, 
          status: 'queued' as const, 
          error: undefined, 
          progress: 0 
        }))
      )
      
      // The SSE connection should automatically start receiving new updates
    } catch (error) {
      console.error('Retry failed:', error)
      alert('Failed to retry job. Please refresh the page and try again.')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold text-gray-900">
              Task Processing
            </h1>
            <div className="flex items-center gap-3">
              {/* Connection Status */}
              <div className="flex items-center gap-2">
                {isConnected ? (
                  <Wifi className="h-4 w-4 text-green-500" />
                ) : (
                  <WifiOff className="h-4 w-4 text-red-500" />
                )}
                <span className="text-sm text-gray-600">
                  {isConnecting ? 'Connecting...' : isConnected ? 'Live' : 'Disconnected'}
                </span>
              </div>
              
              {/* Task Status */}
              <div className="flex items-center gap-2">
                {getStatusIcon(status)}
                <span className={`font-medium ${getStatusColor(status)}`}>
                  {getStatusText(status)}
                </span>
              </div>
            </div>
          </div>
          
          <div className="grid md:grid-cols-3 gap-4 text-sm text-gray-600">
            <div>
              <span className="font-medium">Task ID:</span> {taskId}
            </div>
            <div>
              <span className="font-medium">Started:</span> {new Date(processingStartTime).toLocaleString()}
            </div>
            {status?.task_name && (
              <div>
                <span className="font-medium">Task Type:</span> {status.task_name}
              </div>
            )}
          </div>

          {/* Progress Bar */}
          {status && (isProcessing || status.status === 'queued') && (
            <div className="mt-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Progress</span>
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  {status.current !== undefined && status.total !== undefined && (
                    <span>{status.current}/{status.total} files</span>
                  )}
                  <span>{status.progress}%</span>
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="bg-blue-600 h-3 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${status.progress}%` }}
                />
              </div>
              
              {/* ETA and additional info */}
              <div className="flex items-center justify-between mt-2 text-sm text-gray-600">
                <span>{status.message}</span>
                {status.eta_seconds && status.eta_seconds > 0 && (
                  <span className="flex items-center gap-1">
                    <Timer className="h-3 w-3" />
                    {formatETA(status.eta_seconds)}
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Batch Information */}
          {status?.batch_id && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center gap-2 text-sm text-blue-800">
                <FileText className="h-4 w-4" />
                <span className="font-medium">Batch ID:</span> {status.batch_id}
                {status.job_id && (
                  <>
                    <span className="mx-2">•</span>
                    <span className="font-medium">Job ID:</span> {status.job_id}
                  </>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Connection Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-start">
              <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div className="ml-3 flex-1">
                <h3 className="text-sm font-medium text-red-800">Connection Error</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
                {connectionAttempts > 0 && (
                  <p className="text-sm text-red-600 mt-1">
                    Reconnection attempts: {connectionAttempts}
                  </p>
                )}
                <button
                  onClick={reconnect}
                  className="mt-3 bg-red-100 px-3 py-1 rounded-md text-sm font-medium text-red-800 hover:bg-red-200 transition-colors"
                >
                  Retry Connection
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Task Error */}
        {status?.error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-start">
              <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Task Error</h3>
                <p className="text-sm text-red-700 mt-1">{status.error}</p>
                {status.error_type && (
                  <p className="text-sm text-red-600 mt-1">Type: {status.error_type}</p>
                )}
                {status.recoverable && (
                  <p className="text-sm text-yellow-700 mt-1">
                    This error may be recoverable. The system will attempt to retry.
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Completion Summary */}
        {isCompleted && status?.summary && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
            <div className="flex items-center gap-3 mb-4">
              <CheckCircle className="h-6 w-6 text-green-500" />
              <h2 className="text-lg font-semibold text-green-900">Processing Complete!</h2>
            </div>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {status.summary.total_files}
                </div>
                <div className="text-green-700">Total Files</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {status.summary.successful_files}
                </div>
                <div className="text-green-700">Successful</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {status.summary.failed_files}
                </div>
                <div className="text-red-700">Failed</div>
              </div>
            </div>
          </div>
        )}

        {/* Rendered Images Preview - Show completed 3D renders prominently */}
        {files.some(f => f.status === 'completed' && f.thumbnail) && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              Generated 3D Models
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {files.filter(f => f.status === 'completed' && f.thumbnail).map((file, index) => (
                <div key={index} className="space-y-3">
                  <div className="aspect-square rounded-lg overflow-hidden bg-gray-100 shadow-md">
                    <img
                      src={file.thumbnail}
                      alt={`3D render of ${file.filename}`}
                      className="w-full h-full object-cover hover:scale-105 transition-transform duration-200"
                      loading="lazy"
                    />
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-medium text-gray-900 truncate">{file.filename}</p>
                    {file.downloadUrl && (
                      <button
                        onClick={() => downloadFile(file.downloadUrl!, file.filename)}
                        className="mt-2 inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
                      >
                        <Download className="h-4 w-4" />
                        Download GLB
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
            
            {/* Bulk download option for generated models */}
            {files.filter(f => f.status === 'completed' && f.downloadUrl).length > 1 && (
              <div className="mt-6 pt-4 border-t border-gray-200 text-center">
                <button
                  onClick={() => {
                    const completedFiles = files.filter(f => f.status === 'completed' && f.downloadUrl)
                    completedFiles.forEach(file => {
                      if (file.downloadUrl) {
                        downloadFile(file.downloadUrl, file.filename)
                      }
                    })
                  }}
                  className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors"
                >
                  <Download className="h-4 w-4" />
                  Download All Models ({files.filter(f => f.status === 'completed').length})
                </button>
              </div>
            )}
          </div>
        )}

        {/* File Status Grid - Only show when processing or if there are failures */}
        {files.length > 0 && (isProcessing || files.some(f => f.status === 'failed' || f.status === 'processing' || f.status === 'queued')) && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Image className="h-5 w-5" />
              File Processing Status ({files.length} files)
            </h2>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {files.map((file, index) => (
                <div
                  key={index}
                  className={`border rounded-lg p-4 transition-all duration-200 ${
                    file.status === 'completed'
                      ? 'border-green-200 bg-green-50'
                      : file.status === 'failed'
                      ? 'border-red-200 bg-red-50'
                      : file.status === 'processing'
                      ? 'border-blue-200 bg-blue-50 animate-pulse'
                      : 'border-gray-200 bg-gray-50'
                  }`}
                >
                  {/* File preview/thumbnail - simplified for status view */}
                  <div className="aspect-square mb-3 rounded-lg overflow-hidden bg-gray-100 flex items-center justify-center">
                    {file.status === 'failed' ? (
                      <FileX className="h-8 w-8 text-red-400" />
                    ) : file.status === 'completed' ? (
                      <CheckCircle className="h-8 w-8 text-green-400" />
                    ) : file.status === 'processing' ? (
                      <Activity className="h-8 w-8 text-blue-400 animate-pulse" />
                    ) : (
                      <Clock className="h-8 w-8 text-gray-400" />
                    )}
                  </div>

                  {/* File info */}
                  <div className="space-y-2">
                    <div className="text-sm font-medium text-gray-900 truncate" title={file.filename}>
                      {file.filename}
                    </div>
                    
                    {/* Status badge */}
                    <div className="flex items-center gap-2">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
                          file.status === 'completed'
                            ? 'bg-green-100 text-green-700'
                            : file.status === 'failed'
                            ? 'bg-red-100 text-red-700'
                            : file.status === 'processing'
                            ? 'bg-blue-100 text-blue-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {file.status === 'completed' && <CheckCircle className="h-3 w-3" />}
                        {file.status === 'failed' && <AlertCircle className="h-3 w-3" />}
                        {file.status === 'processing' && <Activity className="h-3 w-3" />}
                        {file.status === 'queued' && <Clock className="h-3 w-3" />}
                        {file.status.charAt(0).toUpperCase() + file.status.slice(1)}
                      </span>
                    </div>

                    {/* Progress bar for individual files */}
                    {file.status === 'processing' && file.progress !== undefined && (
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${file.progress}%` }}
                        />
                      </div>
                    )}

                    {/* Error message */}
                    {file.error && (
                      <div className="text-xs text-red-600 bg-red-50 p-2 rounded border">
                        {file.error}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="text-center space-y-4">
          {/* Completion Actions */}
          {isCompleted && (
            <div className="space-y-3">
              <Link
                to={`/results/${jobResults?.job_id || status?.job_id || taskId}`}
                className="inline-block bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors"
              >
                View Results
              </Link>
              
              {/* Success summary for completed jobs */}
              {files.length > 0 && (
                <div className="text-sm text-gray-600">
                  <span className="font-medium text-green-600">
                    {files.filter(f => f.status === 'completed').length}
                  </span> of {files.length} files processed successfully
                  {files.some(f => f.status === 'failed') && (
                    <span className="ml-2 text-red-600">
                      ({files.filter(f => f.status === 'failed').length} failed)
                    </span>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Error Actions */}
          {isFailed && (
            <div className="space-y-3">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
                <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-2" />
                <h3 className="font-medium text-red-900 mb-2">Processing Failed</h3>
                <p className="text-sm text-red-700 mb-4">
                  {status?.error || 'An error occurred while processing your images.'}
                </p>
                
                {/* Retry options */}
                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                  <button
                    onClick={retryJob}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 transition-colors"
                  >
                    <RotateCcw className="h-4 w-4" />
                    Retry Processing
                  </button>
                  
                  <button
                    onClick={reconnect}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700 transition-colors"
                  >
                    <Wifi className="h-4 w-4" />
                    Reconnect
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Processing Actions */}
          {isProcessing && (
            <div className="space-y-3">
              <div className="text-sm text-gray-600">
                Processing in progress... Please keep this page open.
              </div>
              
              {/* Cancel button (if backend supports it) */}
              <button
                onClick={() => {
                  if (confirm('Are you sure you want to cancel processing? This cannot be undone.')) {
                    // This would need backend support to cancel jobs
                    fetch(`/api/cancel/${taskId}`, { method: 'POST' })
                      .catch(err => console.error('Cancel failed:', err))
                  }
                }}
                className="inline-flex items-center gap-2 px-4 py-2 bg-gray-500 text-white text-sm font-medium rounded-lg hover:bg-gray-600 transition-colors"
              >
                <AlertCircle className="h-3 w-3" />
                Cancel Processing
              </button>
            </div>
          )}
          
          {/* Common Actions */}
          <div className="pt-4 border-t border-gray-200">
            <Link
              to="/upload"
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Upload More Images
            </Link>
          </div>

          {/* Debug Info */}
          {process.env.NODE_ENV === 'development' && lastStatus && (
            <details className="mt-8 text-left">
              <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
                Debug: Raw Status Data
              </summary>
              <pre className="mt-2 p-4 bg-gray-100 rounded-lg text-xs overflow-auto">
                {JSON.stringify(lastStatus, null, 2)}
              </pre>
            </details>
          )}
        </div>
      </div>
    </div>
  )
}

export default ProcessingPage