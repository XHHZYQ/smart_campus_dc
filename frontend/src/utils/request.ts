/**
 * Axios 统一封装。
 * - 请求拦截：自动携带 JWT 令牌
 * - 响应拦截：直接返回业务数据，统一处理错误提示
 */
import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'

const TOKEN_KEY = 'smart_campus_token'

export function getToken(): string {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

const service: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000
})

service.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

service.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const status = error?.response?.status
    const detail = error?.response?.data?.detail
    const text = typeof detail === 'string' ? detail : '请求失败，请稍后重试'

    if (status === 401) {
      removeToken()
      ElMessage.error(text)
      // 已经在登录页就不跳转，避免整页刷新把刚弹出的错误提示抹掉
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    } else {
      ElMessage.error(text)
    }
    return Promise.reject(error)
  }
)

/** 通用请求方法：泛型指定返回类型 */
export function request<T>(config: AxiosRequestConfig): Promise<T> {
  return service.request<unknown, T>(config)
}

export default service
