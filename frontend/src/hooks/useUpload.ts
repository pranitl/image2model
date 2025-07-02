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
      
      files.forEach((file) => {
        formData.append(`images`, file)
      })
      
      // Add generation options
      formData.append('options', JSON.stringify(options))

      // Upload files with progress tracking
      const response = await apiRequest.upload<UploadJob>(
        '/upload',
        formData,
        (progress) => {
          setUploadProgress(progress)
        }
      )

      if (response.data.success && response.data.data) {
        return response.data.data
      } else {
        throw new Error(response.data.error || 'Upload failed')
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