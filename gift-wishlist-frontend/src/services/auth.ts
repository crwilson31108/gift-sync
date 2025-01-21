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
    this.setToken(access)
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
    this.clearTokens()
    delete api.defaults.headers.common['Authorization']
  },

  isAuthenticated(): boolean {
    const token = this.getToken()
    return Boolean(token && token.length > 0)
  },

  getToken(): string | null {
    return localStorage.getItem('token')
  },

  setToken(token: string): void {
    localStorage.setItem('token', token)
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  },

  clearTokens(): void {
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
  },

  async requestPasswordReset(email: string) {
    const { data } = await api.post('/password-reset/request_reset/', { email })
    return data
  },

  async resetPassword(userId: string, token: string, newPassword: string) {
    const { data } = await api.post('/password-reset/reset_password/', {
      user_id: userId,
      token,
      new_password: newPassword
    })
    return data
  },

  async validateToken(): Promise<User> {
    try {
      const token = this.getToken()
      if (!token) {
        throw new Error('No token found')
      }
      
      // Set token in headers if not already set
      if (!api.defaults.headers.common['Authorization']) {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      }
      
      const { data } = await api.get('/users/me/')
      return data
    } catch (error) {
      this.clearTokens()
      throw error
    }
  },

  // Add method to setup API with existing token
  setupApiWithToken(): void {
    const token = this.getToken()
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    }
  }
} 