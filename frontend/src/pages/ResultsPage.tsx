import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Download, Eye, RotateCcw, CheckCircle, Clock, AlertCircle } from 'lucide-react'
import { apiRequest } from '@/utils/api'

interface TaskResult {
  file_path: string
  status: string
  result_path?: string
  download_url?: string
  model_format?: string
  rendered_image?: string
  filename?: string
}

interface ProcessingJob {
  id: string
  task_id: string
  status: 'queued' | 'processing' | 'completed' | 'failed'
  progress: number
  inputImage: string
  filename: string
  results?: TaskResult[]
  createdAt: string
  error?: string
}

const ResultsPage: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>()
  const [job, setJob] = useState<ProcessingJob | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showPreview, setShowPreview] = useState(false)
  const [previewImage, setPreviewImage] = useState<string | null>(null)

  useEffect(() => {
    const fetchJobStatus = async () => {
      if (!jobId) {
        setError('No job ID provided')
        setLoading(false)
        return
      }

      try {
        // Get the task ID from localStorage (saved during upload)
        const taskData = localStorage.getItem(`job_${jobId}`)
        if (!taskData) {
          setError('Job information not found')
          setLoading(false)
          return
        }

        const { taskId, fileId, filename, uploadPath } = JSON.parse(taskData)

        // Fetch task status
        const response = await apiRequest.get(`/status/tasks/${taskId}/status`)
        const taskStatus = response.data.data

        // Map task status to job status
        let jobStatus: ProcessingJob['status'] = 'queued'
        if (taskStatus.status === 'queued') jobStatus = 'queued'
        else if (taskStatus.status === 'processing') jobStatus = 'processing'
        else if (taskStatus.status === 'completed') jobStatus = 'completed'
        else if (taskStatus.status === 'failed') jobStatus = 'failed'

        // Create job object from task status
        const jobData: ProcessingJob = {
          id: jobId,
          task_id: taskId,
          status: jobStatus,
          progress: taskStatus.progress || 0,
          inputImage: uploadPath || '/api/placeholder/300/300',
          filename: filename || 'Uploaded Image',
          createdAt: new Date().toISOString(),
          error: taskStatus.error
        }

        // If completed, extract results
        if (taskStatus.status === 'completed' && taskStatus.result) {
          const meta = taskStatus.result
          if (meta.results && Array.isArray(meta.results)) {
            jobData.results = meta.results
          }
        }

        setJob(jobData)
      } catch (err) {
        console.error('Error fetching job status:', err)
        setError('Failed to fetch job status')
      } finally {
        setLoading(false)
      }
    }

    fetchJobStatus()
    
    // Poll for updates if not completed
    const interval = setInterval(() => {
      if (job && (job.status === 'completed' || job.status === 'failed')) {
        clearInterval(interval)
      } else {
        fetchJobStatus()
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [jobId, job?.status])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-6 w-6 text-green-500" />
      case 'processing':
        return <Clock className="h-6 w-6 text-blue-500" />
      case 'failed':
        return <AlertCircle className="h-6 w-6 text-red-500" />
      default:
        return <Clock className="h-6 w-6 text-gray-500" />
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Completed'
      case 'processing':
        return 'Processing'
      case 'failed':
        return 'Failed'
      default:
        return 'Pending'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="container mx-auto px-4 max-w-4xl text-center">
          <div className="spinner mx-auto mb-4" />
          <p className="text-gray-600">Loading results...</p>
        </div>
      </div>
    )
  }

  if (error || !job) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="container mx-auto px-4 max-w-4xl text-center">
          <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            {error || 'Job Not Found'}
          </h1>
          <p className="text-gray-600 mb-8">
            {error || 'The requested job could not be found.'}
          </p>
          <Link to="/upload" className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors">
            Upload New Images
          </Link>
        </div>
      </div>
    )
  }

  const handlePreview = (imageUrl: string) => {
    setPreviewImage(imageUrl)
    setShowPreview(true)
  }

  const handleDownload = async (jobId: string, filename: string) => {
    try {
      const downloadUrl = `/api/v1/download/${jobId}/${filename}`
      window.open(downloadUrl, '_blank')
    } catch (err) {
      console.error('Download failed:', err)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold text-gray-900">
              Processing Results
            </h1>
            <div className="flex items-center gap-2">
              {getStatusIcon(job.status)}
              <span className="font-medium text-gray-900">
                {getStatusText(job.status)}
              </span>
            </div>
          </div>
          
          <div className="grid md:grid-cols-3 gap-4 text-sm text-gray-600">
            <div>
              <span className="font-medium">Job ID:</span> {job.id}
            </div>
            <div>
              <span className="font-medium">Created:</span> {new Date(job.createdAt).toLocaleString()}
            </div>
            <div>
              <span className="font-medium">Images:</span> {job.inputImages.length}
            </div>
          </div>

          {job.status === 'processing' && (
            <div className="mt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Progress</span>
                <span className="text-sm text-gray-600">{job.progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${job.progress}%` }}
                />
              </div>
            </div>
          )}
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Input Image */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Input Image
            </h2>
            <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
              <img
                src={job.inputImage}
                alt={job.filename}
                className="w-full h-full object-cover"
              />
            </div>
            <p className="mt-2 text-sm text-gray-600 text-center">{job.filename}</p>
          </div>

          {/* Output Models */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Generated 3D Model
            </h2>
            {job.status === 'completed' && job.results && job.results.length > 0 ? (
              <div className="space-y-4">
                {job.results.map((result, index) => {
                  if (result.status !== 'completed') return null
                  
                  const modelFilename = result.filename || 
                    result.result_path?.split('/').pop() || 
                    `model_${index + 1}.glb`
                  
                  return (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <h3 className="font-medium text-gray-900">{modelFilename}</h3>
                          <p className="text-sm text-gray-600">
                            {result.model_format?.toUpperCase() || 'GLB'} Format
                          </p>
                        </div>
                        <div className="flex gap-2">
                          {(result.rendered_image || (result as any).rendered_image?.url) && (
                            <button 
                              onClick={() => {
                                const imageUrl = typeof result.rendered_image === 'string' 
                                  ? result.rendered_image 
                                  : (result as any).rendered_image?.url
                                if (imageUrl) handlePreview(imageUrl)
                              }}
                              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                              title="Preview rendered image"
                            >
                              <Eye className="h-4 w-4" />
                            </button>
                          )}
                          <button 
                            onClick={() => handleDownload(job.id, modelFilename)}
                            className="p-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Download 3D model"
                          >
                            <Download className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                      {(result.rendered_image || (result as any).rendered_image?.url) && (
                        <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
                          <img
                            src={
                              typeof result.rendered_image === 'string' 
                                ? result.rendered_image 
                                : (result as any).rendered_image?.url
                            }
                            alt={`Preview of ${modelFilename}`}
                            className="w-full h-full object-contain"
                          />
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            ) : job.status === 'processing' ? (
              <div className="text-center py-8">
                <div className="spinner mx-auto mb-4" />
                <p className="text-gray-600">Generating 3D model...</p>
                {job.progress > 0 && (
                  <div className="mt-4">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${job.progress}%` }}
                      />
                    </div>
                    <p className="text-sm text-gray-600 mt-2">{job.progress}% complete</p>
                  </div>
                )}
              </div>
            ) : job.status === 'failed' ? (
              <div className="text-center py-8">
                <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
                <p className="text-gray-600 mb-2">Processing failed</p>
                {job.error && (
                  <p className="text-sm text-red-600 mb-4">{job.error}</p>
                )}
                <Link 
                  to="/upload"
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center gap-2"
                >
                  <RotateCcw className="h-4 w-4" />
                  Try Again
                </Link>
              </div>
            ) : (
              <div className="text-center py-8">
                <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">Waiting to start processing...</p>
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="mt-8 text-center">
          <Link
            to="/upload"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Upload More Images
          </Link>
        </div>
      </div>

      {/* Preview Modal */}
      {showPreview && previewImage && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={() => setShowPreview(false)}
        >
          <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] overflow-hidden">
            <div className="p-4 border-b flex justify-between items-center">
              <h3 className="text-lg font-semibold">3D Model Preview</h3>
              <button
                onClick={() => setShowPreview(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-4">
              <img
                src={previewImage}
                alt="3D Model Preview"
                className="max-w-full max-h-[70vh] object-contain"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ResultsPage