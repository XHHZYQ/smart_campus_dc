<template>
  <div class="page-container">
    <div class="sc-card">
      <el-tabs v-model="activeTab">
        <!-- 宿舍房间 -->
        <el-tab-pane label="宿舍房间" name="room">
          <el-form :inline="true" class="search-bar" @submit.prevent>
            <el-form-item label="关键字">
              <el-input
                v-model="roomQuery.keyword"
                placeholder="宿舍楼 / 房间号"
                clearable
                style="width: 180px"
                @keyup.enter="handleRoomSearch"
              />
            </el-form-item>
            <el-form-item label="宿舍楼">
              <el-input v-model="roomQuery.building" placeholder="全部" clearable style="width: 140px" />
            </el-form-item>
            <el-form-item label="性别类型">
              <el-select v-model="roomQuery.gender_type" placeholder="全部" clearable style="width: 130px">
                <el-option v-for="item in genderTypeOptions" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleRoomSearch">查询</el-button>
              <el-button @click="handleRoomReset">重置</el-button>
            </el-form-item>
          </el-form>

          <div class="table-toolbar">
            <span class="title">宿舍房间列表</span>
            <el-button type="primary" @click="openRoomCreate">
              <el-icon><Plus /></el-icon> 新增房间
            </el-button>
          </div>

          <el-table v-loading="roomLoading" :data="roomList" border stripe>
            <el-table-column type="index" label="序号" width="70" align="center" />
            <el-table-column prop="building" label="宿舍楼" min-width="110" />
            <el-table-column prop="room_no" label="房间号" min-width="100" />
            <el-table-column prop="floor" label="楼层" width="80" align="center">
              <template #default="{ row }">{{ row.floor ?? '-' }}</template>
            </el-table-column>
            <el-table-column prop="capacity" label="床位数" width="90" align="center" />
            <el-table-column prop="occupied" label="已住人数" width="90" align="center" />
            <el-table-column prop="gender_type" label="性别类型" width="100" align="center" />
            <el-table-column prop="remark" label="备注" min-width="140">
              <template #default="{ row }">{{ row.remark || '-' }}</template>
            </el-table-column>
            <el-table-column label="操作" width="150" align="center" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="openRoomEdit(row)">编辑</el-button>
                <el-button link type="danger" @click="handleRoomDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-wrap">
            <el-pagination
              background
              layout="total, sizes, prev, pager, next"
              :total="roomTotal"
              :current-page="roomQuery.page"
              :page-size="roomQuery.page_size"
              :page-sizes="[10, 20, 50]"
              @current-change="handleRoomPageChange"
              @size-change="handleRoomSizeChange"
            />
          </div>
        </el-tab-pane>

        <!-- 住宿分配 -->
        <el-tab-pane label="住宿分配" name="allocation">
          <el-form :inline="true" class="search-bar" @submit.prevent>
            <el-form-item label="关键字">
              <el-input
                v-model="allocQuery.keyword"
                placeholder="学籍号 / 学生姓名"
                clearable
                style="width: 200px"
                @keyup.enter="handleAllocSearch"
              />
            </el-form-item>
            <el-form-item label="宿舍房间">
              <el-select v-model="allocQuery.room_id" placeholder="全部房间" clearable filterable style="width: 180px">
                <el-option v-for="item in roomOptions" :key="item.id" :label="item.name" :value="item.id" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleAllocSearch">查询</el-button>
              <el-button @click="handleAllocReset">重置</el-button>
            </el-form-item>
          </el-form>

          <div class="table-toolbar">
            <span class="title">住宿分配列表</span>
            <el-button type="primary" @click="openAllocCreate">
              <el-icon><Plus /></el-icon> 新增分配
            </el-button>
          </div>

          <el-table v-loading="allocLoading" :data="allocList" border stripe>
            <el-table-column type="index" label="序号" width="70" align="center" />
            <el-table-column prop="student_no" label="学籍号" min-width="120" />
            <el-table-column prop="student_name" label="学生姓名" min-width="100" />
            <el-table-column prop="class_name" label="班级" min-width="110" />
            <el-table-column label="宿舍" min-width="120">
              <template #default="{ row }">{{ row.building }} {{ row.room_no }}</template>
            </el-table-column>
            <el-table-column prop="bed_no" label="床位号" min-width="90">
              <template #default="{ row }">{{ row.bed_no || '-' }}</template>
            </el-table-column>
            <el-table-column prop="check_in_date" label="入住日期" width="120" align="center">
              <template #default="{ row }">{{ row.check_in_date || '-' }}</template>
            </el-table-column>
            <el-table-column label="状态" width="90" align="center">
              <template #default="{ row }">
                <el-tag :type="row.status === '在住' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="210" align="center" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="openAllocEdit(row)">编辑</el-button>
                <el-button
                  link
                  type="warning"
                  :disabled="row.status !== '在住'"
                  @click="handleCheckout(row)"
                >
                  退宿
                </el-button>
                <el-button link type="danger" @click="handleAllocDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-wrap">
            <el-pagination
              background
              layout="total, sizes, prev, pager, next"
              :total="allocTotal"
              :current-page="allocQuery.page"
              :page-size="allocQuery.page_size"
              :page-sizes="[10, 20, 50]"
              @current-change="handleAllocPageChange"
              @size-change="handleAllocSizeChange"
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 房间新增 / 编辑弹窗 -->
    <el-dialog v-model="roomDialogVisible" :title="roomDialogTitle" width="520px" @closed="resetRoomForm">
      <el-form ref="roomFormRef" :model="roomForm" :rules="roomRules" label-width="100px">
        <el-form-item label="宿舍楼" prop="building">
          <el-input v-model="roomForm.building" placeholder="如：1号楼" />
        </el-form-item>
        <el-form-item label="房间号" prop="room_no">
          <el-input v-model="roomForm.room_no" placeholder="如：101" />
        </el-form-item>
        <el-form-item label="楼层" prop="floor">
          <el-input-number v-model="roomForm.floor" :min="1" :max="30" />
        </el-form-item>
        <el-form-item label="床位数" prop="capacity">
          <el-input-number v-model="roomForm.capacity" :min="1" :max="20" />
        </el-form-item>
        <el-form-item label="性别类型" prop="gender_type">
          <el-select v-model="roomForm.gender_type" placeholder="请选择" style="width: 100%">
            <el-option v-for="item in genderTypeOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="roomForm.remark" type="textarea" :rows="2" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roomDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitRoom">确定</el-button>
      </template>
    </el-dialog>

    <!-- 分配新增 / 编辑弹窗 -->
    <el-dialog v-model="allocDialogVisible" :title="allocDialogTitle" width="520px" @closed="resetAllocForm">
      <el-form ref="allocFormRef" :model="allocForm" :rules="allocRules" label-width="100px">
        <el-form-item label="学生" prop="student_id">
          <el-select
            v-model="allocForm.student_id"
            placeholder="请选择学生"
            filterable
            :disabled="!!allocEditId"
            style="width: 100%"
          >
            <el-option v-for="item in studentOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="宿舍房间" prop="room_id">
          <el-select v-model="allocForm.room_id" placeholder="请选择房间" filterable style="width: 100%">
            <el-option v-for="item in roomOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="床位号" prop="bed_no">
          <el-input v-model="allocForm.bed_no" placeholder="可选" />
        </el-form-item>
        <el-form-item label="入住日期" prop="check_in_date">
          <el-date-picker
            v-model="allocForm.check_in_date"
            type="date"
            placeholder="请选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="allocForm.status" placeholder="请选择状态" style="width: 100%">
            <el-option v-for="item in allocStatusOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="allocDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitAlloc">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  createDormAllocation,
  createDormRoom,
  deleteDormAllocation,
  deleteDormRoom,
  listDormAllocations,
  listDormRoomOptions,
  listDormRooms,
  updateDormAllocation,
  updateDormRoom,
  type DormAllocationForm,
  type DormRoomForm
} from '@/api/dorm'
import { listStudentOptions } from '@/api/student'
import type { DormAllocation, DormRoom, OptionItem } from '@/types/api'

