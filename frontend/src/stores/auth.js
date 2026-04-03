import { defineStore } from 'pinia'
import http, { TOKEN_KEY, USER_KEY } from '../lib/http'

function readStoredUser() {
  const raw = localStorage.getItem(USER_KEY)

  if (!raw) {
    return null
  }

  try {
    return JSON.parse(raw)
  } catch {
    localStorage.removeItem(USER_KEY)
    return null
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || '',
    user: readStoredUser(),
    loading: false,
    bootstrapping: false,
    initialized: false,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token && !!state.user,
  },

  actions: {
    setAuth(token, user) {
      this.token = token
      this.user = user

      localStorage.setItem(TOKEN_KEY, token)
      localStorage.setItem(USER_KEY, JSON.stringify(user))
    },

    setUser(user) {
      this.user = user
      localStorage.setItem(USER_KEY, JSON.stringify(user))
    },

    clearAuth() {
      this.token = ''
      this.user = null

      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
    },

    async login(identifier, password) {
      this.loading = true

      try {
        const response = await http.post('/auth/login', {
          identifier,
          password,
        })

        const data = response.data
        this.setAuth(data.access_token, data.user)

        return data
      } finally {
        this.loading = false
      }
    },

    async fetchMe() {
      const response = await http.get('/users/me')
      this.setUser(response.data)
      return response.data
    },

    async initializeAuth() {
      if (this.initialized) {
        return
      }

      this.bootstrapping = true

      try {
        if (!this.token) {
          this.clearAuth()
          return
        }

        await this.fetchMe()
      } catch (error) {
        this.clearAuth()
      } finally {
        this.bootstrapping = false
        this.initialized = true
      }
    },

    logout() {
      this.clearAuth()
    },
  },
})
