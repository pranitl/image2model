/**
 * Integration test for useTaskStream hook to verify connection error fix
 */

import { renderHook, act } from '@testing-library/react'
import { useTaskStream } from '../useTaskStream'

// Mock EventSource
const mockEventSource = {
  addEventListener: jest.fn(),
  close: jest.fn(),
  readyState: 1,
  url: '',
  withCredentials: false,
  CONNECTING: 0,
  OPEN: 1,
  CLOSED: 2,
  onopen: null,
  onmessage: null,
  onerror: null,
  dispatchEvent: jest.fn()
}

const mockEventSourceConstructor = jest.fn(() => mockEventSource)

// Mock EventSource globally
Object.defineProperty(window, 'EventSource', {
  writable: true,
  value: mockEventSourceConstructor
})

describe('useTaskStream connection error fix', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should not show connection error when task completes successfully', () => {
    const { result } = renderHook(() => useTaskStream('test-task-id'))

    // Simulate connection opening
    act(() => {
      const onOpenCallback = mockEventSource.addEventListener.mock.calls.find(
        call => call[0] === 'task_completed'
      )?.[1]

      if (onOpenCallback) {
        onOpenCallback({
          data: JSON.stringify({
            status: 'completed',
            progress: 100,
            message: 'Task completed successfully',
            task_id: 'test-task-id'
          })
        } as MessageEvent)
      }
    })

    // Wait for disconnection timeout
    act(() => {
      jest.runAllTimers()
    })

    // Simulate EventSource error event (which happens when connection closes)
    act(() => {
      if (mockEventSource.onerror) {
        mockEventSource.onerror(new Event('error'))
      }
    })

    // Verify that no error is shown for completed task
    expect(result.current.error).toBeNull()
    expect(result.current.isConnected).toBe(false)
    expect(result.current.status?.status).toBe('completed')
  })

  it('should show connection error when task is processing and real error occurs', () => {
    const { result } = renderHook(() => useTaskStream('test-task-id'))

    // Simulate task processing
    act(() => {
      const onProgressCallback = mockEventSource.addEventListener.mock.calls.find(
        call => call[0] === 'task_progress'
      )?.[1]

      if (onProgressCallback) {
        onProgressCallback({
          data: JSON.stringify({
            status: 'processing',
            progress: 50,
            message: 'Processing...',
            task_id: 'test-task-id'
          })
        } as MessageEvent)
      }
    })

    // Simulate real connection error during processing
    act(() => {
      if (mockEventSource.onerror) {
        mockEventSource.onerror(new Event('error'))
      }
    })

    // Verify that error is shown for processing task
    expect(result.current.error).toBe('Connection error occurred')
    expect(result.current.isConnected).toBe(false)
    expect(result.current.status?.status).toBe('processing')
  })

  it('should not show connection error when task fails and connection closes', () => {
    const { result } = renderHook(() => useTaskStream('test-task-id'))

    // Simulate task failure
    act(() => {
      const onFailedCallback = mockEventSource.addEventListener.mock.calls.find(
        call => call[0] === 'task_failed'
      )?.[1]

      if (onFailedCallback) {
        onFailedCallback({
          data: JSON.stringify({
            status: 'failed',
            progress: 0,
            message: 'Task failed',
            task_id: 'test-task-id',
            error: 'Processing error'
          })
        } as MessageEvent)
      }
    })

    // Wait for disconnection timeout
    act(() => {
      jest.runAllTimers()
    })

    // Simulate EventSource error event (which happens when connection closes)
    act(() => {
      if (mockEventSource.onerror) {
        mockEventSource.onerror(new Event('error'))
      }
    })

    // Verify that no connection error is shown for failed task (task error is separate)
    expect(result.current.error).toBeNull()
    expect(result.current.isConnected).toBe(false)
    expect(result.current.status?.status).toBe('failed')
  })

  it('should clear error when reconnecting manually', () => {
    const { result } = renderHook(() => useTaskStream('test-task-id'))

    // Simulate connection error during processing
    act(() => {
      const onProgressCallback = mockEventSource.addEventListener.mock.calls.find(
        call => call[0] === 'task_progress'
      )?.[1]

      if (onProgressCallback) {
        onProgressCallback({
          data: JSON.stringify({
            status: 'processing',
            progress: 25,
            message: 'Processing...',
            task_id: 'test-task-id'
          })
        } as MessageEvent)
      }
    })

    act(() => {
      if (mockEventSource.onerror) {
        mockEventSource.onerror(new Event('error'))
      }
    })

    // Verify error is present
    expect(result.current.error).toBe('Connection error occurred')

    // Manually reconnect
    act(() => {
      result.current.reconnect()
    })

    // Verify error is cleared
    expect(result.current.error).toBeNull()
    expect(result.current.connectionAttempts).toBe(0)
  })
})