/** 性别类型可选项 */
const genderTypeOptions = ['男', '女']
/** 住宿状态可选项 */
const allocStatusOptions = ['在住', '已退']

const activeTab = ref('room')
const submitting = ref(false)
const roomOptions = ref<OptionItem[]>([])
const studentOptions = ref<OptionItem[]>([])

/* ---------------- 宿舍房间 ---------------- */
const roomLoading = ref(false)
const roomList = ref<DormRoom[]>([])
const roomTotal = ref(0)
const roomQuery = reactive<{
  page: number
  page_size: number
  keyword: string
  building: string
  gender_type: string | undefined
}>({
  page: 1,
  page_size: 10,
  keyword: '',
  building: '',
  gender_type: undefined
})

const roomDialogVisible = ref(false)
const roomFormRef = ref<FormInstance>()
const roomEditId = ref<number | null>(null)
const roomDialogTitle = computed(() => (roomEditId.value ? '编辑宿舍房间' : '新增宿舍房间'))
const roomForm = reactive<{
  building: string
  room_no: string
  floor: number | null
  capacity: number
  gender_type: string
  remark: string
}>({
  building: '',
  room_no: '',
  floor: 1,
  capacity: 6,
  gender_type: '男',
  remark: ''
})
const roomRules: FormRules = {
  building: [{ required: true, message: '请输入宿舍楼', trigger: 'blur' }],
  room_no: [{ required: true, message: '请输入房间号', trigger: 'blur' }],
  capacity: [{ required: true, message: '请输入床位数', trigger: 'blur' }],
  gender_type: [{ required: true, message: '请选择性别类型', trigger: 'change' }]
}

