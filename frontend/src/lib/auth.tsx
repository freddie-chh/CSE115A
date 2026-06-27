import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { authApi } from './api'
import type { Profile } from './types'

interface AuthContextValue {
  user: Profile | null
  token: string | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<Profile | null>(null)
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('access_token'),
  )
  const [loading, setLoading] = useState(true)

  const fetchProfile = useCallback(async () => {
    const stored = localStorage.getItem('access_token')
    if (!stored) {
      setLoading(false)
      return
    }
    try {
      const { data } = await authApi.me()
      setUser(data)
      setToken(stored)
    } catch {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_email')
      setToken(null)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchProfile()
  }, [fetchProfile])

  const login = async (email: string, password: string) => {
    const { data } = await authApi.login(email, password)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('user_email', data.email)
    setToken(data.access_token)
    setUser({ id: data.user_id, email: data.email })
  }

  const register = async (email: string, password: string) => {
    const { data } = await authApi.register(email, password)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('user_email', data.email)
    setToken(data.access_token)
    setUser({ id: data.user_id, email: data.email })
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } catch {
      // ignore
    }
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_email')
    setToken(null)
    setUser(null)
  }

  const value = useMemo(
    () => ({ user, token, loading, login, register, logout }),
    [user, token, loading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
