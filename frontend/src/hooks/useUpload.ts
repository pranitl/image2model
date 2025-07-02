import { useState, useCallback } from 'react'
import { apiRequest, handleApiError } from '@/utils/api'
import { validateImageFiles } from '@/utils/validation'
import type { UploadJob, GenerationOptions } from '@/types'

interface UseUploadReturn {
  uploadFiles: (files: File[], options?: GenerationOptions) => Promise<UploadJob | null>
  isUploading: boolean
  uploadProgress: number
  error: string | null
  clearError: () => void
}

export const useUpload = (): UseUploadReturn => {
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const uploadFiles = useCallback(async (
    files: File[],
    options: GenerationOptions = {
      quality: 'standard',
      outputFormat: 'obj',
      generateTextures: true,
      optimizeForPrinting: false,
    }
  ): Promise<UploadJob | null> => {
    setError(null)
    setUploadProgress(0)

    // Validate files
    const validation = validateImageFiles(files)
    if (!validation.isValid) {
      setError(validation.errors.join(', '))
      return null
    }

    setIsUploading(true)

    try {
      // Prepare form data
      const formData = new FormData()
      
      // Choose endpoint based on file count
      let endpoint: string
      if (files.length === 1) {
        // Single file upload - use /api/v1/upload/image
        endpoint = '/api/v1/upload/image'
        formData.append('file', files[0])
      } else {
        // Multiple files upload - use /api/v1/upload/batch
        endpoint = '/api/v1/upload/batch'
        files.forEach((file) => {
          formData.append('files', file)
        })
        
        // Add face_limit from options if specified
        if (options.faceLimit) {
          formData.append('face_limit', options.faceLimit.toString())
        }
      }

      // Upload files with progress tracking
      const response = await apiRequest.upload<UploadJob>(
        endpoint,
        formData,
        (progress) => {
          setUploadProgress(progress)
        }
      )

      // Backend returns direct response, not wrapped in ApiResponse
      if (response.data) {
        return response.data as UploadJob
      } else {
        throw new Error('Upload failed - no response data')
      }
    } catch (err: any) {
      const errorMessage = handleApiError(err)
      setError(errorMessage)
      return null
    } finally {
      setIsUploading(false)
      setUploadProgress(0)
    }
  }, [])

  return {
    uploadFiles,
    isUploading,
    uploadProgress,
    error,
    clearError,
  }
}