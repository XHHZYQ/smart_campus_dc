/**
 * 年级管理接口。
 */
import { request } from '@/utils/request'
import type { Grade, MessageOut, OptionItem, PageResult } from '@/types/api'

/** 年级分页查询参数 */
export interface GradeQuery {
  page?: number
  page_size?: number
  keyword?: string
  stage?: string
}

/** 年级表单数据 */
export interface GradeForm {
  name: string
  code: string
  stage: string
  grade_level: number
  head_teacher_id?: number | null
}

/** 年级分页列表 */
export function listGrades(params: GradeQuery) {
  return request<PageResult<Grade>>({
    url: '/grades',
    method: 'get',
    params
  })
}

/** 年级下拉选项 */
export function listGradeOptions() {
  return request<OptionItem[]>({
    url: '/grades/options',
    method: 'get'
  })
}

/** 新增年级 */
export function createGrade(data: GradeForm) {
  return request<Grade>({
    url: '/grades',
    method: 'post',
    data
  })
}

/** 修改年级 */
export function updateGrade(id: number, data: Partial<GradeForm>) {
  return request<Grade>({
    url: `/grades/${id}`,
    method: 'put',
    data
  })
}

/** 删除年级 */
export function deleteGrade(id: number) {
  return request<MessageOut>({
    url: `/grades/${id}`,
    method: 'delete'
  })
}
