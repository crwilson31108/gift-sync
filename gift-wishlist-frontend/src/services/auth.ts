import api from './api'

export interface LoginCredentials {
  email: string
  password: string
}

export interface AuthResponse {
  access: string
  refresh: string
  user: {
    id: number
    username: string
    email: string
    profile_picture?: string
    bio?: string
  }
}

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await api.post('/token/', credentials)
    const { access, refresh } = response.data
    
    // Store tokens
    localStorage.setItem('token', access)
    localStorage.setItem('refreshToken', refresh)
    
    // Get user data
    const userResponse = await api.get('/users/me/')
    
    return {
      access,
      refresh,
      user: userResponse.data
    }
  },

  async logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('token')
  }
} 