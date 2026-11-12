<template>
  <div class="page-container">
    <div class="sc-card">
      <!-- 搜索栏 -->
      <el-form :inline="true" class="search-bar" @submit.prevent>
        <el-form-item label="关键字">
          <el-input
            v-model="query.keyword"
            placeholder="学期名称 / 学年"
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
        <span class="title">学期列表</span>
        <el-button type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon> 新增学期
        </el-button>
      </div>

      <!-- 数据表格 -->
      <el-table v-loading="loading" :data="list" border stripe>
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column prop="name" label="学期名称" min-width="160" />
        <el-table-column prop="academic_year" label="学年" min-width="130" />
        <el-table-column label="学期" width="90" align="center">
          <template #default="{ row }">{{ termText(row.term) }}</template>
        </el-table-column>
        <el-table-column prop="start_date" label="开始日期" min-width="130" />
        <el-table-column prop="end_date" label="结束日期" min-width="130" />
        <el-table-column label="当前学期" width="110" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_current" type="success">是</el-tag>
            <el-tag v-else type="info">否</el-tag>
          </template>
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
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="学期名称" prop="name">
          <el-input v-model="form.name" placeholder="如 2025-2026学年第一学期" />
        </el-form-item>
        <el-form-item label="学年" prop="academic_year">
          <el-input v-model="form.academic_year" placeholder="如 2025-2026" />
        </el-form-item>
        <el-form-item label="学期" prop="term">
          <el-radio-group v-model="form.term">
            <el-radio :label="1">第一学期（秋季）</el-radio>
            <el-radio :label="2">第二学期（春季）</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker
            v-model="form.start_date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="请选择开始日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束日期" prop="end_date">
          <el-date-picker
            v-model="form.end_date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="请选择结束日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="当前学期" prop="is_current">
          <el-switch v-model="form.is_current" />
          <span class="tip">设为当前学期后，其他学期将自动取消</span>
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
import { createSemester, deleteSemester, listSemesters, updateSemester } from '@/api/semester'
import type { Semester } from '@/types/api'

const loading = ref(false)
const list = ref<Semester[]>([])
const total = ref(0)
const query = reactive({ page: 1, page_size: 10, keyword: '' })

const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const editId = ref<number | null>(null)
const dialogTitle = computed(() => (editId.value ? '编辑学期' : '新增学期'))

const form = reactive<{
  name: string
  academic_year: string
  term: number
  start_date: string | null
  end_date: string | null
  is_current: boolean
}>({
  name: '',
  academic_year: '',
  term: 1,
  start_date: null,
  end_date: null,
  is_current: false
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入学期名称', trigger: 'blur' }],
  academic_year: [{ required: true, message: '请输入学年', trigger: 'blur' }],
  term: [{ required: true, message: '请选择学期', trigger: 'change' }]
}

/** 学期序号文案 */
function termText(term: number) {
  return term === 1 ? '第一学期' : '第二学期'
}

/** 加载学期分页列表 */
async function loadList() {
  loading.value = true
  try {
    const res = await listSemesters(query)
    list.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
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
  form.name = ''
  form.academic_year = ''
  form.term = 1
  form.start_date = null
  form.end_date = null
  form.is_current = false
  formRef.value?.clearValidate()
}

function openCreate() {
  editId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: Semester) {
  editId.value = row.id
  form.name = row.name
  form.academic_year = row.academic_year
  form.term = row.term
  form.start_date = row.start_date
  form.end_date = row.end_date
  form.is_current = row.is_current
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (editId.value) {
      await updateSemester(editId.value, { ...form })
      ElMessage.success('修改成功')
    } else {
      await createSemester({ ...form })
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

async function handleDelete(row: Semester) {
  try {
    await ElMessageBox.confirm(`确定删除学期「${row.name}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch {
    return
  }

  try {
    await deleteSemester(row.id)
    ElMessage.success('删除成功')
    loadList()
  } catch {
    // 错误提示由请求拦截器统一处理
  }
}

onMounted(loadList)
</script>

<style scoped>
.tip {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}
</style>
