import axios from 'axios'

const BASE = import.meta.env.VITE_API_BASE_URL  // e.g. http://127.0.0.1:8000/api
console.log("✅ API Base URL:", BASE)

const http = axios.create({
  baseURL: BASE,
  withCredentials: false,
})

// ✅ Attach token to private endpoints
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')

  // define public routes
  const publicEndpoints = ['/auth/login/', '/auth/register/', '/auth/password/reset/']
  const isPublic = publicEndpoints.some((endpoint) => config.url?.includes(endpoint))

  if (!isPublic && token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

export default http
