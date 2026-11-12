/**
 * 部门管理接口。
 */
import { request } from '@/utils/request'
import type { Department, MessageOut, OptionItem, PageResult } from '@/types/api'

/** 部门分页查询参数 */
export interface DepartmentQuery {
  page?: number
  page_size?: number
  keyword?: string
  dept_type?: string
}

/** 部门表单数据 */
export type DepartmentForm = Omit<Department, 'id' | 'created_at'>

/** 部门分页列表 */
export function listDepartments(params: DepartmentQuery) {
  return request<PageResult<Department>>({
    url: '/departments',
    method: 'get',
    params
  })
}

/** 部门下拉选项 */
export function listDepartmentOptions() {
  return request<OptionItem[]>({
    url: '/departments/options',
    method: 'get'
  })
}

/** 新增部门 */
export function createDepartment(data: Partial<DepartmentForm>) {
  return request<Department>({
    url: '/departments',
    method: 'post',
    data
  })
}

/** 修改部门 */
export function updateDepartment(id: number, data: Partial<DepartmentForm>) {
  return request<Department>({
    url: `/departments/${id}`,
    method: 'put',
    data
  })
}

/** 删除部门 */
export function deleteDepartment(id: number) {
  return request<MessageOut>({
    url: `/departments/${id}`,
    method: 'delete'
  })
}
