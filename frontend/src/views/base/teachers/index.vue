<template>
  <div class="page-container">
    <div class="sc-card">
      <!-- 搜索栏 -->
      <el-form :inline="true" class="search-bar" @submit.prevent>
        <el-form-item label="关键字">
          <el-input
            v-model="query.keyword"
            placeholder="工号 / 姓名 / 电话"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="query.department_id" placeholder="全部部门" clearable style="width: 160px">
            <el-option v-for="item in departmentOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="query.status" placeholder="全部状态" clearable style="width: 130px">
            <el-option label="在职" value="在职" />
            <el-option label="离职" value="离职" />
            <el-option label="退休" value="退休" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格工具栏 -->
      <div class="table-toolbar">
        <span class="title">教职工列表</span>
        <el-button type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon> 新增教职工
        </el-button>
      </div>

      <!-- 数据表格 -->
      <el-table v-loading="loading" :data="list" border stripe>
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column prop="teacher_no" label="工号" min-width="120" />
        <el-table-column prop="name" label="姓名" min-width="100" />
        <el-table-column label="性别" width="80" align="center">
          <template #default="{ row }">{{ row.gender }}</template>
        </el-table-column>
        <el-table-column prop="department_name" label="所属部门" min-width="130">
          <template #default="{ row }">{{ row.department_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="subject" label="任教学科" min-width="110" />
        <el-table-column prop="title" label="职称" min-width="110" />
        <el-table-column prop="phone" label="联系电话" min-width="130" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">{{ row.status }}</el-tag>
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" @closed="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="工号" prop="teacher_no">
              <el-input v-model="form.teacher_no" placeholder="请输入工号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="form.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="form.gender">
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属部门" prop="department_id">
              <el-select v-model="form.department_id" placeholder="请选择部门" clearable style="width: 100%">
                <el-option v-for="item in departmentOptions" :key="item.id" :label="item.name" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="任教学科" prop="subject">
              <el-input v-model="form.subject" placeholder="如 语文" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职称" prop="title">
              <el-input v-model="form.title" placeholder="如 一级教师" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="form.phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="电子邮箱" prop="email">
              <el-input v-model="form.email" placeholder="请输入电子邮箱" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="入职日期" prop="hire_date">
              <el-date-picker
                v-model="form.hire_date"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="请选择入职日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="在职状态" prop="status">
              <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
                <el-option label="在职" value="在职" />
                <el-option label="离职" value="离职" />
                <el-option label="退休" value="退休" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="备注" prop="remark">
              <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注" />
            </el-form-item>
          </el-col>
        </el-row>
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
import { createTeacher, deleteTeacher, listTeachers, updateTeacher } from '@/api/teacher'
import { listDepartmentOptions } from '@/api/department'
import type { OptionItem, Teacher } from '@/types/api'

const loading = ref(false)
const list = ref<Teacher[]>([])
const total = ref(0)
const query = reactive<{
  page: number
  page_size: number
  keyword: string
  department_id: number | undefined
  status: string
}>({
  page: 1,
  page_size: 10,
  keyword: '',
  department_id: undefined,
  status: ''
})
const departmentOptions = ref<OptionItem[]>([])

const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const editId = ref<number | null>(null)
const dialogTitle = computed(() => (editId.value ? '编辑教职工' : '新增教职工'))

const form = reactive<{
  teacher_no: string
  name: string
  gender: string
  department_id: number | null
  subject: string
  title: string
  phone: string
  email: string
  hire_date: string | null
  status: string
  remark: string
}>({
  teacher_no: '',
  name: '',
  gender: '男',
  department_id: null,
  subject: '',
  title: '',
  phone: '',
  email: '',
  hire_date: null,
  status: '在职',
  remark: ''
})

const rules: FormRules = {
  teacher_no: [{ required: true, message: '请输入工号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  status: [{ required: true, message: '请选择在职状态', trigger: 'change' }]
}

/** 在职状态标签颜色 */
function statusTagType(status: string) {
  if (status === '在职') return 'success'
  if (status === '离职') return 'warning'
  return 'info'
}

/** 加载教职工分页列表 */
async function loadList() {
  loading.value = true
  try {
    const res = await listTeachers({
      page: query.page,
      page_size: query.page_size,
      keyword: query.keyword || undefined,
      department_id: query.department_id,
      status: query.status || undefined
    })
    list.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

/** 加载部门下拉选项 */
async function loadOptions() {
  departmentOptions.value = await listDepartmentOptions()
}

function handleSearch() {
  query.page = 1
  loadList()
}

function handleReset() {
  query.keyword = ''
  query.department_id = undefined
  query.status = ''
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
  form.teacher_no = ''
  form.name = ''
  form.gender = '男'
  form.department_id = null
  form.subject = ''
  form.title = ''
  form.phone = ''
  form.email = ''
  form.hire_date = null
  form.status = '在职'
  form.remark = ''
  formRef.value?.clearValidate()
}

function openCreate() {
  editId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: Teacher) {
  editId.value = row.id
  form.teacher_no = row.teacher_no
  form.name = row.name
  form.gender = row.gender
  form.department_id = row.department_id
  form.subject = row.subject || ''
  form.title = row.title || ''
  form.phone = row.phone || ''
  form.email = row.email || ''
  form.hire_date = row.hire_date
  form.status = row.status
  form.remark = row.remark || ''
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (editId.value) {
      await updateTeacher(editId.value, { ...form })
      ElMessage.success('修改成功')
    } else {
      await createTeacher({ ...form })
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

async function handleDelete(row: Teacher) {
  try {
    await ElMessageBox.confirm(`确定删除教职工「${row.name}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch {
    return
  }

  try {
    await deleteTeacher(row.id)
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
