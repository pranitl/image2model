/**
 * Validation utilities for forms and inputs
 */

export const VALIDATION_RULES = {
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/jpg', 'image/png'],
  MAX_FILES_COUNT: 25,
  MIN_IMAGE_DIMENSION: 100,
  MAX_IMAGE_DIMENSION: 4096,
} as const

/**
 * Validate if file is a valid image
 */
export const validateImageFile = (file: File): { isValid: boolean; error?: string } => {
  // Check file type
  if (!VALIDATION_RULES.ALLOWED_IMAGE_TYPES.includes(file.type as any)) {
    return {
      isValid: false,
      error: 'Please upload a valid image file (JPEG or PNG)',
    }
  }

  // Check file size
  if (file.size > VALIDATION_RULES.MAX_FILE_SIZE) {
    return {
      isValid: false,
      error: `File size must be less than ${VALIDATION_RULES.MAX_FILE_SIZE / (1024 * 1024)}MB`,
    }
  }

  return { isValid: true }
}

/**
 * Validate multiple image files
 */
export const validateImageFiles = (files: File[]): { isValid: boolean; errors: string[] } => {
  const errors: string[] = []

  // Check files count
  if (files.length === 0) {
    errors.push('Please select at least one image')
  }

  if (files.length > VALIDATION_RULES.MAX_FILES_COUNT) {
    errors.push(`Maximum ${VALIDATION_RULES.MAX_FILES_COUNT} images allowed`)
  }

  // Validate each file
  files.forEach((file, index) => {
    const validation = validateImageFile(file)
    if (!validation.isValid) {
      errors.push(`File ${index + 1}: ${validation.error}`)
    }
  })

  return {
    isValid: errors.length === 0,
    errors,
  }
}

/**
 * Validate image dimensions (requires image element)
 */
export const validateImageDimensions = (
  image: HTMLImageElement
): { isValid: boolean; error?: string } => {
  const { width, height } = image

  if (width < VALIDATION_RULES.MIN_IMAGE_DIMENSION || height < VALIDATION_RULES.MIN_IMAGE_DIMENSION) {
    return {
      isValid: false,
      error: `Image dimensions must be at least ${VALIDATION_RULES.MIN_IMAGE_DIMENSION}x${VALIDATION_RULES.MIN_IMAGE_DIMENSION} pixels`,
    }
  }

  if (width > VALIDATION_RULES.MAX_IMAGE_DIMENSION || height > VALIDATION_RULES.MAX_IMAGE_DIMENSION) {
    return {
      isValid: false,
      error: `Image dimensions must not exceed ${VALIDATION_RULES.MAX_IMAGE_DIMENSION}x${VALIDATION_RULES.MAX_IMAGE_DIMENSION} pixels`,
    }
  }

  return { isValid: true }
}

/**
 * Validate email format
 */
export const validateEmail = (email: string): { isValid: boolean; error?: string } => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  
  if (!email) {
    return { isValid: false, error: 'Email is required' }
  }
  
  if (!emailRegex.test(email)) {
    return { isValid: false, error: 'Please enter a valid email address' }
  }
  
  return { isValid: true }
}

/**
 * Validate required field
 */
export const validateRequired = (value: string, fieldName: string): { isValid: boolean; error?: string } => {
  if (!value || value.trim().length === 0) {
    return { isValid: false, error: `${fieldName} is required` }
  }
  
  return { isValid: true }
}

/**
 * Validate string length
 */
export const validateLength = (
  value: string,
  min: number,
  max: number,
  fieldName: string
): { isValid: boolean; error?: string } => {
  if (value.length < min) {
    return { isValid: false, error: `${fieldName} must be at least ${min} characters` }
  }
  
  if (value.length > max) {
    return { isValid: false, error: `${fieldName} must not exceed ${max} characters` }
  }
  
  return { isValid: true }
}

/**
 * Get file extension from filename
 */
export const getFileExtension = (filename: string): string => {
  return filename.split('.').pop()?.toLowerCase() || ''
}

/**
 * Check if file type is supported
 */
export const isImageTypeSupported = (mimeType: string): boolean => {
  return VALIDATION_RULES.ALLOWED_IMAGE_TYPES.includes(mimeType as any)
}