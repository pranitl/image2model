/**
 * Unit tests for Upload Queue Zustand Store
 * 
 * Tests all store actions, state transitions, persistence logic,
 * and edge cases to ensure robustness and type safety.
 */

import { renderHook, act } from '@testing-library/react'
import { useUploadQueue, useQueueItems, useQueueStats, useQueueSettings, usePersistedItems } from '../uploadQueue'
import type { UploadItem, QueueSettings } from '../types'

// Mock sessionStorage
const mockSessionStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
}

Object.defineProperty(window, 'sessionStorage', {
  value: mockSessionStorage
})

// Mock URL.createObjectURL and revokeObjectURL
const mockCreateObjectURL = jest.fn(() => 'blob:mock-url')
const mockRevokeObjectURL = jest.fn()

Object.defineProperty(URL, 'createObjectURL', {
  value: mockCreateObjectURL
})

Object.defineProperty(URL, 'revokeObjectURL', {
  value: mockRevokeObjectURL
})

// Mock nanoid
jest.mock('nanoid', () => ({
  nanoid: jest.fn(() => 'mock-id-' + Math.random().toString(36).substr(2, 9))
}))

// Helper function to create mock files
const createMockFile = (name: string, size: number = 1024, type: string = 'image/jpeg'): File => {
  const file = new File(['mock content'], name, { type })
  Object.defineProperty(file, 'size', { value: size })
  return file
}

// Helper function to wait for async operations
const waitForAsync = () => new Promise(resolve => setTimeout(resolve, 0))

