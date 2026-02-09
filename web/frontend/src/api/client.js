import axios from 'axios'

// Helper function to get CSRF token from cookies
function getCsrfToken() {
  const name = 'csrf_token='
  const decodedCookie = decodeURIComponent(document.cookie)
  const cookieArray = decodedCookie.split(';')

  for (let cookie of cookieArray) {
    cookie = cookie.trim()
    if (cookie.indexOf(name) === 0) {
      return cookie.substring(name.length)
    }
  }
  return null
}

const client = axios.create({
  baseURL: import.meta.env.DEV ? 'http://localhost:5555/api' : '/api',  // Updated to port 5555
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true  // Required to send/receive cookies for CSRF
})

// Request interceptor - Add CSRF token to state-changing requests
client.interceptors.request.use(
  (config) => {
    // Add CSRF token for POST, PUT, DELETE, PATCH requests
    if (['post', 'put', 'delete', 'patch'].includes(config.method.toLowerCase())) {
      const csrfToken = getCsrfToken()
      if (csrfToken) {
        config.headers['X-CSRF-Token'] = csrfToken
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
client.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export default client
