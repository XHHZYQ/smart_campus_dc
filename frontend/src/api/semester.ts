/**
 * 学期管理接口。
 */
import { request } from '@/utils/request'
import type { MessageOut, OptionItem, PageResult, Semester } from '@/types/api'

/** 学期分页查询参数 */
export interface SemesterQuery {
  page?: number
  page_size?: number
  keyword?: string
}

/** 学期表单数据 */
export interface SemesterForm {
  name: string
  academic_year: string
  term: number
  start_date?: string | null
  end_date?: string | null
  is_current?: boolean
}

/** 学期分页列表 */
export function listSemesters(params: SemesterQuery) {
  return request<PageResult<Semester>>({
    url: '/semesters',
    method: 'get',
    params
  })
}

/** 学期下拉选项 */
export function listSemesterOptions() {
  return request<OptionItem[]>({
    url: '/semesters/options',
    method: 'get'
  })
}

/** 新增学期 */
export function createSemester(data: SemesterForm) {
  return request<Semester>({
    url: '/semesters',
    method: 'post',
    data
  })
}

/** 修改学期 */
export function updateSemester(id: number, data: Partial<SemesterForm>) {
  return request<Semester>({
    url: `/semesters/${id}`,
    method: 'put',
    data
  })
}

/** 删除学期 */
export function deleteSemester(id: number) {
  return request<MessageOut>({
    url: `/semesters/${id}`,
    method: 'delete'
  })
}