/** 加载宿舍房间分页列表 */
async function loadRooms() {
  roomLoading.value = true
  try {
    const res = await listDormRooms({
      page: roomQuery.page,
      page_size: roomQuery.page_size,
      keyword: roomQuery.keyword || undefined,
      building: roomQuery.building || undefined,
      gender_type: roomQuery.gender_type
    })
    roomList.value = res.items
    roomTotal.value = res.total
  } finally {
    roomLoading.value = false
  }
}

function handleRoomSearch() {
  roomQuery.page = 1
  loadRooms()
}

function handleRoomReset() {
  roomQuery.keyword = ''
  roomQuery.building = ''
  roomQuery.gender_type = undefined
  roomQuery.page = 1
  loadRooms()
}

function handleRoomPageChange(page: number) {
  roomQuery.page = page
  loadRooms()
}

function handleRoomSizeChange(size: number) {
  roomQuery.page_size = size
  roomQuery.page = 1
  loadRooms()
}

function resetRoomForm() {
  Object.assign(roomForm, { building: '', room_no: '', floor: 1, capacity: 6, gender_type: '男', remark: '' })
  roomFormRef.value?.clearValidate()
}

function openRoomCreate() {
  roomEditId.value = null
  resetRoomForm()
  roomDialogVisible.value = true
}

function openRoomEdit(row: DormRoom) {
  roomEditId.value = row.id
  Object.assign(roomForm, {
    building: row.building,
    room_no: row.room_no,
    floor: row.floor,
    capacity: row.capacity,
    gender_type: row.gender_type,
    remark: row.remark || ''
  })
  roomDialogVisible.value = true
}

async function submitRoom() {
  const valid = await roomFormRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const data: DormRoomForm = {
      building: roomForm.building,
      room_no: roomForm.room_no,
      floor: roomForm.floor,
      capacity: roomForm.capacity,
      gender_type: roomForm.gender_type,
      remark: roomForm.remark || null
    }
    if (roomEditId.value) {
      await updateDormRoom(roomEditId.value, data)
      ElMessage.success('修改成功')
    } else {
      await createDormRoom(data)
      ElMessage.success('新增成功')
    }
    roomDialogVisible.value = false
    loadRooms()
    loadRoomOptions()
  } catch {
    // 错误提示由请求拦截器统一处理
  } finally {
    submitting.value = false
  }
}

