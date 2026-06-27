import axios from 'axios'
import type {
  AuthResponse,
  BacktestResult,
  OHLCVBar,
  Profile,
  Strategy,
  StrategyFormData,
  Timeframe,
} from './types'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_email')
      if (!window.location.pathname.startsWith('/login') && !window.location.pathname.startsWith('/register')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

export const authApi = {
  register: (email: string, password: string) =>
    api.post<AuthResponse>('/auth/register', { email, password }),
  login: (email: string, password: string) =>
    api.post<AuthResponse>('/auth/login', { email, password }),
  logout: () => api.post('/auth/logout'),
  me: () => api.get<Profile>('/me'),
}

export const marketApi = {
  getData: (ticker: string, timeframe: Timeframe) =>
    api.get<{ ticker: string; timeframe: string; data: OHLCVBar[] }>(
      `/market-data/${ticker}`,
      { params: { timeframe } },
    ),
}

export const strategyApi = {
  list: () => api.get<Strategy[]>('/strategies'),
  get: (id: string) => api.get<Strategy>(`/strategies/${id}`),
  create: (data: StrategyFormData) => api.post<Strategy>('/strategies', data),
  update: (id: string, data: StrategyFormData) =>
    api.put<Strategy>(`/strategies/${id}`, data),
  delete: (id: string) => api.delete(`/strategies/${id}`),
}

export const backtestApi = {
  run: (payload: { strategy_id?: string } & Partial<StrategyFormData>) =>
    api.post<BacktestResult>('/backtest', payload),
  get: (id: string) => api.get<BacktestResult>(`/backtests/${id}`),
}

export default api
