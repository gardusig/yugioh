// API configuration
const API_BASE = import.meta.env.VITE_API_BASE || (import.meta.env.DEV ? 'http://localhost:8080' : '/api')

export const getApiUrl = (endpoint) => {
  if (import.meta.env.DEV) {
    return `${API_BASE}${endpoint}`
  }
  return `/api${endpoint}`
}

