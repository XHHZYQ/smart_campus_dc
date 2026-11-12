/**
 * 教职工档案接口。
 */
import { request } from '@/utils/request'
import type { MessageOut, OptionItem, PageResult, Teacher } from '@/types/api'

/** 教职工分页查询参数 */
export interface TeacherQuery {
  page?: number
  page_size?: number
  keyword?: string
  department_id?: number
  status?: string
}

/** 教职工表单数据 */
export interface TeacherForm {
  teacher_no: string
  name: string
  gender: string
  department_id?: number | null
  subject?: string | null
  title?: string | null
  phone?: string | null
  email?: string | null
  hire_date?: string | null
  status?: string
  remark?: string | null
}

/** 教职工分页列表 */
export function listTeachers(params: TeacherQuery) {
  return request<PageResult<Teacher>>({
    url: '/teachers',
    method: 'get',
    params
  })
}

/** 教职工下拉选项 */
export function listTeacherOptions() {
  return request<OptionItem[]>({
    url: '/teachers/options',
    method: 'get'
  })
}

/** 新增教职工 */
export function createTeacher(data: TeacherForm) {
  return request<Teacher>({
    url: '/teachers',
    method: 'post',
    data
  })
}

/** 修改教职工 */
export function updateTeacher(id: number, data: Partial<TeacherForm>) {
  return request<Teacher>({
    url: `/teachers/${id}`,
    method: 'put',
    data
  })
}

/** 删除教职工 */
export function deleteTeacher(id: number) {
  return request<MessageOut>({
    url: `/teachers/${id}`,
    method: 'delete'
  })
}
