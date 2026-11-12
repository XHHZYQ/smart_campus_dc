/**
 * 资产台账接口。
 */
import { request } from '@/utils/request'
import type { Asset, MessageOut, OptionItem, PageResult } from '@/types/api'

/** 资产分页查询参数 */
export interface AssetQuery {
  page?: number
  page_size?: number
  keyword?: string
  category?: string
  status?: string
  department_id?: number
}

/** 资产表单数据 */
export interface AssetForm {
  asset_no: string
  name: string
  category: string
  brand?: string | null
  model?: string | null
  price?: number | null
  quantity?: number
  purchase_date?: string | null
  department_id?: number | null
  keeper?: string | null
  status?: string
  location?: string | null
}

/** 资产分页列表 */
export function listAssets(params: AssetQuery) {
  return request<PageResult<Asset>>({
    url: '/assets',
    method: 'get',
    params
  })
}

/** 资产下拉选项 */
export function listAssetOptions() {
  return request<OptionItem[]>({
    url: '/assets/options',
    method: 'get'
  })
}

/** 新增资产 */
export function createAsset(data: AssetForm) {
  return request<Asset>({
    url: '/assets',
    method: 'post',
    data
  })
}

/** 修改资产 */
export function updateAsset(id: number, data: Partial<AssetForm>) {
  return request<Asset>({
    url: `/assets/${id}`,
    method: 'put',
    data
  })
}

/** 删除资产 */
export function deleteAsset(id: number) {
  return request<MessageOut>({
    url: `/assets/${id}`,
    method: 'delete'
  })
}
