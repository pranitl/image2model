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
  PersistedQueueItem,
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
 * Helper function to serialize queue state for storage
 * Excludes File objects and blob URLs which cannot be serialized
 */
const serializeQueueState = (items: UploadItem[]) => {
  return items.map(item => ({
    id: item.id,
    filename: item.file.name,
    size: item.file.size,
    type: item.file.type,
    status: item.status,
    progress: item.progress,
    uploadSpeed: item.uploadSpeed,
    estimatedTimeRemaining: item.estimatedTimeRemaining,
    errorMessage: item.errorMessage,
    createdAt: item.createdAt.toISOString(),
    startedAt: item.startedAt?.toISOString(),
    completedAt: item.completedAt?.toISOString(),
    jobId: item.jobId,
    generationOptions: item.generationOptions,
    retryCount: item.retryCount,
    maxRetries: item.maxRetries
  }))
}

/**
 * Helper function to save queue state to session storage
 * Only saves essential metadata, not the actual files
 */
const saveQueueStateToStorage = (items: UploadItem[]): void => {
  try {
    const serializedItems = serializeQueueState(items)
    sessionStorage.setItem(STORAGE_KEYS.QUEUE_STATE, JSON.stringify({
      items: serializedItems,
      timestamp: new Date().toISOString()
    }))
  } catch (error) {
    console.warn('Failed to save queue state to storage:', error)
  }
}

/**
 * Helper function to load queue state from session storage
 * Returns serialized items that can be used to restore queue display
 */
const loadQueueStateFromStorage = () => {
  try {
    const stored = sessionStorage.getItem(STORAGE_KEYS.QUEUE_STATE)
    if (stored) {
      const parsed = JSON.parse(stored)
      
      // Check if the stored data is not too old (1 hour)
      const timestamp = new Date(parsed.timestamp)
      const now = new Date()
      const hoursSinceStored = (now.getTime() - timestamp.getTime()) / (1000 * 60 * 60)
      
      if (hoursSinceStored < 1) {
        return parsed.items.map((item: any) => ({
          ...item,
          createdAt: new Date(item.createdAt),
          startedAt: item.startedAt ? new Date(item.startedAt) : undefined,
          completedAt: item.completedAt ? new Date(item.completedAt) : undefined
        }))
      } else {
        // Clear old data
        sessionStorage.removeItem(STORAGE_KEYS.QUEUE_STATE)
      }
    }
  } catch (error) {
    console.warn('Failed to load queue state from storage:', error)
  }
  return []
}

/**
 * Helper function to clear all storage data
 */
