/**
 * 学科课程接口。
 */
import { request } from '@/utils/request'
import type { Course, MessageOut, OptionItem, PageResult } from '@/types/api'

/** 课程分页查询参数 */
export interface CourseQuery {
  page?: number
  page_size?: number
  keyword?: string
}

/** 课程表单数据 */
export interface CourseForm {
  code: string
  name: string
  stage: string
  department_id?: number | null
  weekly_hours?: number
  course_type?: string
  teacher_id?: number | null
}

/** 课程分页列表 */
export function listCourses(params: CourseQuery) {
  return request<PageResult<Course>>({
    url: '/courses',
    method: 'get',
    params
  })
}

/** 课程下拉选项 */
export function listCourseOptions() {
  return request<OptionItem[]>({
    url: '/courses/options',
    method: 'get'
  })
}

/** 新增课程 */
export function createCourse(data: CourseForm) {
  return request<Course>({
    url: '/courses',
    method: 'post',
    data
  })
}

/** 修改课程 */
export function updateCourse(id: number, data: Partial<CourseForm>) {
  return request<Course>({
    url: `/courses/${id}`,
    method: 'put',
    data
  })
}

/** 删除课程 */
export function deleteCourse(id: number) {
  return request<MessageOut>({
    url: `/courses/${id}`,
    method: 'delete'
  })
}
