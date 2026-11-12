/**
 * 角色管理接口。
 */
import { request } from '@/utils/request'
import type { MessageOut, OptionItem, PageResult, Role } from '@/types/api'

/** 角色分页查询参数 */
export interface RoleQuery {
  page?: number
  page_size?: number
  keyword?: string
}

/** 角色分页列表 */
export function listRoles(params: RoleQuery) {
  return request<PageResult<Role>>({
    url: '/roles',
    method: 'get',
    params
  })
}

/** 角色下拉选项 */
export function listRoleOptions() {
  return request<OptionItem[]>({
    url: '/roles/options',
    method: 'get'
  })
}

/** 新增角色 */
export function createRole(data: Partial<Role>) {
  return request<Role>({
    url: '/roles',
    method: 'post',
    data
  })
}

/** 修改角色 */
export function updateRole(id: number, data: Partial<Role>) {
  return request<Role>({
    url: `/roles/${id}`,
    method: 'put',
    data
  })
}

/** 删除角色 */
export function deleteRole(id: number) {
  return request<MessageOut>({
    url: `/roles/${id}`,
    method: 'delete'
  })
}
