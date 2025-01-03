import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true  // Important for CORS with credentials
})

// Add request interceptor to include token
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
  console.error('API Error:', error)
  return Promise.reject(error)
})

export default api 