const clearStorageData = (): void => {
  try {
    Object.values(STORAGE_KEYS).forEach(key => {
      sessionStorage.removeItem(key)
    })
  } catch (error) {
    console.warn('Failed to clear storage data:', error)
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
 * Loads persisted settings and queue state from session storage
 */
const getInitialState = () => {
  const settings = loadSettingsFromStorage()
  const faceLimit = loadFaceLimitFromStorage()
  
  // Update default face limit in settings if different from storage
  if (settings.defaultFaceLimit !== faceLimit) {
    settings.defaultFaceLimit = faceLimit
  }

  // Load persisted queue state (metadata only, files cannot be restored)
  const persistedQueueItems = loadQueueStateFromStorage()

  return {
    items: [],
    settings,
    isActive: false,
    isPaused: false,
    // Store persisted queue metadata for display purposes
    persistedItems: persistedQueueItems
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

    // Add multiple files to the queue
    addFiles: (files: File[], options?: GenerationOptions) => {
      if (files.length === 0) return

      set((state) => {
        const newItems = files.map(file => createUploadItem(file, options))
        
        return {
          ...state,
          items: [...state.items, ...newItems],
          isActive: true
        }
      })

      // Persist state after adding files
      const { _persistState } = get()
      _persistState()

      // Auto-start uploads if enabled
      const { settings } = get()
      if (settings.autoStart) {
        // Delay to ensure state is updated
        setTimeout(() => {
          const { startAll } = get()
          startAll()
        }, 0)
      }
    },

    addFile: (file: File, options?: GenerationOptions) => {
      const { addFiles } = get()
      addFiles([file], options)
    },

    updateItem: (id: string, patch: UploadItemPatch) => {
      set((state) => ({
        ...state,
        items: state.items.map(item => 
          item.id === id 
            ? { 
                ...item, 
                ...patch,
                // Update timestamps based on status changes
                ...(patch.status === 'uploading' && !item.startedAt ? { startedAt: new Date() } : {}),
                ...(patch.status === 'completed' || patch.status === 'failed' ? { completedAt: new Date() } : {})
              }
            : item
        )
      }))

      // Persist state after updating item
      const { _persistState } = get()
      _persistState()
    },

    removeItem: (id: string) => {
      set((state) => {
        const itemToRemove = state.items.find(item => item.id === id)
        
        // Clean up blob URL if it exists
        if (itemToRemove?.previewURL && itemToRemove.previewURL.startsWith('blob:')) {
          URL.revokeObjectURL(itemToRemove.previewURL)
        }
        
        const newItems = state.items.filter(item => item.id !== id)
        
        return {
          ...state,
          items: newItems,
          isActive: newItems.length > 0
        }
      })

      // Persist state after removing item
      const { _persistState } = get()
      _persistState()
    },

    clearQueue: (filter?: (item: UploadItem) => boolean) => {
      set((state) => {
        const itemsToRemove = filter ? state.items.filter(filter) : state.items
        const itemsToKeep = filter ? state.items.filter(item => !filter(item)) : []
        
        // Clean up blob URLs for items being removed
        cleanupBlobURLs(itemsToRemove)
        
        return {
          ...state,
          items: itemsToKeep,
          isActive: itemsToKeep.length > 0
        }
      })
    },

    startItem: (id: string) => {
      const { updateItem } = get()
      const { items } = get()
      const item = items.find(item => item.id === id)
      
      if (item && (item.status === 'queued' || item.status === 'paused')) {
        updateItem(id, { 
          status: 'uploading',
          startedAt: new Date()
        })
      }
    },

    pauseItem: (id: string) => {
      const { updateItem } = get()
      const { items } = get()
      const item = items.find(item => item.id === id)
      
      if (item && item.status === 'uploading') {
        updateItem(id, { status: 'paused' })
      }
    },

    cancelItem: (id: string) => {
      const { updateItem } = get()
      const { items } = get()
      const item = items.find(item => item.id === id)
      
      if (item && ['queued', 'uploading', 'paused'].includes(item.status)) {
        updateItem(id, { 
          status: 'cancelled',
          completedAt: new Date()
        })
      }
    },

    retryItem: (id: string) => {
      const { updateItem } = get()
      const { items, settings } = get()
      const item = items.find(item => item.id === id)
      
      if (item && item.status === 'failed') {
        const newRetryCount = (item.retryCount || 0) + 1
        
        if (newRetryCount <= (item.maxRetries || settings.maxRetries)) {
          updateItem(id, { 
            status: 'queued',
            retryCount: newRetryCount,
            errorMessage: undefined,
            progress: 0
          })
        }
      }
    },

    startAll: () => {
      const { items, settings } = get()
      const queuedItems = items.filter(item => item.status === 'queued')
      const uploadingItems = items.filter(item => item.status === 'uploading')
      
      // Respect max concurrent uploads limit
      const availableSlots = Math.max(0, settings.maxConcurrentUploads - uploadingItems.length)
      const itemsToStart = queuedItems.slice(0, availableSlots)
      
      itemsToStart.forEach(item => {
        const { startItem } = get()
        startItem(item.id)
      })
      
      // Set queue as active and not paused
      set((state) => ({
        ...state,
        isActive: true,
        isPaused: false
      }))
    },

    pauseAll: () => {
      const { items } = get()
      const uploadingItems = items.filter(item => item.status === 'uploading')
      
      uploadingItems.forEach(item => {
        const { pauseItem } = get()
        pauseItem(item.id)
      })
      
      set((state) => ({
        ...state,
        isPaused: true
      }))
    },

    cancelAll: () => {
      const { items } = get()
      const activeItems = items.filter(item => 
        ['queued', 'uploading', 'paused'].includes(item.status)
      )
      
      activeItems.forEach(item => {
        const { cancelItem } = get()
        cancelItem(item.id)
      })
      
      set((state) => ({
        ...state,
        isPaused: false
      }))
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
      
      // Clear all storage data
      clearStorageData()
      
      // Reset to initial state
      set(getInitialState())
    },

    _cleanupBlobURLs: (itemIds: string[]) => {
      const { items } = get()
      const itemsToCleanup = items.filter(item => itemIds.includes(item.id))
      cleanupBlobURLs(itemsToCleanup)
    },

    clearPersistedItems: () => {
      try {
        sessionStorage.removeItem(STORAGE_KEYS.QUEUE_STATE)
        set((state) => ({
          ...state,
          persistedItems: []
        }))
      } catch (error) {
        console.warn('Failed to clear persisted items:', error)
      }
    },

    getPersistedItems: () => {
      const { persistedItems } = get()
      return persistedItems
    },

    _persistState: () => {
      const { items } = get()
      saveQueueStateToStorage(items)
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

// Get persisted queue items from previous sessions
export const usePersistedItems = () => 
  useUploadQueue(state => state.persistedItems)

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