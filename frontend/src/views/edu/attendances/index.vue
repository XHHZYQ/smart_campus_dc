<template>
  <div class="page-container">
    <div class="sc-card">
      <!-- 搜索栏 -->
      <el-form :inline="true" class="search-bar" @submit.prevent>
        <el-form-item label="班级">
          <el-select v-model="query.class_id" placeholder="全部班级" clearable filterable style="width: 160px">
            <el-option v-for="item in classOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程">
          <el-select v-model="query.course_id" placeholder="全部课程" clearable filterable style="width: 160px">
            <el-option v-for="item in courseOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="考勤日期">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 260px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 工具栏 -->
      <div class="table-toolbar">
        <span class="title">考勤记录列表</span>
        <el-button type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon> 新增考勤
        </el-button>
      </div>

      <!-- 表格 -->
      <el-table v-loading="loading" :data="list" border stripe>
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column prop="student_no" label="学籍号" min-width="120" />
        <el-table-column prop="student_name" label="学生姓名" min-width="100" />
        <el-table-column prop="class_name" label="班级" min-width="110" />
        <el-table-column prop="course_name" label="课程" min-width="100" />
        <el-table-column prop="attend_date" label="考勤日期" width="120" align="center" />
        <el-table-column label="考勤状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="140">
          <template #default="{ row }">{{ row.remark || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next"
          :total="total"
          :current-page="query.page"
          :page-size="query.page_size"
          :page-sizes="[10, 20, 50]"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </div>

    <!-- 新增 / 编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="520px" @closed="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="学生" prop="student_id">
          <el-select
            v-model="form.student_id"
            placeholder="请选择学生"
            filterable
            :disabled="!!editId"
            style="width: 100%"
          >
            <el-option v-for="item in studentOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程" prop="course_id">
          <el-select
            v-model="form.course_id"
            placeholder="请选择课程"
            filterable
            :disabled="!!editId"
            style="width: 100%"
          >
            <el-option v-for="item in courseOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="考勤日期" prop="attend_date">
          <el-date-picker
            v-model="form.attend_date"
            type="date"
            placeholder="请选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="考勤状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
            <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  createAttendance,
  deleteAttendance,
  listAttendances,
  updateAttendance,
  type AttendanceForm
} from '@/api/attendance'
import { listClassOptions } from '@/api/class'
import { listCourseOptions } from '@/api/course'
import { listStudentOptions } from '@/api/student'
import type { Attendance, OptionItem } from '@/types/api'

/** 考勤状态可选项 */
const statusOptions = ['正常', '迟到', '早退', '缺勤', '请假']

function statusTagType(status: string) {
  if (status === '正常') return 'success'
  if (status === '迟到' || status === '早退') return 'warning'
  if (status === '缺勤') return 'danger'
  return 'info'
}

const loading = ref(false)
const list = ref<Attendance[]>([])
const total = ref(0)
const dateRange = ref<[string, string] | undefined>(undefined)
const query = reactive<{
  page: number
  page_size: number
  class_id: number | undefined
  course_id: number | undefined
}>({
  page: 1,
  page_size: 10,
  class_id: undefined,
  course_id: undefined
})

const classOptions = ref<OptionItem[]>([])
const courseOptions = ref<OptionItem[]>([])
const studentOptions = ref<OptionItem[]>([])

const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const editId = ref<number | null>(null)
const dialogTitle = computed(() => (editId.value ? '编辑考勤' : '新增考勤'))

const form = reactive<{
  student_id: number | null
  course_id: number | null
  attend_date: string
  status: string
  remark: string
}>({
  student_id: null,
  course_id: null,
  attend_date: '',
  status: '正常',
  remark: ''
})

const rules: FormRules = {
  student_id: [{ required: true, message: '请选择学生', trigger: 'change' }],
  course_id: [{ required: true, message: '请选择课程', trigger: 'change' }],
  attend_date: [{ required: true, message: '请选择考勤日期', trigger: 'change' }],
  status: [{ required: true, message: '请选择考勤状态', trigger: 'change' }]
}

/** 加载考勤分页列表 */
async function loadList() {
  loading.value = true
  try {
    const res = await listAttendances({
      page: query.page,
      page_size: query.page_size,
      class_id: query.class_id,
      course_id: query.course_id,
      date_from: dateRange.value?.[0],
      date_to: dateRange.value?.[1]
    })
    list.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

/** 加载下拉选项 */
async function loadOptions() {
  classOptions.value = await listClassOptions()
  courseOptions.value = await listCourseOptions()
  studentOptions.value = await listStudentOptions()
}

function handleSearch() {
  query.page = 1
  loadList()
}

function handleReset() {
  query.class_id = undefined
  query.course_id = undefined
  dateRange.value = undefined
  query.page = 1
  loadList()
}

function handlePageChange(page: number) {
  query.page = page
  loadList()
}

function handleSizeChange(size: number) {
  query.page_size = size
  query.page = 1
  loadList()
}

function resetForm() {
  Object.assign(form, { student_id: null, course_id: null, attend_date: '', status: '正常', remark: '' })
  formRef.value?.clearValidate()
}

function openCreate() {
  editId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: Attendance) {
  editId.value = row.id
  Object.assign(form, {
    student_id: row.student_id,
    course_id: row.course_id,
    attend_date: row.attend_date,
    status: row.status,
    remark: row.remark || ''
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (editId.value) {
      await updateAttendance(editId.value, {
        status: form.status,
        remark: form.remark || null
      })
      ElMessage.success('修改成功')
    } else {
      const data: AttendanceForm = {
        student_id: form.student_id as number,
        course_id: form.course_id as number,
        attend_date: form.attend_date,
        status: form.status,
        remark: form.remark || null
      }
      await createAttendance(data)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    loadList()
  } catch {
    // 错误提示由请求拦截器统一处理
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row: Attendance) {
  try {
    await ElMessageBox.confirm(
      `确定删除「${row.student_name}」${row.attend_date} 的考勤记录吗？`,
      '提示',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }

  try {
    await deleteAttendance(row.id)
    ElMessage.success('删除成功')
    loadList()
  } catch {
    // 错误提示由请求拦截器统一处理
  }
}

onMounted(() => {
  loadList()
  loadOptions()
})
</script>