async function handleRoomDelete(row: DormRoom) {
  try {
    await ElMessageBox.confirm(`确定删除宿舍「${row.building} ${row.room_no}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch {
    return
  }

  try {
    await deleteDormRoom(row.id)
    ElMessage.success('删除成功')
    loadRooms()
    loadRoomOptions()
  } catch {
    // 错误提示由请求拦截器统一处理
  }
}

/* ---------------- 住宿分配 ---------------- */
const allocLoading = ref(false)
const allocList = ref<DormAllocation[]>([])
const allocTotal = ref(0)
const allocQuery = reactive<{
  page: number
  page_size: number
  keyword: string
  room_id: number | undefined
}>({
  page: 1,
  page_size: 10,
  keyword: '',
  room_id: undefined
})

const allocDialogVisible = ref(false)
const allocFormRef = ref<FormInstance>()
const allocEditId = ref<number | null>(null)
const allocDialogTitle = computed(() => (allocEditId.value ? '编辑住宿分配' : '新增住宿分配'))
const allocForm = reactive<{
  student_id: number | null
  room_id: number | null
  bed_no: string
  check_in_date: string
  status: string
}>({
  student_id: null,
  room_id: null,
  bed_no: '',
  check_in_date: '',
  status: '在住'
})
const allocRules: FormRules = {
  student_id: [{ required: true, message: '请选择学生', trigger: 'change' }],
  room_id: [{ required: true, message: '请选择宿舍房间', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

/** 加载住宿分配分页列表 */
async function loadAllocations() {
  allocLoading.value = true
  try {
    const res = await listDormAllocations({
      page: allocQuery.page,
      page_size: allocQuery.page_size,
      keyword: allocQuery.keyword || undefined,
      room_id: allocQuery.room_id
    })
    allocList.value = res.items
    allocTotal.value = res.total
  } finally {
    allocLoading.value = false
  }
}

/** 加载房间下拉选项 */
async function loadRoomOptions() {
  roomOptions.value = await listDormRoomOptions()
}

function handleAllocSearch() {
  allocQuery.page = 1
  loadAllocations()
}

function handleAllocReset() {
  allocQuery.keyword = ''
  allocQuery.room_id = undefined
  allocQuery.page = 1
  loadAllocations()
}

function handleAllocPageChange(page: number) {
  allocQuery.page = page
  loadAllocations()
}

function handleAllocSizeChange(size: number) {
  allocQuery.page_size = size
  allocQuery.page = 1
  loadAllocations()
}

function resetAllocForm() {
  Object.assign(allocForm, { student_id: null, room_id: null, bed_no: '', check_in_date: '', status: '在住' })
  allocFormRef.value?.clearValidate()
}

function openAllocCreate() {
  allocEditId.value = null
  resetAllocForm()
  allocDialogVisible.value = true
}

function openAllocEdit(row: DormAllocation) {
  allocEditId.value = row.id
  Object.assign(allocForm, {
    student_id: row.student_id,
    room_id: row.room_id,
    bed_no: row.bed_no || '',
    check_in_date: row.check_in_date || '',
    status: row.status
  })
  allocDialogVisible.value = true
}

async function submitAlloc() {
  const valid = await allocFormRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const data: DormAllocationForm = {
      student_id: allocForm.student_id as number,
      room_id: allocForm.room_id as number,
      bed_no: allocForm.bed_no || null,
      check_in_date: allocForm.check_in_date || null,
      status: allocForm.status
    }
    if (allocEditId.value) {
      await updateDormAllocation(allocEditId.value, data)
      ElMessage.success('修改成功')
    } else {
      await createDormAllocation(data)
      ElMessage.success('新增成功')
    }
    allocDialogVisible.value = false
    loadAllocations()
    loadRooms()
  } catch {
    // 错误提示由请求拦截器统一处理
  } finally {
    submitting.value = false
  }
}

async function handleCheckout(row: DormAllocation) {
  try {
    await ElMessageBox.confirm(`确定将「${row.student_name}」办理退宿吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch {
    return
  }

  try {
    await updateDormAllocation(row.id, { status: '已退' })
    ElMessage.success('退宿成功')
    loadAllocations()
    loadRooms()
  } catch {
    // 错误提示由请求拦截器统一处理
  }
}

async function handleAllocDelete(row: DormAllocation) {
  try {
    await ElMessageBox.confirm(`确定删除「${row.student_name}」的住宿分配记录吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch {
    return
  }

  try {
    await deleteDormAllocation(row.id)
    ElMessage.success('删除成功')
    loadAllocations()
    loadRooms()
  } catch {
    // 错误提示由请求拦截器统一处理
  }
}

onMounted(() => {
  loadRooms()
  loadAllocations()
  loadRoomOptions()
  listStudentOptions().then((res) => {
    studentOptions.value = res
  })
})
</script>
