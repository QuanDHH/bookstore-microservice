import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

// Attach access token to every request
api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('access_token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

// Auto-refresh on 401
api.interceptors.response.use(
  r => r,
  async err => {
    const orig = err.config
    if (err.response?.status === 401 && !orig._retry) {
      orig._retry = true
      try {
        const refresh = localStorage.getItem('refresh_token')
        const { data } = await axios.post('/api/customers/token/refresh/', { refresh })
        localStorage.setItem('access_token', data.access)
        orig.headers.Authorization = `Bearer ${data.access}`
        return api(orig)
      } catch {
        localStorage.clear()
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

// ── Customer auth ─────────────────────────────────────────────────────────────
export const customerRegister = d => api.post('/customers/register/', d)
export const customerLogin    = d => api.post('/customers/login/', d)
export const getProfile       = ()  => api.get('/customers/profile/')

// ── Staff auth ────────────────────────────────────────────────────────────────
export const staffRegister = d => api.post('/staff/register/', d)
export const staffLogin    = d => api.post('/staff/login/', d)

// ── Products ──────────────────────────────────────────────────────────────────
export const getLaptops  = params => api.get('/laptops/', { params })
export const getClothes  = params => api.get('/clothes/', { params })
export const createLaptop  = d => api.post('/staff/products/laptops/', d)
export const updateLaptop  = (id, d) => api.patch(`/staff/products/laptops/${id}/`, d)
export const createClothes = d => api.post('/staff/products/clothes/', d)
export const updateClothes = (id, d) => api.patch(`/staff/products/clothes/${id}/`, d)

// ── Cart ──────────────────────────────────────────────────────────────────────
export const getCart     = id  => api.get(`/carts/${id}/`)
export const addToCart   = (id, d) => api.post(`/carts/${id}/add/`, d)
export const removeFromCart = (id, d) => api.delete(`/carts/${id}/remove/`, { data: d })

export default api