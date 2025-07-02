import { useState, useCallback } from 'react'
import { apiRequest, handleApiError } from '@/utils/api'
import { validateImageFiles } from '@/utils/validation'
import type { UploadJob, UploadJobWithTaskId, GenerationOptions } from '@/types'

interface UseUploadReturn {
  uploadFiles: (files: File[], options?: GenerationOptions) => Promise<UploadJobWithTaskId | null>
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
  ): Promise<UploadJobWithTaskId | null> => {
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
        // Extract the actual upload job from the response
        const uploadJob = (response.data as any).success !== undefined 
          ? (response.data as any).data as UploadJob
          : response.data as UploadJob
        
        // Extract task ID based on upload type
        let taskId: string
        if ('job_id' in uploadJob) {
          // Batch upload - use job_id for SSE streaming
          taskId = uploadJob.job_id
        } else if ('file_id' in uploadJob) {
          // Single file upload - for now, use file_id as task ID
          // Note: Single file uploads might not trigger background processing
          // but we need a consistent interface for the frontend
          taskId = uploadJob.file_id
        } else {
          throw new Error('Upload response missing required ID field')
        }
        
        return {
          taskId,
          data: uploadJob
        }
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