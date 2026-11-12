<template>
  <div class="page-container">
    <div class="sc-card">
      <!-- 搜索栏 -->
      <el-form :inline="true" class="search-bar" @submit.prevent>
        <el-form-item label="关键字">
          <el-input
            v-model="query.keyword"
            placeholder="登录账号 / 姓名"
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
        <span class="title">用户列表</span>
        <el-button type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon> 新增用户
        </el-button>
      </div>

      <!-- 数据表格 -->
      <el-table v-loading="loading" :data="list" border stripe>
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column prop="username" label="登录账号" min-width="130" />
        <el-table-column prop="real_name" label="姓名" min-width="100" />
        <el-table-column prop="role_name" label="所属角色" min-width="120" />
        <el-table-column prop="phone" label="联系电话" min-width="130" />
        <el-table-column prop="email" label="电子邮箱" min-width="180" show-overflow-tooltip />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === '启用' ? 'success' : 'info'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_login_at" label="最后登录" min-width="170" />
        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="warning" @click="handleResetPassword(row)">重置密码</el-button>
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
        <el-form-item label="登录账号" prop="username">
          <el-input v-model="form.username" :disabled="!!editId" placeholder="请输入登录账号" />
        </el-form-item>
        <el-form-item v-if="!editId" label="登录密码" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="请输入登录密码" />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="所属角色" prop="role_id">
          <el-select v-model="form.role_id" placeholder="请选择角色" style="width: 100%">
            <el-option v-for="item in roleOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联教职工" prop="teacher_id">
          <el-select v-model="form.teacher_id" placeholder="可不选" clearable filterable style="width: 100%">
            <el-option v-for="item in teacherOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="电子邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入电子邮箱" />
        </el-form-item>
        <el-form-item label="账号状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="启用">启用</el-radio>
            <el-radio label="停用">停用</el-radio>
          </el-radio-group>
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
  createUser,
  deleteUser,
  listUsers,
  resetUserPassword,
  updateUser,
  type UserForm
} from '@/api/user'
import { listRoleOptions } from '@/api/role'
import { listTeacherOptions } from '@/api/teacher'
import type { OptionItem, User } from '@/types/api'

const loading = ref(false)
const list = ref<User[]>([])
const total = ref(0)
const query = reactive({ page: 1, page_size: 10, keyword: '' })
const roleOptions = ref<OptionItem[]>([])
const teacherOptions = ref<OptionItem[]>([])

const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const editId = ref<number | null>(null)
const dialogTitle = computed(() => (editId.value ? '编辑用户' : '新增用户'))

const form = reactive<{
  username: string
  password: string
  real_name: string
  role_id: number | undefined
  teacher_id: number | null
  phone: string
  email: string
  status: string
}>({
  username: '',
  password: '',
  real_name: '',
  role_id: undefined,
  teacher_id: null,
  phone: '',
  email: '',
  status: '启用'
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入登录账号', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入登录密码', trigger: 'blur' },
    { min: 4, message: '密码长度不少于 4 位', trigger: 'blur' }
  ],
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  role_id: [{ required: true, message: '请选择所属角色', trigger: 'change' }]
}

/** 加载用户分页列表 */
async function loadList() {
  loading.value = true
  try {
    const res = await listUsers(query)
    list.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

/** 加载下拉选项 */
async function loadOptions() {
  const [roles, teachers] = await Promise.all([listRoleOptions(), listTeacherOptions()])
  roleOptions.value = roles
  teacherOptions.value = teachers
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
  form.username = ''
  form.password = ''
  form.real_name = ''
  form.role_id = undefined
  form.teacher_id = null
  form.phone = ''
  form.email = ''
  form.status = '启用'
  formRef.value?.clearValidate()
}

function openCreate() {
  editId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: User) {
  editId.value = row.id
  form.username = row.username
  form.password = ''
  form.real_name = row.real_name
  form.role_id = row.role_id
  form.teacher_id = row.teacher_id
  form.phone = row.phone || ''
  form.email = row.email || ''
  form.status = row.status
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (editId.value) {
      await updateUser(editId.value, {
        real_name: form.real_name,
        role_id: form.role_id as number,
        teacher_id: form.teacher_id,
        phone: form.phone,
        email: form.email,
        status: form.status
      })
      ElMessage.success('修改成功')
    } else {
      const payload: UserForm = {
        username: form.username,
        password: form.password,
        real_name: form.real_name,
        role_id: form.role_id as number,
        teacher_id: form.teacher_id,
        phone: form.phone,
        email: form.email,
        status: form.status
      }
      await createUser(payload)
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

async function handleResetPassword(row: User) {
  try {
    const { value } = await ElMessageBox.prompt(
      `请为用户「${row.real_name}」设置新密码`,
      '重置密码',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputType: 'password',
        inputPlaceholder: '请输入新密码（不少于 4 位）',
        inputValidator: (val: string) => (val && val.length >= 4) || '密码长度不少于 4 位'
      }
    )
    await resetUserPassword(row.id, value)
    ElMessage.success('密码重置成功')
  } catch {
    // 取消或失败均不额外提示
  }
}

async function handleDelete(row: User) {
  try {
    await ElMessageBox.confirm(`确定删除用户「${row.real_name}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch {
    return
  }

  try {
    await deleteUser(row.id)
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
