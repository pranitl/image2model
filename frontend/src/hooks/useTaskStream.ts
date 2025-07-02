import { useState, useEffect, useRef, useCallback } from 'react'

export interface TaskStatus {
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'error' | 'timeout' | 'cancelled' | 'retrying' | 'heartbeat'
  progress: number
  current?: number
  total?: number
  message: string
  task_id: string
  timestamp: number
  task_name?: string
  batch_id?: string
  job_id?: string
  eta_seconds?: number
  estimated_completion?: number
  error?: string
  error_type?: string
  recoverable?: boolean
  result?: any
  summary?: {
    total_files: number
    successful_files: number
    failed_files: number
  }
}

export interface TaskStreamOptions {
  timeout?: number
  autoReconnect?: boolean
  maxReconnectAttempts?: number
  reconnectInterval?: number
}

export interface TaskStreamState {
  status: TaskStatus | null
  isConnected: boolean
  isConnecting: boolean
  error: string | null
  connectionAttempts: number
}

export const useTaskStream = (
  taskId: string | null,
  options: TaskStreamOptions = {}
) => {
  const {
    timeout = 3600,
    autoReconnect = true,
    maxReconnectAttempts = 5,
    reconnectInterval = 2000
  } = options

  const [state, setState] = useState<TaskStreamState>({
    status: null,
    isConnected: false,
    isConnecting: false,
    error: null,
    connectionAttempts: 0
  })

  const eventSourceRef = useRef<EventSource | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const lastStatusRef = useRef<TaskStatus | null>(null)

  const updateState = useCallback((updates: Partial<TaskStreamState>) => {
    setState(prev => ({ ...prev, ...updates }))
  }, [])

  const connect = useCallback(() => {
    if (!taskId || eventSourceRef.current) {
      return
    }

    updateState({ isConnecting: true, error: null })

    try {
      const url = `/api/v1/status/tasks/${taskId}/stream?timeout=${timeout}`
      const eventSource = new EventSource(url)
      eventSourceRef.current = eventSource

      eventSource.onopen = () => {
        console.log(`SSE connected for task ${taskId}`)
        updateState({
          isConnected: true,
          isConnecting: false,
          connectionAttempts: 0,
          error: null
        })
      }

      eventSource.onerror = (event) => {
        console.error(`SSE error for task ${taskId}:`, event)
        updateState({
          isConnected: false,
          isConnecting: false,
          error: 'Connection error occurred'
        })

        // Don't reconnect if task is completed, failed, or cancelled
        const lastStatus = lastStatusRef.current
        const isTaskFinished = lastStatus && ['completed', 'failed', 'cancelled'].includes(lastStatus.status)
        
        // Auto-reconnect logic (but not for finished tasks)
        if (autoReconnect && !isTaskFinished && state.connectionAttempts < maxReconnectAttempts) {
          reconnectTimeoutRef.current = setTimeout(() => {
            updateState({ connectionAttempts: state.connectionAttempts + 1 })
            connect()
          }, reconnectInterval)
        }
      }

      // Handle different event types
      const handleTaskEvent = (event: MessageEvent) => {
        try {
          const data: TaskStatus = JSON.parse(event.data)
          lastStatusRef.current = data
          updateState({ status: data })
          
          // Automatically disconnect when task is finished
          if (['completed', 'failed', 'cancelled'].includes(data.status)) {
            console.log(`Task ${taskId} finished with status: ${data.status}. Disconnecting...`)
            setTimeout(() => disconnect(), 1000) // Small delay to ensure UI updates
          }
        } catch (err) {
          console.error('Failed to parse SSE data:', err)
        }
      }

      // Event type handlers
      eventSource.addEventListener('task_queued', handleTaskEvent)
      eventSource.addEventListener('task_progress', handleTaskEvent)
      eventSource.addEventListener('task_completed', handleTaskEvent)
      eventSource.addEventListener('task_failed', handleTaskEvent)
      eventSource.addEventListener('task_retry', handleTaskEvent)
      eventSource.addEventListener('task_cancelled', handleTaskEvent)
      eventSource.addEventListener('task_error', handleTaskEvent)
      eventSource.addEventListener('task_status', handleTaskEvent)
      
      eventSource.addEventListener('heartbeat', (event) => {
        try {
          const data = JSON.parse(event.data)
          console.log(`Heartbeat received for task ${taskId}:`, data.timestamp)
        } catch (err) {
          console.error('Failed to parse heartbeat data:', err)
        }
      })

      eventSource.addEventListener('connection_timeout', (event) => {
        try {
          const data = JSON.parse(event.data)
          updateState({
            error: data.message,
            isConnected: false
          })
          disconnect()
        } catch (err) {
          console.error('Failed to parse timeout data:', err)
        }
      })

      eventSource.addEventListener('stream_error', (event) => {
        try {
          const data = JSON.parse(event.data)
          updateState({
            error: data.error || 'Stream error occurred',
            isConnected: false
          })
          disconnect()
        } catch (err) {
          console.error('Failed to parse stream error data:', err)
        }
      })

    } catch (err) {
      console.error('Failed to create EventSource:', err)
      updateState({
        isConnected: false,
        isConnecting: false,
        error: 'Failed to establish connection'
      })
    }
  }, [taskId, timeout, autoReconnect, maxReconnectAttempts, reconnectInterval, state.connectionAttempts, updateState])

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    updateState({
      isConnected: false,
      isConnecting: false
    })
  }, [updateState])

  const reconnect = useCallback(() => {
    disconnect()
    updateState({ connectionAttempts: 0 })
    setTimeout(connect, 100)
  }, [disconnect, connect, updateState])

  // Effect to manage connection lifecycle
  useEffect(() => {
    if (taskId) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [taskId, connect, disconnect])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [disconnect])

  return {
    ...state,
    lastStatus: lastStatusRef.current,
    connect,
    disconnect,
    reconnect
  }
}

export default useTaskStream