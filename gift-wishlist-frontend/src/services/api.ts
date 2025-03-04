import axios from 'axios'
import { useAppStore } from '@/stores/useAppStore'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: true
})

// Add request interceptor to handle auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, (error) => {
  return Promise.reject(error)
})

// Add response interceptor to handle errors
api.interceptors.response.use((response) => {
  return response
}, (error) => {
  // Handle token expiration
  if (error.response && (error.response.status === 401 || error.response.status === 403)) {
    // Check if the error is due to token expiration
    const errorMessage = error.response.data?.detail || ''
    if (
      errorMessage.includes('expired') || 
      errorMessage.includes('invalid') || 
      errorMessage.includes('not provided') ||
      errorMessage.includes('authentication')
    ) {
      console.log('Token expired or invalid, redirecting to login')
      
      // Clear user data
      const appStore = useAppStore()
      appStore.logout()
      
      // Redirect to login
      window.location.href = '/login'
    }
  }
  console.error('API Error:', error)
  return Promise.reject(error)
})

export default api 