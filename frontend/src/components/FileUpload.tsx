import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, X, FileImage, AlertCircle, Info } from 'lucide-react'
import { validateImageFiles, VALIDATION_RULES } from '@/utils/validation'
import { clsx } from 'clsx'

export interface FileUploadProps {
  onUpload: (files: File[], faceLimit?: number) => void
  isUploading?: boolean
  className?: string
}

interface FileWithPreview extends File {
  preview: string
}

const FileUpload: React.FC<FileUploadProps> = ({ 
  onUpload, 
  isUploading = false, 
  className 
}) => {
  const [files, setFiles] = useState<FileWithPreview[]>([])
  const [faceLimit, setFaceLimit] = useState<string>('')
  const [errors, setErrors] = useState<string[]>([])

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    // Clear previous errors
    setErrors([])
    
    // Filter out files that exceed size limit or are wrong type
    const validFiles = acceptedFiles.filter(file => {
      if (file.size > VALIDATION_RULES.MAX_FILE_SIZE) {
        setErrors(prev => [...prev, `${file.name} exceeds 10MB limit`])
        return false
      }
      return true
    })
    
    // Check total file count limit
    if (files.length + validFiles.length > VALIDATION_RULES.MAX_FILES_COUNT) {
      setErrors(prev => [...prev, `Maximum ${VALIDATION_RULES.MAX_FILES_COUNT} images allowed`])
      return
    }
    
    // Add rejected file messages
    rejectedFiles.forEach(({ file, errors: fileErrors }) => {
      fileErrors.forEach((error: any) => {
        if (error.code === 'file-invalid-type') {
          setErrors(prev => [...prev, `${file.name} is not a supported image format (JPEG or PNG only)`])
        } else if (error.code === 'file-too-large') {
          setErrors(prev => [...prev, `${file.name} exceeds 10MB limit`])
        }
      })
    })
    
    // Create file previews for valid files
    const filesWithPreviews = validFiles.map(file => 
      Object.assign(file, {
        preview: URL.createObjectURL(file)
      })
    )
    
    setFiles(prev => [...prev, ...filesWithPreviews])
  }, [files])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png']
    },
    maxSize: VALIDATION_RULES.MAX_FILE_SIZE,
    maxFiles: VALIDATION_RULES.MAX_FILES_COUNT
  })

  const removeFile = useCallback((index: number) => {
    setFiles(prev => {
      const newFiles = [...prev]
      // Revoke the object URL to prevent memory leaks
      URL.revokeObjectURL(newFiles[index].preview)
      newFiles.splice(index, 1)
      return newFiles
    })
  }, [])

  const clearAllFiles = useCallback(() => {
    files.forEach(file => URL.revokeObjectURL(file.preview))
    setFiles([])
    setErrors([])
  }, [files])

  const handleUpload = useCallback(() => {
    if (files.length === 0) return

    // Final validation before upload
    const validation = validateImageFiles(files)
    if (!validation.isValid) {
      setErrors(validation.errors)
      return
    }

    const faceLimitNumber = faceLimit ? parseInt(faceLimit, 10) : undefined
    onUpload(files, faceLimitNumber)
  }, [files, faceLimit, onUpload])

  const handleFaceLimitChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    // Only allow positive integers
    if (value === '' || /^\d+$/.test(value)) {
      setFaceLimit(value)
    }
  }, [])

  // Cleanup object URLs on unmount
  React.useEffect(() => {
    return () => {
      files.forEach(file => URL.revokeObjectURL(file.preview))
    }
  }, [])

  return (
    <div className={clsx('space-y-6', className)}>
      {/* Upload Zone */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div
          {...getRootProps()}
          className={clsx(
            'border-2 border-dashed rounded-lg p-8 text-center transition-all cursor-pointer',
            isDragActive
              ? 'border-blue-500 bg-blue-50 scale-105'
              : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50',
            isUploading && 'pointer-events-none opacity-50'
          )}
        >
          <input {...getInputProps()} />
          <Upload className={clsx(
            'h-12 w-12 mx-auto mb-4 transition-colors',
            isDragActive ? 'text-blue-500' : 'text-gray-400'
          )} />
          
          {isDragActive ? (
            <div>
              <h3 className="text-lg font-semibold text-blue-600 mb-2">
                Drop images here!
              </h3>
              <p className="text-blue-500">
                Release to add images to your upload
              </p>
            </div>
          ) : (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Drag & drop images or click to browse
              </h3>
              <p className="text-gray-600 mb-4">
                Supports JPEG and PNG files up to 10MB each
              </p>
              <p className="text-sm text-gray-500">
                Maximum {VALIDATION_RULES.MAX_FILES_COUNT} images per upload
              </p>
            </div>
          )}
        </div>

        {/* File count and limits info */}
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-600">
            {files.length} of {VALIDATION_RULES.MAX_FILES_COUNT} images selected
          </p>
        </div>
      </div>

      {/* Error Messages */}
      {errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start">
            <AlertCircle className="h-5 w-5 text-red-500 mt-0.5 mr-3 flex-shrink-0" />
            <div className="flex-1">
              <h4 className="text-sm font-medium text-red-800 mb-2">
                Please fix the following issues:
              </h4>
              <ul className="text-sm text-red-700 space-y-1">
                {errors.map((error, index) => (
                  <li key={index} className="flex items-start">
                    <span className="w-1 h-1 bg-red-500 rounded-full mt-2 mr-2 flex-shrink-0" />
                    {error}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Selected Files Preview */}
      {files.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Selected Images ({files.length})
            </h3>
            <button
              onClick={clearAllFiles}
              className="text-sm text-red-600 hover:text-red-700 font-medium"
              disabled={isUploading}
            >
              Clear All
            </button>
          </div>
          
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {files.map((file, index) => (
              <div key={index} className="relative group">
                <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                  <img
                    src={file.preview}
                    alt={file.name}
                    className="w-full h-full object-cover"
                    onLoad={() => URL.revokeObjectURL(file.preview)}
                  />
                </div>
                
                <button
                  onClick={() => removeFile(index)}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1.5 opacity-0 group-hover:opacity-100 transition-opacity shadow-sm"
                  disabled={isUploading}
                  title="Remove image"
                >
                  <X className="h-3 w-3" />
                </button>
                
                <div className="mt-2">
                  <p className="text-xs text-gray-600 truncate" title={file.name}>
                    {file.name}
                  </p>
                  <p className="text-xs text-gray-400">
                    {(file.size / (1024 * 1024)).toFixed(1)} MB
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Face Limit Configuration */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-start space-x-3">
          <Info className="h-5 w-5 text-blue-500 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Face Limit (optional)
            </label>
            <input
              type="text"
              value={faceLimit}
              onChange={handleFaceLimitChange}
              placeholder="Auto"
              className="w-full sm:w-32 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={isUploading}
            />
            <p className="text-xs text-gray-500 mt-2">
              Controls the level of detail in the generated 3D model. Higher values create more detailed models but take longer to process. Leave blank for automatic optimization.
            </p>
          </div>
        </div>
      </div>

      {/* Upload Button */}
      <div className="text-center">
        <button
          onClick={handleUpload}
          disabled={files.length === 0 || isUploading}
          className={clsx(
            'inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg shadow-sm text-white transition-all',
            files.length === 0 || isUploading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 hover:shadow-md active:bg-blue-800',
          )}
        >
          {isUploading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2" />
              Processing...
            </>
          ) : (
            <>
              <FileImage className="h-5 w-5 mr-2" />
              Upload and Generate 3D Models
            </>
          )}
        </button>
        
        {files.length > 0 && !isUploading && (
          <p className="text-sm text-gray-500 mt-2">
            Ready to upload {files.length} image{files.length === 1 ? '' : 's'}
          </p>
        )}
      </div>
    </div>
  )
}

export default FileUpload