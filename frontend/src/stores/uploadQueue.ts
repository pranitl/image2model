/**
 * Upload Queue Zustand Store
 * 
 * State management system for handling file uploads using Zustand.
 * Provides queue management, progress tracking, and session persistence.
 */

import { create } from 'zustand'
import { subscribeWithSelector } from 'zustand/middleware'
import { nanoid } from 'nanoid'
import type { GenerationOptions } from '../types'
import type {
  UploadQueueStore,
  UploadItem,
  UploadItemPatch,
  QueueStats,
  QueueSettings,
  UploadStatus,
  DEFAULT_QUEUE_SETTINGS,
  DEFAULT_UPLOAD_ITEM,
  STORAGE_KEYS
} from './types'

/**
 * Helper function to load settings from session storage
 */
const loadSettingsFromStorage = (): QueueSettings => {
  try {
    const stored = sessionStorage.getItem(STORAGE_KEYS.QUEUE_SETTINGS)
    if (stored) {
      const parsed = JSON.parse(stored)
      return { ...DEFAULT_QUEUE_SETTINGS, ...parsed }
    }
  } catch (error) {
    console.warn('Failed to load queue settings from storage:', error)
  }
  return DEFAULT_QUEUE_SETTINGS
}

/**
 * Helper function to save settings to session storage
 */
const saveSettingsToStorage = (settings: QueueSettings): void => {
  try {
    sessionStorage.setItem(STORAGE_KEYS.QUEUE_SETTINGS, JSON.stringify(settings))
  } catch (error) {
    console.warn('Failed to save queue settings to storage:', error)
  }
}

/**
 * Helper function to load face limit from session storage
 */
const loadFaceLimitFromStorage = (): number => {
  try {
    const stored = sessionStorage.getItem(STORAGE_KEYS.FACE_LIMIT)
    if (stored) {
      const parsed = parseInt(stored, 10)
      if (!isNaN(parsed) && parsed > 0) {
        return parsed
      }
    }
  } catch (error) {
    console.warn('Failed to load face limit from storage:', error)
  }
  return DEFAULT_QUEUE_SETTINGS.defaultFaceLimit
}

/**
 * Helper function to save face limit to session storage
 */
const saveFaceLimitToStorage = (faceLimit: number): void => {
  try {
    sessionStorage.setItem(STORAGE_KEYS.FACE_LIMIT, faceLimit.toString())
  } catch (error) {
    console.warn('Failed to save face limit to storage:', error)
  }
}

/**
 * Helper function to create a new upload item from a file
 */
const createUploadItem = (file: File, options?: GenerationOptions): UploadItem => {
  const id = nanoid()
  const previewURL = file.type.startsWith('image/') 
    ? URL.createObjectURL(file) 
    : ''

  return {
    ...DEFAULT_UPLOAD_ITEM,
    id,
    file,
    previewURL,
    createdAt: new Date(),
    generationOptions: options,
    status: 'queued',
    progress: 0,
    retryCount: 0,
    maxRetries: DEFAULT_QUEUE_SETTINGS.maxRetries
  } as UploadItem
}

/**
 * Helper function to calculate queue statistics
 */
const calculateStats = (items: UploadItem[]): QueueStats => {
  const stats = items.reduce(
    (acc, item) => {
      acc.total++
      acc[item.status]++
      acc.totalBytes += item.file.size
      
      if (item.status === 'completed' || item.status === 'uploading') {
        acc.uploadedBytes += Math.floor((item.progress / 100) * item.file.size)
      }
      
      return acc
    },
    {
      total: 0,
      queued: 0,
      uploading: 0,
      processing: 0,
      completed: 0,
      failed: 0,
      cancelled: 0,
      paused: 0,
      overallProgress: 0,
      totalBytes: 0,
      uploadedBytes: 0
    } as QueueStats
  )

  // Calculate overall progress percentage
  if (stats.totalBytes > 0) {
    stats.overallProgress = Math.round((stats.uploadedBytes / stats.totalBytes) * 100)
  }

  return stats
}

/**
 * Helper function to clean up blob URLs
 */
const cleanupBlobURLs = (items: UploadItem[]): void => {
  items.forEach(item => {
    if (item.previewURL && item.previewURL.startsWith('blob:')) {
      URL.revokeObjectURL(item.previewURL)
    }
  })
}

/**
 * Initial store state
 */
const getInitialState = () => {
  const settings = loadSettingsFromStorage()
  const faceLimit = loadFaceLimitFromStorage()
  
  // Update default face limit in settings if different from storage
  if (settings.defaultFaceLimit !== faceLimit) {
    settings.defaultFaceLimit = faceLimit
  }

  return {
    items: [],
    settings,
    isActive: false,
    isPaused: false
  }
}

