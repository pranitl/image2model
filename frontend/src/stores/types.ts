/**
 * Upload Queue Store Types
 * 
 * Type definitions for the Zustand upload queue state management system.
 * These interfaces define the structure for upload queue items, store state,
 * and all related actions for managing file uploads.
 */

import type { GenerationOptions } from '../types'

/**
 * Upload status enumeration
 * Defines all possible states for an upload item
 */
export type UploadStatus = 
  | 'queued'      // File is queued for upload
  | 'uploading'   // File is currently being uploaded
  | 'processing'  // File is being processed by the backend
  | 'completed'   // Upload and processing completed successfully
  | 'failed'      // Upload or processing failed
  | 'cancelled'   // Upload was cancelled by user
  | 'paused'      // Upload is temporarily paused

/**
 * Individual upload queue item
 * Represents a single file in the upload queue with all its metadata
 */
export interface UploadItem {
  /** Unique identifier for the upload item */
  id: string
  
  /** The actual file object to be uploaded */
  file: File
  
  /** Preview URL for the file (blob URL for images) */
  previewURL: string
  
  /** Current upload status */
  status: UploadStatus
  
  /** Upload progress (0-100) */
  progress: number
  
  /** Upload speed in bytes per second */
  uploadSpeed?: number
  
  /** Estimated time remaining in seconds */
  estimatedTimeRemaining?: number
  
  /** Error message if upload failed */
  errorMessage?: string
  
  /** Timestamp when item was added to queue */
  createdAt: Date
  
  /** Timestamp when upload started */
  startedAt?: Date
  
  /** Timestamp when upload completed */
  completedAt?: Date
  
  /** Backend job ID once upload starts */
  jobId?: string
  
  /** Generation options for this upload */
  generationOptions?: GenerationOptions
  
  /** Number of retry attempts */
  retryCount?: number
  
  /** Maximum number of retries allowed */
  maxRetries?: number
}

/**
 * Upload queue statistics
 * Provides aggregate information about the upload queue
 */
export interface QueueStats {
  /** Total number of items in queue */
  total: number
  
  /** Number of items currently queued */
  queued: number
  
  /** Number of items currently uploading */
  uploading: number
  
  /** Number of items being processed */
  processing: number
  
  /** Number of completed items */
  completed: number
  
  /** Number of failed items */
  failed: number
  
  /** Number of cancelled items */
  cancelled: number
  
  /** Number of paused items */
  paused: number
  
  /** Overall progress percentage (0-100) */
  overallProgress: number
  
  /** Total bytes to upload */
  totalBytes: number
  
  /** Bytes uploaded so far */
  uploadedBytes: number
}

/**
 * Upload queue settings
 * Configuration options for the upload queue behavior
 */
export interface QueueSettings {
  /** Maximum number of concurrent uploads */
  maxConcurrentUploads: number
  
  /** Maximum number of retry attempts per file */
  maxRetries: number
  
  /** Auto-start uploads when files are added */
  autoStart: boolean
  
  /** Auto-remove completed items after delay (milliseconds) */
  autoRemoveCompleted?: number
  
  /** Auto-remove failed items after delay (milliseconds) */
  autoRemoveFailed?: number
  
  /** Default face limit for 3D generation */
  defaultFaceLimit: number
}

/**
 * Patch object for updating upload items
 * Allows partial updates to upload item properties
 */
export type UploadItemPatch = Partial<Pick<UploadItem, 
  | 'status' 
  | 'progress' 
  | 'uploadSpeed'
  | 'estimatedTimeRemaining'
  | 'errorMessage'
  | 'jobId'
  | 'generationOptions'
  | 'retryCount'
  | 'startedAt'
  | 'completedAt'
>>

/**
 * Upload queue store state interface
 * Defines the complete state structure for the Zustand store
 */
export interface UploadQueueState {
  /** Array of upload items in the queue */
  items: UploadItem[]
  
  /** Queue settings and configuration */
  settings: QueueSettings
  
  /** Whether the queue is currently active */
  isActive: boolean
  
  /** Whether uploads should auto-start */
  isPaused: boolean
}

/**
 * Upload queue store actions interface
 * Defines all available actions for managing the upload queue
 */
export interface UploadQueueActions {
  /**
   * Add multiple files to the upload queue
   * @param files - Array of File objects to add
   * @param options - Optional generation options for all files
   */
  addFiles: (files: File[], options?: GenerationOptions) => void
  
  /**
   * Add a single file to the upload queue
   * @param file - File object to add
   * @param options - Optional generation options
   */
  addFile: (file: File, options?: GenerationOptions) => void
  
  /**
   * Update an upload item with partial data
   * @param id - ID of the item to update
   * @param patch - Partial update data
   */
  updateItem: (id: string, patch: UploadItemPatch) => void
  
  /**
   * Remove an item from the upload queue
   * @param id - ID of the item to remove
   */
  removeItem: (id: string) => void
  
  /**
   * Clear all items from the queue
   * @param filter - Optional filter to only clear specific items
   */
  clearQueue: (filter?: (item: UploadItem) => boolean) => void
  
  /**
   * Start uploading a specific item
   * @param id - ID of the item to start
   */
  startItem: (id: string) => void
  
  /**
   * Pause uploading a specific item
   * @param id - ID of the item to pause
   */
  pauseItem: (id: string) => void
  
  /**
   * Cancel uploading a specific item
   * @param id - ID of the item to cancel
   */
  cancelItem: (id: string) => void
  
  /**
   * Retry a failed upload item
   * @param id - ID of the item to retry
   */
  retryItem: (id: string) => void
  
  /**
   * Start all queued uploads
   */
  startAll: () => void
  
  /**
   * Pause all active uploads
   */
  pauseAll: () => void
  
  /**
   * Cancel all uploads
   */
  cancelAll: () => void
  
  /**
   * Get queue statistics
   * @returns Current queue statistics
   */
  getStats: () => QueueStats
  
  /**
   * Update queue settings
   * @param settings - Partial settings to update
   */
  updateSettings: (settings: Partial<QueueSettings>) => void
  
  /**
   * Reset queue to initial state
   */
  reset: () => void
  
  /**
   * Clean up blob URLs for removed items
   * Internal method for memory management
   */
  _cleanupBlobURLs: (itemIds: string[]) => void
}

/**
 * Complete upload queue store interface
 * Combines state and actions for the Zustand store
 */
export interface UploadQueueStore extends UploadQueueState, UploadQueueActions {}

/**
 * Storage keys for session persistence
 */
export const STORAGE_KEYS = {
  QUEUE_SETTINGS: 'uploadQueue:settings',
  FACE_LIMIT: 'uploadQueue:faceLimit',
  QUEUE_STATE: 'uploadQueue:state'
} as const

/**
 * Default queue settings
 */
export const DEFAULT_QUEUE_SETTINGS: QueueSettings = {
  maxConcurrentUploads: 3,
  maxRetries: 3,
  autoStart: true,
  autoRemoveCompleted: 30000, // 30 seconds
  autoRemoveFailed: 60000,    // 60 seconds
  defaultFaceLimit: 50000
} as const

/**
 * Default upload item properties
 */
export const DEFAULT_UPLOAD_ITEM: Partial<UploadItem> = {
  status: 'queued',
  progress: 0,
  retryCount: 0,
  maxRetries: 3
} as const