import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Download, Eye, RotateCcw, CheckCircle, Clock, AlertCircle } from 'lucide-react'

interface ProcessingJob {
  id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  inputImages: string[]
  outputModels?: Array<{
    id: string
    name: string
    format: string
    size: string
    downloadUrl: string
    previewUrl: string
  }>
  createdAt: string
  estimatedCompletion?: string
}

const ResultsPage: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>()
  const [job, setJob] = useState<ProcessingJob | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // TODO: Replace with actual API call
    const mockJob: ProcessingJob = {
      id: jobId || 'mock-job-id',
      status: 'completed',
      progress: 100,
      inputImages: [
        '/api/placeholder/300/300',
        '/api/placeholder/300/300',
      ],
      outputModels: [
        {
          id: '1',
          name: 'model_001.obj',
          format: 'OBJ',
          size: '2.4 MB',
          downloadUrl: '#',
          previewUrl: '/api/placeholder/400/400'
        },
        {
          id: '2',
          name: 'model_001.gltf',
          format: 'GLTF',
          size: '1.8 MB',
          downloadUrl: '#',
          previewUrl: '/api/placeholder/400/400'
        }
      ],
      createdAt: new Date().toISOString(),
    }

    setTimeout(() => {
      setJob(mockJob)
      setLoading(false)
    }, 1000)
  }, [jobId])

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

  if (!job) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="container mx-auto px-4 max-w-4xl text-center">
          <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Job Not Found</h1>
          <p className="text-gray-600 mb-8">The requested job could not be found.</p>
          <Link to="/upload" className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors">
            Upload New Images
          </Link>
        </div>
      </div>
    )
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
          {/* Input Images */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Input Images
            </h2>
            <div className="grid grid-cols-2 gap-4">
              {job.inputImages.map((image, index) => (
                <div key={index} className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                  <img
                    src={image}
                    alt={`Input ${index + 1}`}
                    className="w-full h-full object-cover"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Output Models */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Generated Models
            </h2>
            {job.status === 'completed' && job.outputModels ? (
              <div className="space-y-4">
                {job.outputModels.map((model) => (
                  <div key={model.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h3 className="font-medium text-gray-900">{model.name}</h3>
                        <p className="text-sm text-gray-600">
                          {model.format} • {model.size}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
                          <Eye className="h-4 w-4" />
                        </button>
                        <button className="p-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors">
                          <Download className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                    <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
                      <img
                        src={model.previewUrl}
                        alt={`Preview of ${model.name}`}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : job.status === 'processing' ? (
              <div className="text-center py-8">
                <div className="spinner mx-auto mb-4" />
                <p className="text-gray-600">Generating 3D models...</p>
              </div>
            ) : job.status === 'failed' ? (
              <div className="text-center py-8">
                <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
                <p className="text-gray-600 mb-4">Processing failed. Please try again.</p>
                <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 mx-auto">
                  <RotateCcw className="h-4 w-4" />
                  Retry
                </button>
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
    </div>
  )
}

export default ResultsPage