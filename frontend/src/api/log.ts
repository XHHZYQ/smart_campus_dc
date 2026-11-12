/**
 * 日志查询接口（操作日志、登录日志，均为只读）。
 */
import { request } from '@/utils/request'
import type { LoginLog, OperationLog, PageResult } from '@/types/api'

/** 日志分页查询参数 */
export interface LogQuery {
  page?: number
  page_size?: number
  keyword?: string
  start_date?: string
  end_date?: string
}

/** 操作日志分页列表 */
export function listOperationLogs(params: LogQuery) {
  return request<PageResult<OperationLog>>({
    url: '/logs/operation',
    method: 'get',
    params
  })
}

/** 登录日志分页列表 */
export function listLoginLogs(params: LogQuery) {
  return request<PageResult<LoginLog>>({
    url: '/logs/login',
    method: 'get',
    params
  })
}
