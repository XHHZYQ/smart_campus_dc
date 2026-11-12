<template>
  <div class="page-container">
    <div class="sc-card">
      <!-- 搜索栏 -->
      <el-form :inline="true" class="search-bar" @submit.prevent>
        <el-form-item label="关键字">
          <el-input
            v-model="query.keyword"
            placeholder="年级名称 / 编码"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="学段">
          <el-select v-model="query.stage" placeholder="全部学段" clearable style="width: 140px">
            <el-option label="小学" value="小学" />
            <el-option label="初中" value="初中" />
            <el-option label="高中" value="高中" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格工具栏 -->
      <div class="table-toolbar">
        <span class="title">年级列表</span>
        <el-button type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon> 新增年级
        </el-button>
      </div>

      <!-- 数据表格 -->
      <el-table v-loading="loading" :data="list" border stripe>
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column prop="name" label="年级名称" min-width="130" />
        <el-table-column prop="code" label="年级编码" min-width="120" />
        <el-table-column label="学段" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="stageTagType(row.stage)">{{ row.stage }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="grade_level" label="年级序号" width="100" align="center" />
        <el-table-column prop="head_teacher_name" label="年级组长" min-width="120">
          <template #default="{ row }">{{ row.head_teacher_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="class_count" label="班级数" width="90" align="center" />
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="520px" @closed="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="年级名称" prop="name">
          <el-input v-model="form.name" placeholder="如 一年级、初一" />
        </el-form-item>
        <el-form-item label="年级编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入年级编码" />
        </el-form-item>
        <el-form-item label="所属学段" prop="stage">
          <el-radio-group v-model="form.stage">
            <el-radio label="小学">小学</el-radio>
            <el-radio label="初中">初中</el-radio>
            <el-radio label="高中">高中</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="年级序号" prop="grade_level">
          <el-input-number v-model="form.grade_level" :min="1" :max="12" />
        </el-form-item>
        <el-form-item label="年级组长" prop="head_teacher_id">
          <el-select v-model="form.head_teacher_id" placeholder="可不选" clearable filterable style="width: 100%">
            <el-option v-for="item in teacherOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
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
import { createGrade, deleteGrade, listGrades, updateGrade } from '@/api/grade'
import { listTeacherOptions } from '@/api/teacher'
import type { Grade, OptionItem } from '@/types/api'

const loading = ref(false)
const list = ref<Grade[]>([])
const total = ref(0)
const query = reactive<{ page: number; page_size: number; keyword: string; stage: string }>({
  page: 1,
  page_size: 10,
  keyword: '',
  stage: ''
})
const teacherOptions = ref<OptionItem[]>([])

const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const editId = ref<number | null>(null)
const dialogTitle = computed(() => (editId.value ? '编辑年级' : '新增年级'))

const form = reactive<{
  name: string
  code: string
  stage: string
  grade_level: number
  head_teacher_id: number | null
}>({
  name: '',
  code: '',
  stage: '小学',
  grade_level: 1,
  head_teacher_id: null
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入年级名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入年级编码', trigger: 'blur' }],
  stage: [{ required: true, message: '请选择所属学段', trigger: 'change' }],
  grade_level: [{ required: true, message: '请输入年级序号', trigger: 'blur' }]
}

/** 学段对应标签颜色 */
function stageTagType(stage: string) {
  if (stage === '小学') return 'success'
  if (stage === '初中') return 'warning'
  return 'danger'
}

/** 加载年级分页列表 */
async function loadList() {
  loading.value = true
  try {
    const res = await listGrades({
      page: query.page,
      page_size: query.page_size,
      keyword: query.keyword || undefined,
      stage: query.stage || undefined
    })
    list.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

/** 加载年级组长候选（教职工选项） */
async function loadOptions() {
  teacherOptions.value = await listTeacherOptions()
}

function handleSearch() {
  query.page = 1
  loadList()
}

function handleReset() {
  query.keyword = ''
  query.stage = ''
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
  form.stage = '小学'
  form.grade_level = 1
  form.head_teacher_id = null
  formRef.value?.clearValidate()
}

function openCreate() {
  editId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: Grade) {
  editId.value = row.id
  form.name = row.name
  form.code = row.code
  form.stage = row.stage
  form.grade_level = row.grade_level
  form.head_teacher_id = row.head_teacher_id
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (editId.value) {
      await updateGrade(editId.value, { ...form })
      ElMessage.success('修改成功')
    } else {
      await createGrade({ ...form })
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

async function handleDelete(row: Grade) {
  try {
    await ElMessageBox.confirm(`确定删除年级「${row.name}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch {
    return
  }

  try {
    await deleteGrade(row.id)
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
