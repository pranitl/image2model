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
      
      // For single file upload, use 'file' parameter
      if (files.length === 1) {
        formData.append('file', files[0])
      } else {
        // For multiple files, append each as 'file'
        files.forEach((file) => {
          formData.append('file', file)
        })
      }
      
      // Add generation options
      formData.append('options', JSON.stringify(options))

      // Upload files with progress tracking
      const response = await apiRequest.upload<any>(
        '/upload/image',
        formData,
        (progress) => {
          setUploadProgress(progress)
        }
      )

      // Backend returns direct UploadResponse, not wrapped in ApiResponse
      const uploadData = response.data
      if (uploadData && uploadData.file_id) {
        // Convert backend response to UploadJob format
        const uploadJob: UploadJob = {
          id: uploadData.file_id,
          taskId: uploadData.task_id,  // Include task ID for monitoring
          status: 'pending',
          progress: 0,
          inputImages: [{
            id: uploadData.file_id,
            filename: uploadData.filename,
            originalName: uploadData.filename,
            size: uploadData.file_size,
            mimeType: uploadData.content_type,
            url: `/download/${uploadData.file_id}`,
            uploadedAt: new Date().toISOString()
          }],
          outputModels: [],
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        }
        return uploadJob
      } else {
        throw new Error('Upload failed: Invalid response format')
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