/**
 * Upload Queue Zustand Store
 * 
 * Main store implementation with all actions and state management
 */
export const useUploadQueue = create<UploadQueueStore>()(
  subscribeWithSelector((set, get) => ({
    ...getInitialState(),

    // Actions implementation will be added in the next subtask
    addFiles: (files: File[], options?: GenerationOptions) => {
      // Placeholder - will be implemented in subtask 3.3
      console.log('addFiles called with', files.length, 'files')
    },

    addFile: (file: File, options?: GenerationOptions) => {
      // Placeholder - will be implemented in subtask 3.3
      console.log('addFile called with', file.name)
    },

    updateItem: (id: string, patch: UploadItemPatch) => {
      // Placeholder - will be implemented in subtask 3.3
      console.log('updateItem called for', id, 'with patch', patch)
    },

    removeItem: (id: string) => {
      // Placeholder - will be implemented in subtask 3.3
      console.log('removeItem called for', id)
    },

    clearQueue: (filter?: (item: UploadItem) => boolean) => {
      // Placeholder - will be implemented in subtask 3.3
      console.log('clearQueue called with filter', !!filter)
    },

    startItem: (id: string) => {
      // Placeholder - will be implemented in subtask 3.3
      console.log('startItem called for', id)
    },

    pauseItem: (id: string) => {
      // Placeholder - will be implemented in subtask 3.3
      console.log('pauseItem called for', id)
    },

    cancelItem: (id: string) => {
      // Placeholder - will be implemented in subtask 3.3
      console.log('cancelItem called for', id)
    },

    retryItem: (id: string) => {
      // Placeholder - will be implemented in subtask 3.3
      console.log('retryItem called for', id)
    },

    startAll: () => {
      // Placeholder - will be implemented in subtask 3.3
      console.log('startAll called')
    },

    pauseAll: () => {
      // Placeholder - will be implemented in subtask 3.3
      console.log('pauseAll called')
    },

    cancelAll: () => {
      // Placeholder - will be implemented in subtask 3.3
      console.log('cancelAll called')
    },

    getStats: (): QueueStats => {
      const { items } = get()
      return calculateStats(items)
    },

    updateSettings: (newSettings: Partial<QueueSettings>) => {
      set((state) => {
        const updatedSettings = { ...state.settings, ...newSettings }
        
        // Save to session storage
        saveSettingsToStorage(updatedSettings)
        
        // Save face limit separately if updated
        if (newSettings.defaultFaceLimit !== undefined) {
          saveFaceLimitToStorage(newSettings.defaultFaceLimit)
        }
        
        return {
          ...state,
          settings: updatedSettings
        }
      })
    },

    reset: () => {
      const { items } = get()
      
      // Clean up any existing blob URLs
      cleanupBlobURLs(items)
      
      // Reset to initial state
      set(getInitialState())
    },

    _cleanupBlobURLs: (itemIds: string[]) => {
      const { items } = get()
      const itemsToCleanup = items.filter(item => itemIds.includes(item.id))
      cleanupBlobURLs(itemsToCleanup)
    }
  }))
)

/**
 * Selector hooks for optimized component subscriptions
 */

// Get queue items
export const useQueueItems = () => useUploadQueue(state => state.items)

// Get queue statistics
export const useQueueStats = () => useUploadQueue(state => calculateStats(state.items))

// Get queue settings
export const useQueueSettings = () => useUploadQueue(state => state.settings)

// Get specific item by ID
export const useQueueItem = (id: string) => 
  useUploadQueue(state => state.items.find(item => item.id === id))

// Get items by status
export const useItemsByStatus = (status: UploadStatus) =>
  useUploadQueue(state => state.items.filter(item => item.status === status))

// Get active uploads (uploading or processing)
export const useActiveUploads = () =>
  useUploadQueue(state => 
    state.items.filter(item => 
      item.status === 'uploading' || item.status === 'processing'
    )
  )

// Get queue state flags
export const useQueueState = () => 
  useUploadQueue(state => ({
    isActive: state.isActive,
    isPaused: state.isPaused,
    hasItems: state.items.length > 0
  }))

/**
 * Auto-cleanup effect for blob URLs on unmount
 * Call this in components that use the store to ensure proper cleanup
 */
export const useUploadQueueCleanup = () => {
  const reset = useUploadQueue(state => state.reset)
  
  // Return cleanup function
  return () => {
    reset()
  }
}