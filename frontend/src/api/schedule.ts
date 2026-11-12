/**
 * 排课管理接口。
 */
import { request } from '@/utils/request'
import type { MessageOut, PageResult, Schedule, TimetableCell } from '@/types/api'

/** 排课分页查询参数 */
export interface ScheduleQuery {
  page?: number
  page_size?: number
  class_id?: number
  course_id?: number
  semester_id?: number
  weekday?: number
}

/** 周课表查询参数 */
export interface TimetableQuery {
  class_id?: number
  teacher_id?: number
  semester_id?: number
}

/** 排课表单数据 */
export interface ScheduleForm {
  semester_id: number
  class_id: number
  course_id: number
  teacher_id?: number | null
  weekday: number
  period: number
  room?: string | null
}

/** 排课分页列表 */
export function listSchedules(params: ScheduleQuery) {
  return request<PageResult<Schedule>>({
    url: '/schedules',
    method: 'get',
    params
  })
}

/** 周课表（按班级或教师） */
export function getTimetable(params: TimetableQuery) {
  return request<TimetableCell[]>({
    url: '/schedules/timetable',
    method: 'get',
    params
  })
}

/** 新增排课 */
export function createSchedule(data: ScheduleForm) {
  return request<Schedule>({
    url: '/schedules',
    method: 'post',
    data
  })
}

/** 修改排课 */
export function updateSchedule(id: number, data: Partial<ScheduleForm>) {
  return request<Schedule>({
    url: `/schedules/${id}`,
    method: 'put',
    data
  })
}

/** 删除排课 */
export function deleteSchedule(id: number) {
  return request<MessageOut>({
    url: `/schedules/${id}`,
    method: 'delete'
  })
}
