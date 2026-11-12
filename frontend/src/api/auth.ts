/**
 * 认证相关接口。
 */
import { request } from '@/utils/request'
import type {
  LoginRequest,
  LoginResponse,
  MessageOut,
  UserProfile
} from '@/types/api'

/** 用户登录 */
export function login(data: LoginRequest) {
  return request<LoginResponse>({
    url: '/auth/login',
    method: 'post',
    data
  })
}

/** 获取当前登录用户信息 */
export function getProfile() {
  return request<UserProfile>({
    url: '/auth/profile',
    method: 'get'
  })
}

/** 修改密码 */
export function changePassword(data: { old_password: string; new_password: string }) {
  return request<MessageOut>({
    url: '/auth/change-password',
    method: 'post',
    data
  })
}
