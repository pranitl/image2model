import axios, { AxiosError, AxiosResponse } from 'axios'
import type { ApiResponse, ApiError } from '@/types'

// Determine the correct API base URL
const getApiBaseURL = () => {
  // If we're in development and accessing from host machine, use direct backend URL
  if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    return 'http://localhost:8000/api'
  }
  // Otherwise use the proxy
  return '/api'
}

// Create axios instance with default config
export const api = axios.create({
  baseURL: getApiBaseURL(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    return response
  },
  (error: AxiosError<ApiError>) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API helper functions
export const apiRequest = {
  get: <T>(url: string) => api.get<ApiResponse<T>>(url),
  post: <T>(url: string, data?: any) => api.post<ApiResponse<T>>(url, data),
  put: <T>(url: string, data?: any) => api.put<ApiResponse<T>>(url, data),
  delete: <T>(url: string) => api.delete<ApiResponse<T>>(url),
  upload: <T>(url: string, formData: FormData, onProgress?: (progress: number) => void) => {
    return api.post<ApiResponse<T>>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })
  },
}

// Error handling utility
export const handleApiError = (error: AxiosError<ApiError>): string => {
  if (error.response?.data?.message) {
    return error.response.data.message
  }
  if (error.message) {
    return error.message
  }
  return 'An unexpected error occurred'
}