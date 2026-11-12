<template>
  <div class="page-container">
    <div class="sc-card">
      <!-- 搜索栏 -->
      <el-form :inline="true" class="search-bar" @submit.prevent>
        <el-form-item label="关键字">
          <el-input
            v-model="query.keyword"
            placeholder="班级名称 / 编码"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="年级">
          <el-select v-model="query.grade_id" placeholder="全部年级" clearable style="width: 160px">
            <el-option v-for="item in gradeOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格工具栏 -->
      <div class="table-toolbar">
        <span class="title">班级列表</span>
        <el-button type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon> 新增班级
        </el-button>
      </div>

      <!-- 数据表格 -->
      <el-table v-loading="loading" :data="list" border stripe>
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column prop="name" label="班级名称" min-width="130" />
        <el-table-column prop="code" label="班级编码" min-width="120" />
        <el-table-column prop="grade_name" label="所属年级" min-width="110" />
        <el-table-column label="学段" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="stageTagType(row.stage)">{{ row.stage }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="room" label="教室" min-width="100" />
        <el-table-column prop="head_teacher_name" label="班主任" min-width="110">
          <template #default="{ row }">{{ row.head_teacher_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="student_count" label="班级人数" width="100" align="center" />
        <el-table-column prop="enroll_year" label="入学年份" width="100" align="center" />
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
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="班级名称" prop="name">
          <el-input v-model="form.name" placeholder="如 一年级1班" />
        </el-form-item>
        <el-form-item label="班级编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入班级编码" />
        </el-form-item>
        <el-form-item label="所属年级" prop="grade_id">
          <el-select v-model="form.grade_id" placeholder="请选择年级" style="width: 100%">
            <el-option v-for="item in gradeOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="教室" prop="room">
          <el-input v-model="form.room" placeholder="请输入教室" />
        </el-form-item>
        <el-form-item label="班主任" prop="head_teacher_id">
          <el-select v-model="form.head_teacher_id" placeholder="可不选" clearable filterable style="width: 100%">
            <el-option v-for="item in teacherOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="入学年份" prop="enroll_year">
          <el-input-number v-model="form.enroll_year" :min="2000" :max="2100" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注" />
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
import { createClass, deleteClass, listClasses, updateClass } from '@/api/class'
import { listGradeOptions } from '@/api/grade'
import { listTeacherOptions } from '@/api/teacher'
import type { ClassInfo, OptionItem } from '@/types/api'

const loading = ref(false)
const list = ref<ClassInfo[]>([])
const total = ref(0)
const query = reactive<{ page: number; page_size: number; keyword: string; grade_id: number | undefined }>({
  page: 1,
  page_size: 10,
  keyword: '',
  grade_id: undefined
})
const gradeOptions = ref<OptionItem[]>([])
const teacherOptions = ref<OptionItem[]>([])

const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const editId = ref<number | null>(null)
const dialogTitle = computed(() => (editId.value ? '编辑班级' : '新增班级'))

const form = reactive<{
  name: string
  code: string
  grade_id: number | undefined
  room: string
  head_teacher_id: number | null
  enroll_year: number | null
  remark: string
}>({
  name: '',
  code: '',
  grade_id: undefined,
  room: '',
  head_teacher_id: null,
  enroll_year: null,
  remark: ''
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入班级名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入班级编码', trigger: 'blur' }],
  grade_id: [{ required: true, message: '请选择所属年级', trigger: 'change' }]
}

/** 学段对应标签颜色 */
function stageTagType(stage: string) {
  if (stage === '小学') return 'success'
  if (stage === '初中') return 'warning'
  return 'danger'
}

/** 加载班级分页列表 */
async function loadList() {
  loading.value = true
  try {
    const res = await listClasses({
      page: query.page,
      page_size: query.page_size,
      keyword: query.keyword || undefined,
      grade_id: query.grade_id
    })
    list.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

/** 加载年级与班主任下拉选项 */
async function loadOptions() {
  const [grades, teachers] = await Promise.all([listGradeOptions(), listTeacherOptions()])
  gradeOptions.value = grades
  teacherOptions.value = teachers
}

function handleSearch() {
  query.page = 1
  loadList()
}

function handleReset() {
  query.keyword = ''
  query.grade_id = undefined
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
  form.name = ''
  form.code = ''
  form.grade_id = undefined
  form.room = ''
  form.head_teacher_id = null
  form.enroll_year = null
  form.remark = ''
  formRef.value?.clearValidate()
}

function openCreate() {
  editId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: ClassInfo) {
  editId.value = row.id
  form.name = row.name
  form.code = row.code
  form.grade_id = row.grade_id
  form.room = row.room || ''
  form.head_teacher_id = row.head_teacher_id
  form.enroll_year = row.enroll_year
  form.remark = row.remark || ''
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const payload = {
      name: form.name,
      code: form.code,
      grade_id: form.grade_id as number,
      room: form.room,
      head_teacher_id: form.head_teacher_id,
      enroll_year: form.enroll_year,
      remark: form.remark
    }
    if (editId.value) {
      await updateClass(editId.value, payload)
      ElMessage.success('修改成功')
    } else {
      await createClass(payload)
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

async function handleDelete(row: ClassInfo) {
  try {
    await ElMessageBox.confirm(`确定删除班级「${row.name}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch {
    return
  }

  try {
    await deleteClass(row.id)
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
