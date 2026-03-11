import { defineStore } from 'pinia'
import { login as apiLogin, logout as apiLogout } from '../api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
    loading: false,
    error: null,
    unreadNotifications: 0
  }),
  getters: {
    isAuthenticated: (state) => state.token !== null,
    isAdmin: (state) => state.user?.role === 'admin',
    isCompany: (state) => state.user?.role === 'company',
    isStudent: (state) => state.user?.role === 'student',
    isApprovedCompany: (state) =>
      state.user?.role === 'company' && state.user?.approval_status === 'approved'
  },
  actions: {
    async login(email, password) {
      this.loading = true
      this.error = null
      try {
        const response = await apiLogin({ email, password })
        this.token = response.data.access_token
        this.user = response.data.user
        localStorage.setItem('access_token', this.token)
      } catch (err) {
        this.error = err.message || 'Login failed'
        throw err
      } finally {
        this.loading = false
      }
    },
    logout() {
      apiLogout().catch(() => {})
      this.token = null
      this.user = null
      this.error = null
      localStorage.removeItem('access_token')
    },
    initAuth() {
      const token = localStorage.getItem('access_token')
      if (!token) return

      try {
        // Decode JWT payload (no API call — avoids 401 race on page reload)
        const payloadBase64 = token.split('.')[1]
        const base64 = payloadBase64.replace(/-/g, '+').replace(/_/g, '/')
        const payload = JSON.parse(atob(base64))

        // Check expiry before trusting the token
        if (payload.exp && Date.now() / 1000 > payload.exp) {
          this.logout()
          return
        }

        const role = payload.role
        const email = payload.sub || ''
        const id = payload.id
        const username = email.split('@')[0]
        const defaultName = username ? username.charAt(0).toUpperCase() + username.slice(1) : ''

        this.token = token
        this.user = {
          id,
          email,
          role,
          name: defaultName,
          ...(payload.approval_status && { approval_status: payload.approval_status })
        }
      } catch {
        // Malformed token — clear it
        localStorage.removeItem('access_token')
      }
    }
  }
})
