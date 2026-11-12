/**
 * 考勤记录接口。
 */
import { request } from '@/utils/request'
import type { Attendance, MessageOut, PageResult } from '@/types/api'

/** 考勤分页查询参数 */
export interface AttendanceQuery {
  page?: number
  page_size?: number
  student_id?: number
  class_id?: number
  course_id?: number
  date_from?: string
  date_to?: string
}

/** 考勤表单数据 */
export interface AttendanceForm {
  student_id: number
  course_id: number
  attend_date: string
  status?: string
  remark?: string | null
}

/** 考勤分页列表 */
export function listAttendances(params: AttendanceQuery) {
  return request<PageResult<Attendance>>({
    url: '/attendances',
    method: 'get',
    params
  })
}

/** 新增考勤 */
export function createAttendance(data: AttendanceForm) {
  return request<Attendance>({
    url: '/attendances',
    method: 'post',
    data
  })
}

/** 修改考勤 */
export function updateAttendance(id: number, data: { status?: string; remark?: string | null }) {
  return request<Attendance>({
    url: `/attendances/${id}`,
    method: 'put',
    data
  })
}

/** 删除考勤 */
export function deleteAttendance(id: number) {
  return request<MessageOut>({
    url: `/attendances/${id}`,
    method: 'delete'
  })
}
