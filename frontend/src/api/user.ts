/**
 * 用户管理接口。
 */
import { request } from '@/utils/request'
import type { MessageOut, PageResult, User } from '@/types/api'

/** 用户分页查询参数 */
export interface UserQuery {
  page?: number
  page_size?: number
  keyword?: string
}

/** 新增用户请求体 */
export interface UserForm {
  username: string
  password: string
  real_name: string
  role_id: number
  teacher_id?: number | null
  phone?: string | null
  email?: string | null
  status?: string
}

/** 用户分页列表 */
export function listUsers(params: UserQuery) {
  return request<PageResult<User>>({
    url: '/users',
    method: 'get',
    params
  })
}

/** 新增用户 */
export function createUser(data: UserForm) {
  return request<User>({
    url: '/users',
    method: 'post',
    data
  })
}

/** 修改用户 */
export function updateUser(id: number, data: Partial<UserForm>) {
  return request<User>({
    url: `/users/${id}`,
    method: 'put',
    data
  })
}

/** 重置用户密码 */
export function resetUserPassword(id: number, newPassword: string) {
  return request<MessageOut>({
    url: `/users/${id}/reset-password`,
    method: 'put',
    data: { new_password: newPassword }
  })
}

/** 删除用户 */
export function deleteUser(id: number) {
  return request<MessageOut>({
    url: `/users/${id}`,
    method: 'delete'
  })
}
