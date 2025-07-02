import { apiRequest, api } from '@/utils/api'
import type { UploadJob, PaginatedResponse } from '@/types'

/**
 * Service for managing processing jobs
 */
export const jobService = {
  /**
   * Get a specific job by ID
   */
  getJob: async (jobId: string): Promise<UploadJob> => {
    const response = await apiRequest.get<UploadJob>(`/jobs/${jobId}`)
    
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to fetch job')
    }
    
    return response.data.data
  },

  /**
   * Get all jobs for the current user
   */
  getJobs: async (page: number = 1, pageSize: number = 10): Promise<PaginatedResponse<UploadJob>> => {
    const response = await apiRequest.get<PaginatedResponse<UploadJob>>(
      `/jobs?page=${page}&pageSize=${pageSize}`
    )
    
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to fetch jobs')
    }
    
    return response.data.data
  },

  /**
   * Cancel a processing job
   */
  cancelJob: async (jobId: string): Promise<void> => {
    const response = await apiRequest.post(`/jobs/${jobId}/cancel`)
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to cancel job')
    }
  },

  /**
   * Retry a failed job
   */
  retryJob: async (jobId: string): Promise<UploadJob> => {
    const response = await apiRequest.post<UploadJob>(`/jobs/${jobId}/retry`)
    
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to retry job')
    }
    
    return response.data.data
  },

  /**
   * Delete a job and its associated files
   */
  deleteJob: async (jobId: string): Promise<void> => {
    const response = await apiRequest.delete(`/jobs/${jobId}`)
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to delete job')
    }
  },

  /**
   * Download a generated model
   */
  downloadModel: async (jobId: string, modelId: string): Promise<Blob> => {
    const response = await api.get(`/jobs/${jobId}/models/${modelId}/download`, {
      responseType: 'blob',
    })
    
    return response.data
  },

  /**
   * Get job status (for polling)
   */
  getJobStatus: async (jobId: string): Promise<{ status: string; progress: number }> => {
    const response = await apiRequest.get<{ status: string; progress: number }>(
      `/jobs/${jobId}/status`
    )
    
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to fetch job status')
    }
    
    return response.data.data
  },
}