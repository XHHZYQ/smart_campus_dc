<template>
  <div class="page-container">
    <el-row :gutter="16">
      <el-col :span="12">
        <div class="sc-card">
          <h3 class="page-title">个人信息</h3>
          <p class="page-desc">当前登录账号的基本资料</p>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="登录账号">
              {{ userStore.userInfo?.username || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="姓名">
              {{ userStore.userInfo?.real_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="所属角色">
              {{ userStore.userInfo?.role_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="联系电话">
              {{ userStore.userInfo?.phone || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="电子邮箱">
              {{ userStore.userInfo?.email || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="上次登录">
              {{ userStore.userInfo?.last_login_at || '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-col>

      <el-col :span="12">
        <div class="sc-card">
          <h3 class="page-title">修改密码</h3>
          <p class="page-desc">修改后需使用新密码重新登录</p>
          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            label-width="90px"
            style="max-width: 420px"
          >
            <el-form-item label="原密码" prop="old_password">
              <el-input v-model="form.old_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="form.new_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm_password">
              <el-input v-model="form.confirm_password" type="password" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loading" @click="handleSubmit">
                保存修改
              </el-button>
              <el-button @click="handleReset">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { changePassword } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const rules: FormRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 4, message: '密码长度不少于 4 位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== form.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

function handleReset() {
  formRef.value?.resetFields()
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await changePassword({
      old_password: form.old_password,
      new_password: form.new_password
    })
    ElMessage.success(res.message)
    userStore.logout()
    router.push('/login')
  } finally {
    loading.value = false
  }
}
</script>
