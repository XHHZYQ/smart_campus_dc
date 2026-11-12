<template>
  <div class="page-container">
    <div class="sc-card">
      <!-- 搜索栏 -->
      <el-form :inline="true" class="search-bar" @submit.prevent>
        <el-form-item label="关键字">
          <el-input
            v-model="query.keyword"
            placeholder="课程名称 / 代码"
            clearable
            style="width: 220px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格工具栏 -->
      <div class="table-toolbar">
        <span class="title">学科课程列表</span>
        <el-button type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon> 新增课程
        </el-button>
      </div>

      <!-- 数据表格 -->
      <el-table v-loading="loading" :data="list" border stripe>
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column prop="code" label="课程代码" min-width="110" />
        <el-table-column prop="name" label="课程名称" min-width="120" />
        <el-table-column prop="stage" label="适用学段" width="100" align="center" />
        <el-table-column prop="department_name" label="开课教研组" min-width="130">
          <template #default="{ row }">{{ row.department_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="weekly_hours" label="周课时" width="90" align="center" />
        <el-table-column prop="course_type" label="课程性质" width="100" align="center" />
        <el-table-column prop="teacher_name" label="任课教师" min-width="110">
          <template #default="{ row }">{{ row.teacher_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="560px" @closed="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="课程代码" prop="code">
          <el-input v-model="form.code" :disabled="!!editId" placeholder="请输入课程代码" />
        </el-form-item>
        <el-form-item label="课程名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入课程名称" />
        </el-form-item>
        <el-form-item label="适用学段" prop="stage">
          <el-select v-model="form.stage" placeholder="请选择学段" style="width: 100%">
            <el-option v-for="item in stageOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="开课教研组" prop="department_id">
          <el-select v-model="form.department_id" placeholder="可不选" clearable filterable style="width: 100%">
            <el-option v-for="item in departmentOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="任课教师" prop="teacher_id">
          <el-select v-model="form.teacher_id" placeholder="可不选" clearable filterable style="width: 100%">
            <el-option v-for="item in teacherOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程性质" prop="course_type">
          <el-select v-model="form.course_type" placeholder="请选择课程性质" style="width: 100%">
            <el-option v-for="item in courseTypeOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="周课时" prop="weekly_hours">
          <el-input-number v-model="form.weekly_hours" :min="1" :max="30" />
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
  createCourse,
  deleteCourse,
  listCourses,
  updateCourse,
  type CourseForm
} from '@/api/course'
import { listDepartmentOptions } from '@/api/department'
import { listTeacherOptions } from '@/api/teacher'
import type { Course, OptionItem } from '@/types/api'

/** 学段可选项 */
const stageOptions = ['小学', '初中', '高中']
/** 课程性质可选项 */
const courseTypeOptions = ['必修', '选修', '活动']

const loading = ref(false)
const list = ref<Course[]>([])
const total = ref(0)
const query = reactive<{ page: number; page_size: number; keyword: string }>({
  page: 1,
  page_size: 10,
  keyword: ''
})

const departmentOptions = ref<OptionItem[]>([])
const teacherOptions = ref<OptionItem[]>([])

const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const editId = ref<number | null>(null)
const dialogTitle = computed(() => (editId.value ? '编辑课程' : '新增课程'))

const form = reactive<{
  code: string
  name: string
  stage: string
  department_id: number | null
  teacher_id: number | null
  course_type: string
  weekly_hours: number
}>({
  code: '',
  name: '',
  stage: '小学',
  department_id: null,
  teacher_id: null,
  course_type: '必修',
  weekly_hours: 2
})

const rules: FormRules = {
  code: [{ required: true, message: '请输入课程代码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  stage: [{ required: true, message: '请选择适用学段', trigger: 'change' }],
  course_type: [{ required: true, message: '请选择课程性质', trigger: 'change' }]
}

/** 加载课程分页列表 */
async function loadList() {
  loading.value = true
  try {
    const res = await listCourses({
      page: query.page,
      page_size: query.page_size,
      keyword: query.keyword || undefined
    })
    list.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

/** 加载下拉选项 */
async function loadOptions() {
  departmentOptions.value = await listDepartmentOptions()
  teacherOptions.value = await listTeacherOptions()
}

function handleSearch() {
  query.page = 1
  loadList()
}

function handleReset() {
  query.keyword = ''
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
  Object.assign(form, {
    code: '',
    name: '',
    stage: '小学',
    department_id: null,
    teacher_id: null,
    course_type: '必修',
    weekly_hours: 2
  })
  formRef.value?.clearValidate()
}

function openCreate() {
  editId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: Course) {
  editId.value = row.id
  Object.assign(form, {
    code: row.code,
    name: row.name,
    stage: row.stage,
    department_id: row.department_id,
    teacher_id: row.teacher_id,
    course_type: row.course_type,
    weekly_hours: row.weekly_hours
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const data: CourseForm = { ...form }
    if (editId.value) {
      const { code: _code, ...rest } = data
      await updateCourse(editId.value, rest)
      ElMessage.success('修改成功')
    } else {
      await createCourse(data)
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

async function handleDelete(row: Course) {
  try {
    await ElMessageBox.confirm(`确定删除课程「${row.name}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch {
    return
  }

  try {
    await deleteCourse(row.id)
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
