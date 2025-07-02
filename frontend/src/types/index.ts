export interface UploadJob {
  id: string
  taskId?: string  // Added for tracking Celery task
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  inputImages: UploadedImage[]
  outputModels: GeneratedModel[]
  createdAt: string
  updatedAt: string
  estimatedCompletion?: string
  errorMessage?: string
}

export interface UploadedImage {
  id: string
  filename: string
  originalName: string
  size: number
  mimeType: string
  url: string
  uploadedAt: string
}

export interface GeneratedModel {
  id: string
  name: string
  format: ModelFormat
  size: number
  downloadUrl: string
  previewUrl: string
  thumbnailUrl: string
  createdAt: string
  metadata?: {
    vertices?: number
    faces?: number
    materials?: number
  }
}

export type ModelFormat = 'obj' | 'gltf' | 'fbx' | 'stl' | 'ply'

export interface GenerationOptions {
  quality: 'standard' | 'high' | 'ultra'
  outputFormat: ModelFormat
  generateTextures: boolean
  optimizeForPrinting: boolean
  targetPolyCount?: number
  faceLimit?: number
}

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

// Navigation types
export interface NavItem {
  name: string
  href: string
  icon?: React.ComponentType<{ className?: string }>
  current?: boolean
}

// Form types
export interface FormErrors {
  [key: string]: string | string[]
}

// API Error types
export interface ApiError {
  code: string
  message: string
  details?: Record<string, any>
}