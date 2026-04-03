import axios from 'axios'

export const TOKEN_KEY = 'mango_talk_token'
export const USER_KEY = 'mango_talk_user'

const http = axios.create({
  baseURL: '',
  timeout: 10000,
})

http.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_KEY)

    if (token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => Promise.reject(error)
)

export default http
