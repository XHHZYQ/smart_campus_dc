/**
 * 成绩管理接口。
 */
import { request } from '@/utils/request'
import type { BatchScoreRequest, MessageOut, PageResult, Score } from '@/types/api'

/** 成绩分页查询参数 */
export interface ScoreQuery {
  page?: number
  page_size?: number
  student_id?: number
  class_id?: number
  course_id?: number
  semester_id?: number
  exam_type?: string
}

/** 成绩表单数据 */
export interface ScoreForm {
  student_id: number
  course_id: number
  semester_id: number
  exam_type?: string
  score?: number | null
  remark?: string | null
}

/** 成绩分页列表 */
export function listScores(params: ScoreQuery) {
  return request<PageResult<Score>>({
    url: '/scores',
    method: 'get',
    params
  })
}

/** 单条录入成绩 */
export function createScore(data: ScoreForm) {
  return request<Score>({
    url: '/scores',
    method: 'post',
    data
  })
}

/** 批量录入成绩 */
export function batchCreateScores(data: BatchScoreRequest) {
  return request<MessageOut>({
    url: '/scores/batch',
    method: 'post',
    data
  })
}

/** 修改成绩 */
export function updateScore(id: number, data: { exam_type?: string; score?: number | null; remark?: string | null }) {
  return request<Score>({
    url: `/scores/${id}`,
    method: 'put',
    data
  })
}

/** 删除成绩 */
export function deleteScore(id: number) {
  return request<MessageOut>({
    url: `/scores/${id}`,
    method: 'delete'
  })
}
