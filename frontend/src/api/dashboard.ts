/**
 * 数据看板接口。
 */
import { request } from '@/utils/request'
import type {
  AssetStatistics,
  Overview,
  ScoreAnalysis,
  ScreenData,
  StudentComposition
} from '@/types/api'

/** 成绩分析查询参数 */
export interface ScoreAnalysisQuery {
  semester_id?: number
  exam_type?: string
}

/** 首页概览指标 */
export function getOverview() {
  return request<Overview>({
    url: '/dashboard/overview',
    method: 'get'
  })
}

/** 学生构成分析 */
export function getStudentComposition() {
  return request<StudentComposition>({
    url: '/dashboard/student-composition',
    method: 'get'
  })
}

/** 成绩分析 */
export function getScoreAnalysis(params: ScoreAnalysisQuery = {}) {
  return request<ScoreAnalysis>({
    url: '/dashboard/score-analysis',
    method: 'get',
    params
  })
}

/** 资产统计 */
export function getAssetStatistics() {
  return request<AssetStatistics>({
    url: '/dashboard/asset-statistics',
    method: 'get'
  })
}

/** 数据大屏聚合数据 */
export function getScreenData() {
  return request<ScreenData>({
    url: '/dashboard/screen',
    method: 'get'
  })
}
