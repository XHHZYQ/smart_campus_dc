/**
 * 学生学籍接口。
 */
import { request } from '@/utils/request'
import type { MessageOut, OptionItem, PageResult, Student } from '@/types/api'

/** 学生分页查询参数 */
export interface StudentQuery {
  page?: number
  page_size?: number
  keyword?: string
  class_id?: number
  status?: string
}

/** 学生表单数据（不含后端计算字段） */
export type StudentForm = Omit<Student, 'id' | 'class_name' | 'grade_name' | 'created_at'>

/** 学生分页列表 */
export function listStudents(params: StudentQuery) {
  return request<PageResult<Student>>({
    url: '/students',
    method: 'get',
    params
  })
}

/** 学生下拉选项（可按班级过滤） */
export function listStudentOptions(classId?: number) {
  return request<OptionItem[]>({
    url: '/students/options',
    method: 'get',
    params: classId ? { class_id: classId } : {}
  })
}

/** 学生详情 */
export function getStudent(id: number) {
  return request<Student>({
    url: `/students/${id}`,
    method: 'get'
  })
}

/** 新增学生 */
export function createStudent(data: Partial<StudentForm>) {
  return request<Student>({
    url: '/students',
    method: 'post',
    data
  })
}

/** 修改学生 */
export function updateStudent(id: number, data: Partial<StudentForm>) {
  return request<Student>({
    url: `/students/${id}`,
    method: 'put',
    data
  })
}

/** 删除学生 */
export function deleteStudent(id: number) {
  return request<MessageOut>({
    url: `/students/${id}`,
    method: 'delete'
  })
}
