import { vi } from 'vitest'

// Mock window.matchMedia for responsive tests
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock EventSource for SSE tests
global.EventSource = vi.fn().mockImplementation(() => ({
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  close: vi.fn(),
  readyState: 1, // OPEN
  CONNECTING: 0,
  OPEN: 1,
  CLOSED: 2,
}))

// Mock File API
global.File = class File {
  constructor(fileBits: any[], fileName: string, options: any = {}) {
    return {
      name: fileName,
      size: fileBits.join('').length,
      type: options.type || '',
      lastModified: Date.now(),
    } as File
  }
} as any

// Mock FormData
global.FormData = class FormData {
  private data = new Map<string, any[]>()
  
  append(key: string, value: any) {
    if (!this.data.has(key)) {
      this.data.set(key, [])
    }
    this.data.get(key)!.push(value)
  }
  
  get(key: string) {
    const values = this.data.get(key)
    return values ? values[0] : null
  }
  
  getAll(key: string) {
    return this.data.get(key) || []
  }
} as any