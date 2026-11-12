/**
 * 宿舍管理接口：宿舍房间与住宿分配。
 */
import { request } from '@/utils/request'
import type {
  DormAllocation,
  DormRoom,
  MessageOut,
  OptionItem,
  PageResult
} from '@/types/api'

/** 宿舍房间分页查询参数 */
export interface DormRoomQuery {
  page?: number
  page_size?: number
  keyword?: string
  building?: string
  gender_type?: string
}

/** 宿舍房间表单数据 */
export interface DormRoomForm {
  building: string
  room_no: string
  floor?: number | null
  capacity?: number
  gender_type?: string
  remark?: string | null
}

/** 住宿分配分页查询参数 */
export interface DormAllocationQuery {
  page?: number
  page_size?: number
  keyword?: string
  room_id?: number
}

/** 住宿分配表单数据 */
export interface DormAllocationForm {
  student_id: number
  room_id: number
  bed_no?: string | null
  check_in_date?: string | null
  status?: string
}

/* ---------------- 宿舍房间 ---------------- */

/** 宿舍房间分页列表 */
export function listDormRooms(params: DormRoomQuery) {
  return request<PageResult<DormRoom>>({
    url: '/dorms/rooms',
    method: 'get',
    params
  })
}

/** 宿舍房间下拉选项 */
export function listDormRoomOptions() {
  return request<OptionItem[]>({
    url: '/dorms/rooms/options',
    method: 'get'
  })
}

/** 新增宿舍房间 */
export function createDormRoom(data: DormRoomForm) {
  return request<DormRoom>({
    url: '/dorms/rooms',
    method: 'post',
    data
  })
}

/** 修改宿舍房间 */
export function updateDormRoom(id: number, data: Partial<DormRoomForm>) {
  return request<DormRoom>({
    url: `/dorms/rooms/${id}`,
    method: 'put',
    data
  })
}

/** 删除宿舍房间 */
export function deleteDormRoom(id: number) {
  return request<MessageOut>({
    url: `/dorms/rooms/${id}`,
    method: 'delete'
  })
}

/* ---------------- 住宿分配 ---------------- */

/** 住宿分配分页列表 */
export function listDormAllocations(params: DormAllocationQuery) {
  return request<PageResult<DormAllocation>>({
    url: '/dorms/allocations',
    method: 'get',
    params
  })
}

/** 新增住宿分配 */
export function createDormAllocation(data: DormAllocationForm) {
  return request<DormAllocation>({
    url: '/dorms/allocations',
    method: 'post',
    data
  })
}

/** 修改住宿分配 */
export function updateDormAllocation(id: number, data: Partial<DormAllocationForm>) {
  return request<DormAllocation>({
    url: `/dorms/allocations/${id}`,
    method: 'put',
    data
  })
}

/** 删除住宿分配 */
export function deleteDormAllocation(id: number) {
  return request<MessageOut>({
    url: `/dorms/allocations/${id}`,
    method: 'delete'
  })
}