describe('Upload Queue Store', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockSessionStorage.getItem.mockReturnValue(null)
  })

  describe('Initial State', () => {
    it('should initialize with empty items and default settings', () => {
      const { result } = renderHook(() => useUploadQueue())

      expect(result.current.items).toEqual([])
      expect(result.current.isActive).toBe(false)
      expect(result.current.isPaused).toBe(false)
      expect(result.current.settings).toEqual({
        maxConcurrentUploads: 3,
        maxRetries: 3,
        autoStart: true,
        autoRemoveCompleted: 30000,
        autoRemoveFailed: 60000,
        defaultFaceLimit: 50000
      })
    })

    it('should load persisted settings from storage', () => {
      const mockSettings = {
        maxConcurrentUploads: 5,
        defaultFaceLimit: 100000
      }
      mockSessionStorage.getItem.mockImplementation((key) => {
        if (key === 'uploadQueue:settings') {
          return JSON.stringify(mockSettings)
        }
        if (key === 'uploadQueue:faceLimit') {
          return '75000'
        }
        return null
      })

      const { result } = renderHook(() => useUploadQueue())

      expect(result.current.settings.maxConcurrentUploads).toBe(5)
      expect(result.current.settings.defaultFaceLimit).toBe(75000)
    })

    it('should load persisted queue items', () => {
      const mockPersistedItems = [
        {
          id: 'persisted-1',
          filename: 'test.jpg',
          size: 1024,
          type: 'image/jpeg',
          status: 'completed',
          progress: 100,
          createdAt: new Date().toISOString()
        }
      ]

      mockSessionStorage.getItem.mockImplementation((key) => {
        if (key === 'uploadQueue:state') {
          return JSON.stringify({
            items: mockPersistedItems,
            timestamp: new Date().toISOString()
          })
        }
        return null
      })

      const { result } = renderHook(() => useUploadQueue())

      expect(result.current.persistedItems).toHaveLength(1)
      expect(result.current.persistedItems[0].filename).toBe('test.jpg')
    })
  })

  describe('Adding Files', () => {
    it('should add single file to queue', () => {
      const { result } = renderHook(() => useUploadQueue())
      const mockFile = createMockFile('test.jpg')

      act(() => {
        result.current.addFile(mockFile)
      })

      expect(result.current.items).toHaveLength(1)
      expect(result.current.items[0].file).toBe(mockFile)
      expect(result.current.items[0].status).toBe('queued')
      expect(result.current.items[0].progress).toBe(0)
      expect(result.current.isActive).toBe(true)
      expect(mockCreateObjectURL).toHaveBeenCalledWith(mockFile)
    })

    it('should add multiple files to queue', () => {
      const { result } = renderHook(() => useUploadQueue())
      const mockFiles = [
        createMockFile('test1.jpg'),
        createMockFile('test2.png')
      ]

      act(() => {
        result.current.addFiles(mockFiles)
      })

      expect(result.current.items).toHaveLength(2)
      expect(result.current.items[0].file.name).toBe('test1.jpg')
      expect(result.current.items[1].file.name).toBe('test2.png')
      expect(result.current.isActive).toBe(true)
    })

    it('should not add empty file array', () => {
      const { result } = renderHook(() => useUploadQueue())

      act(() => {
        result.current.addFiles([])
      })

      expect(result.current.items).toHaveLength(0)
      expect(result.current.isActive).toBe(false)
    })

    it('should add files with generation options', () => {
      const { result } = renderHook(() => useUploadQueue())
      const mockFile = createMockFile('test.jpg')
      const options = {
        quality: 'high' as const,
        outputFormat: 'gltf' as const,
        generateTextures: true,
        optimizeForPrinting: false
      }

      act(() => {
        result.current.addFile(mockFile, options)
      })

      expect(result.current.items[0].generationOptions).toEqual(options)
    })

    it('should persist state after adding files', () => {
      const { result } = renderHook(() => useUploadQueue())
      const mockFile = createMockFile('test.jpg')

      act(() => {
        result.current.addFile(mockFile)
      })

      expect(mockSessionStorage.setItem).toHaveBeenCalledWith(
        'uploadQueue:state',
        expect.stringContaining('"filename":"test.jpg"')
      )
    })
  })

  describe('Updating Items', () => {
    it('should update item properties', () => {
      const { result } = renderHook(() => useUploadQueue())
      const mockFile = createMockFile('test.jpg')

      act(() => {
        result.current.addFile(mockFile)
      })

      const itemId = result.current.items[0].id

      act(() => {
        result.current.updateItem(itemId, {
          status: 'uploading',
          progress: 50,
          uploadSpeed: 1024
        })
      })

      const updatedItem = result.current.items[0]
      expect(updatedItem.status).toBe('uploading')
      expect(updatedItem.progress).toBe(50)
      expect(updatedItem.uploadSpeed).toBe(1024)
      expect(updatedItem.startedAt).toBeInstanceOf(Date)
    })

    it('should update timestamps based on status changes', () => {
      const { result } = renderHook(() => useUploadQueue())
      const mockFile = createMockFile('test.jpg')

      act(() => {
        result.current.addFile(mockFile)
      })

      const itemId = result.current.items[0].id

      // Set to uploading - should set startedAt
      act(() => {
        result.current.updateItem(itemId, { status: 'uploading' })
      })

      expect(result.current.items[0].startedAt).toBeInstanceOf(Date)

      // Set to completed - should set completedAt
      act(() => {
        result.current.updateItem(itemId, { status: 'completed' })
      })

      expect(result.current.items[0].completedAt).toBeInstanceOf(Date)
    })

    it('should persist state after updating item', () => {
      const { result } = renderHook(() => useUploadQueue())
      const mockFile = createMockFile('test.jpg')

      act(() => {
        result.current.addFile(mockFile)
      })

      jest.clearAllMocks()

      act(() => {
        result.current.updateItem(result.current.items[0].id, { progress: 50 })
      })

      expect(mockSessionStorage.setItem).toHaveBeenCalledWith(
        'uploadQueue:state',
        expect.stringContaining('"progress":50')
      )
    })
  })

  describe('Removing Items', () => {
    it('should remove item from queue', () => {
      const { result } = renderHook(() => useUploadQueue())
      const mockFile = createMockFile('test.jpg')

      act(() => {
        result.current.addFile(mockFile)
      })

      const itemId = result.current.items[0].id

      act(() => {
        result.current.removeItem(itemId)
      })

      expect(result.current.items).toHaveLength(0)
      expect(result.current.isActive).toBe(false)
      expect(mockRevokeObjectURL).toHaveBeenCalled()
    })

    it('should clean up blob URLs when removing items', () => {
      const { result } = renderHook(() => useUploadQueue())
      const mockFile = createMockFile('test.jpg')

      act(() => {
        result.current.addFile(mockFile)
      })

      const itemId = result.current.items[0].id
      const previewURL = result.current.items[0].previewURL

      act(() => {
        result.current.removeItem(itemId)
      })

      expect(mockRevokeObjectURL).toHaveBeenCalledWith(previewURL)
    })

    it('should persist state after removing item', () => {
      const { result } = renderHook(() => useUploadQueue())
      const mockFile = createMockFile('test.jpg')

      act(() => {
        result.current.addFile(mockFile)
      })

      jest.clearAllMocks()

      act(() => {
        result.current.removeItem(result.current.items[0].id)
      })

      expect(mockSessionStorage.setItem).toHaveBeenCalledWith(
        'uploadQueue:state',
        expect.stringContaining('"items":[]')
      )
    })
  })

  describe('Clear Queue', () => {
    it('should clear all items', () => {
      const { result } = renderHook(() => useUploadQueue())
      const mockFiles = [
        createMockFile('test1.jpg'),
        createMockFile('test2.png')
      ]

      act(() => {
        result.current.addFiles(mockFiles)
      })

      act(() => {
        result.current.clearQueue()
      })

      expect(result.current.items).toHaveLength(0)
      expect(result.current.isActive).toBe(false)
      expect(mockRevokeObjectURL).toHaveBeenCalledTimes(2)
    })

    it('should clear items with filter', () => {
      const { result } = renderHook(() => useUploadQueue())
      const mockFiles = [
        createMockFile('test1.jpg'),
        createMockFile('test2.png')
      ]

      act(() => {
        result.current.addFiles(mockFiles)
      })

      // Update one item to completed
      act(() => {
        result.current.updateItem(result.current.items[0].id, { status: 'completed' })
      })

      // Clear only completed items
      act(() => {
        result.current.clearQueue(item => item.status === 'completed')
      })

      expect(result.current.items).toHaveLength(1)
      expect(result.current.items[0].status).toBe('queued')
    })
  })

  describe('Upload Control', () => {
    it('should start single item', () => {
      const { result } = renderHook(() => useUploadQueue())
      const mockFile = createMockFile('test.jpg')

      act(() => {
        result.current.addFile(mockFile)
      })

      const itemId = result.current.items[0].id

      act(() => {
        result.current.startItem(itemId)
      })

      expect(result.current.items[0].status).toBe('uploading')
      expect(result.current.items[0].startedAt).toBeInstanceOf(Date)
    })

    it('should pause item', () => {
      const { result } = renderHook(() => useUploadQueue())
      const mockFile = createMockFile('test.jpg')

      act(() => {
        result.current.addFile(mockFile)
      })

      const itemId = result.current.items[0].id

      act(() => {
        result.current.updateItem(itemId, { status: 'uploading' })
      })

      act(() => {
        result.current.pauseItem(itemId)
      })

      expect(result.current.items[0].status).toBe('paused')
    })

    it('should cancel item', () => {
      const { result } = renderHook(() => useUploadQueue())
      const mockFile = createMockFile('test.jpg')

      act(() => {
        result.current.addFile(mockFile)
      })

      const itemId = result.current.items[0].id

      act(() => {
        result.current.cancelItem(itemId)
      })

      expect(result.current.items[0].status).toBe('cancelled')
      expect(result.current.items[0].completedAt).toBeInstanceOf(Date)
    })

    it('should retry failed item', () => {
      const { result } = renderHook(() => useUploadQueue())
      const mockFile = createMockFile('test.jpg')

      act(() => {
        result.current.addFile(mockFile)
      })

      const itemId = result.current.items[0].id

      // Set item to failed
      act(() => {
        result.current.updateItem(itemId, { 
          status: 'failed', 
          errorMessage: 'Upload failed',
          retryCount: 1
        })
      })

      act(() => {
        result.current.retryItem(itemId)
      })

      const item = result.current.items[0]
      expect(item.status).toBe('queued')
      expect(item.retryCount).toBe(2)
      expect(item.errorMessage).toBeUndefined()
      expect(item.progress).toBe(0)
    })

    it('should not retry item beyond max retries', () => {
      const { result } = renderHook(() => useUploadQueue())
      const mockFile = createMockFile('test.jpg')

      act(() => {
        result.current.addFile(mockFile)
      })

      const itemId = result.current.items[0].id

      // Set item to failed with max retries reached
      act(() => {
        result.current.updateItem(itemId, { 
          status: 'failed', 
          retryCount: 3,
          maxRetries: 3
        })
      })

      act(() => {
        result.current.retryItem(itemId)
      })

      expect(result.current.items[0].status).toBe('failed')
      expect(result.current.items[0].retryCount).toBe(3)
    })
  })

  describe('Bulk Operations', () => {
    it('should start all queued items', () => {
      const { result } = renderHook(() => useUploadQueue())
      const mockFiles = [
        createMockFile('test1.jpg'),
        createMockFile('test2.png'),
        createMockFile('test3.gif')
      ]

      act(() => {
        result.current.addFiles(mockFiles)
      })

      act(() => {
        result.current.startAll()
      })

      const uploadingItems = result.current.items.filter(item => item.status === 'uploading')
      expect(uploadingItems).toHaveLength(3) // All items within max concurrent limit
      expect(result.current.isActive).toBe(true)
      expect(result.current.isPaused).toBe(false)
    })

    it('should respect max concurrent uploads limit', () => {
      const { result } = renderHook(() => useUploadQueue())
      
      // Set max concurrent uploads to 2
      act(() => {
        result.current.updateSettings({ maxConcurrentUploads: 2 })
      })

      const mockFiles = [
        createMockFile('test1.jpg'),
        createMockFile('test2.png'),
        createMockFile('test3.gif')
      ]

      act(() => {
        result.current.addFiles(mockFiles)
      })

      act(() => {
        result.current.startAll()
      })

      const uploadingItems = result.current.items.filter(item => item.status === 'uploading')
      const queuedItems = result.current.items.filter(item => item.status === 'queued')
      
      expect(uploadingItems).toHaveLength(2)
      expect(queuedItems).toHaveLength(1)
    })

    it('should pause all uploading items', () => {
      const { result } = renderHook(() => useUploadQueue())
      const mockFiles = [
        createMockFile('test1.jpg'),
        createMockFile('test2.png')
      ]

      act(() => {
        result.current.addFiles(mockFiles)
      })

      act(() => {
        result.current.startAll()
      })

      act(() => {
        result.current.pauseAll()
      })

      const pausedItems = result.current.items.filter(item => item.status === 'paused')
      expect(pausedItems).toHaveLength(2)
      expect(result.current.isPaused).toBe(true)
    })

    it('should cancel all active items', () => {
      const { result } = renderHook(() => useUploadQueue())
      const mockFiles = [
        createMockFile('test1.jpg'),
        createMockFile('test2.png')
      ]

      act(() => {
        result.current.addFiles(mockFiles)
      })

      act(() => {
        result.current.startAll()
      })

      act(() => {
        result.current.cancelAll()
      })

      const cancelledItems = result.current.items.filter(item => item.status === 'cancelled')
      expect(cancelledItems).toHaveLength(2)
      expect(result.current.isPaused).toBe(false)
    })
  })

  describe('Statistics', () => {
    it('should calculate queue statistics correctly', () => {
      const { result } = renderHook(() => useUploadQueue())
      const mockFiles = [
        createMockFile('test1.jpg', 1000),
        createMockFile('test2.png', 2000),
        createMockFile('test3.gif', 3000)
      ]

      act(() => {
        result.current.addFiles(mockFiles)
      })

      // Update item statuses
      act(() => {
        result.current.updateItem(result.current.items[0].id, { status: 'completed', progress: 100 })
        result.current.updateItem(result.current.items[1].id, { status: 'uploading', progress: 50 })
        // Leave third item as queued
      })

      const stats = result.current.getStats()

      expect(stats.total).toBe(3)
      expect(stats.completed).toBe(1)
      expect(stats.uploading).toBe(1)
      expect(stats.queued).toBe(1)
      expect(stats.totalBytes).toBe(6000)
      expect(stats.uploadedBytes).toBe(2000) // 100% of 1000 + 50% of 2000
      expect(stats.overallProgress).toBe(33) // 2000 / 6000 * 100, rounded
    })
  })

  describe('Settings Management', () => {
    it('should update settings', () => {
      const { result } = renderHook(() => useUploadQueue())

      act(() => {
        result.current.updateSettings({
          maxConcurrentUploads: 5,
          autoStart: false,
          defaultFaceLimit: 100000
        })
      })

      expect(result.current.settings.maxConcurrentUploads).toBe(5)
      expect(result.current.settings.autoStart).toBe(false)
      expect(result.current.settings.defaultFaceLimit).toBe(100000)
    })

    it('should persist settings to storage', () => {
      const { result } = renderHook(() => useUploadQueue())

      act(() => {
        result.current.updateSettings({ maxConcurrentUploads: 5 })
      })

      expect(mockSessionStorage.setItem).toHaveBeenCalledWith(
        'uploadQueue:settings',
        expect.stringContaining('"maxConcurrentUploads":5')
      )
    })

    it('should persist face limit separately', () => {
      const { result } = renderHook(() => useUploadQueue())

      act(() => {
        result.current.updateSettings({ defaultFaceLimit: 75000 })
      })

      expect(mockSessionStorage.setItem).toHaveBeenCalledWith(
        'uploadQueue:faceLimit',
        '75000'
      )
    })
  })

  describe('Persistence Logic', () => {
    it('should clear persisted items', () => {
      const { result } = renderHook(() => useUploadQueue())

      act(() => {
        result.current.clearPersistedItems()
      })

      expect(mockSessionStorage.removeItem).toHaveBeenCalledWith('uploadQueue:state')
      expect(result.current.persistedItems).toEqual([])
    })

    it('should get persisted items', () => {
      const mockPersistedItems = [
        { id: '1', filename: 'test.jpg', status: 'completed', createdAt: new Date() }
      ]
      
      const { result } = renderHook(() => useUploadQueue())
      
      // Manually set persisted items for testing
      act(() => {
        result.current.clearPersistedItems()
      })

      const persistedItems = result.current.getPersistedItems()
      expect(persistedItems).toEqual([])
    })
  })

  describe('Reset Functionality', () => {
    it('should reset queue to initial state', () => {
      const { result } = renderHook(() => useUploadQueue())
      const mockFiles = [
        createMockFile('test1.jpg'),
        createMockFile('test2.png')
      ]

      act(() => {
        result.current.addFiles(mockFiles)
        result.current.updateSettings({ maxConcurrentUploads: 10 })
      })

      act(() => {
        result.current.reset()
      })

      expect(result.current.items).toHaveLength(0)
      expect(result.current.isActive).toBe(false)
      expect(result.current.isPaused).toBe(false)
      expect(mockRevokeObjectURL).toHaveBeenCalledTimes(2)
      expect(mockSessionStorage.removeItem).toHaveBeenCalledTimes(3) // All storage keys
    })
  })

  describe('Selector Hooks', () => {
    it('should provide queue items selector', () => {
      const { result: storeResult } = renderHook(() => useUploadQueue())
      const { result: itemsResult } = renderHook(() => useQueueItems())
      const mockFile = createMockFile('test.jpg')

      act(() => {
        storeResult.current.addFile(mockFile)
      })

      expect(itemsResult.current).toHaveLength(1)
      expect(itemsResult.current[0].file.name).toBe('test.jpg')
    })

    it('should provide queue stats selector', () => {
      const { result: storeResult } = renderHook(() => useUploadQueue())
      const { result: statsResult } = renderHook(() => useQueueStats())
      const mockFile = createMockFile('test.jpg', 1000)

      act(() => {
        storeResult.current.addFile(mockFile)
      })

      expect(statsResult.current.total).toBe(1)
      expect(statsResult.current.queued).toBe(1)
      expect(statsResult.current.totalBytes).toBe(1000)
    })

    it('should provide queue settings selector', () => {
      const { result: storeResult } = renderHook(() => useUploadQueue())
      const { result: settingsResult } = renderHook(() => useQueueSettings())

      act(() => {
        storeResult.current.updateSettings({ maxConcurrentUploads: 7 })
      })

      expect(settingsResult.current.maxConcurrentUploads).toBe(7)
    })

    it('should provide persisted items selector', () => {
      const { result } = renderHook(() => usePersistedItems())
      
      expect(result.current).toEqual([])
    })
  })

  describe('Error Handling', () => {
    it('should handle storage errors gracefully', () => {
      mockSessionStorage.setItem.mockImplementation(() => {
        throw new Error('Storage quota exceeded')
      })

      const { result } = renderHook(() => useUploadQueue())
      const mockFile = createMockFile('test.jpg')

      // Should not throw
      act(() => {
        result.current.addFile(mockFile)
      })

      expect(result.current.items).toHaveLength(1)
    })

    it('should handle invalid stored data gracefully', () => {
      mockSessionStorage.getItem.mockImplementation((key) => {
        if (key === 'uploadQueue:settings') {
          return 'invalid-json'
        }
        return null
      })

      // Should not throw and use defaults
      const { result } = renderHook(() => useUploadQueue())

      expect(result.current.settings.maxConcurrentUploads).toBe(3)
    })
  })
})