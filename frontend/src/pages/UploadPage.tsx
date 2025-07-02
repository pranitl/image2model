import React from 'react'
import { useNavigate } from 'react-router-dom'
import { FileUpload } from '@/components'
import { useUpload } from '@/hooks'

const UploadPage: React.FC = () => {
  const navigate = useNavigate()
  const { uploadFiles, isUploading, error, clearError } = useUpload()

  const handleUpload = async (files: File[], faceLimit?: number) => {
    // Clear any previous errors
    clearError()
    
    try {
      const generationOptions = {
        quality: 'standard' as const,
        outputFormat: 'gltf' as const,
        generateTextures: true,
        optimizeForPrinting: false,
        faceLimit
      }
      
      const uploadJob = await uploadFiles(files, generationOptions)
      
      if (uploadJob) {
        // Navigate to the processing page to show real-time progress
        navigate(`/processing/${uploadJob.id}`)
      }
    } catch (err) {
      console.error('Upload failed:', err)
      // Error handling is managed by the useUpload hook
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Upload Your Images
          </h1>
          <p className="text-xl text-gray-600">
            Select or drag and drop images to convert them into 3D models
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">
                  Upload Failed
                </h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>{error}</p>
                </div>
                <div className="mt-4">
                  <button
                    onClick={clearError}
                    className="bg-red-100 px-3 py-2 rounded-md text-sm font-medium text-red-800 hover:bg-red-200"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* File Upload Component */}
        <FileUpload 
          onUpload={handleUpload}
          isUploading={isUploading}
        />
      </div>
    </div>
  )
}

export default UploadPage