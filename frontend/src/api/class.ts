/**
 * 班级管理接口。
 */
import { request } from '@/utils/request'
import type { ClassInfo, MessageOut, OptionItem, PageResult } from '@/types/api'

/** 班级分页查询参数 */
export interface ClassQuery {
  page?: number
  page_size?: number
  keyword?: string
  grade_id?: number
}

/** 班级表单数据 */
export interface ClassForm {
  name: string
  code: string
  grade_id: number
  room?: string | null
  head_teacher_id?: number | null
  enroll_year?: number | null
  remark?: string | null
}

/** 班级分页列表 */
export function listClasses(params: ClassQuery) {
  return request<PageResult<ClassInfo>>({
    url: '/classes',
    method: 'get',
    params
  })
}

/** 班级下拉选项（可按年级过滤） */
export function listClassOptions(gradeId?: number) {
  return request<OptionItem[]>({
    url: '/classes/options',
    method: 'get',
    params: gradeId ? { grade_id: gradeId } : {}
  })
}

/** 新增班级 */
export function createClass(data: ClassForm) {
  return request<ClassInfo>({
    url: '/classes',
    method: 'post',
    data
  })
}

/** 修改班级 */
export function updateClass(id: number, data: Partial<ClassForm>) {
  return request<ClassInfo>({
    url: `/classes/${id}`,
    method: 'put',
    data
  })
}

/** 删除班级 */
export function deleteClass(id: number) {
  return request<MessageOut>({
    url: `/classes/${id}`,
    method: 'delete'
  })
}
