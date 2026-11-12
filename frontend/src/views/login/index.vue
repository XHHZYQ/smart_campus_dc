<template>
  <div class="login-page">
    <div class="login-box">
      <!-- 左侧介绍区 -->
      <div class="intro">
        <div class="intro-inner">
          <el-icon class="intro-icon"><School /></el-icon>
          <h1>智慧校园数据中心</h1>
          <p class="sub">CAMPUS DATA CENTER</p>
          <ul class="feature-list">
            <li><el-icon><Select /></el-icon> 学生学籍与教职工档案统一管理</li>
            <li><el-icon><Select /></el-icon> 课程排课、成绩与考勤一体化</li>
            <li><el-icon><Select /></el-icon> 资产台账与宿舍住宿统计</li>
            <li><el-icon><Select /></el-icon> 数据看板与可视化大屏</li>
          </ul>
        </div>
      </div>

      <!-- 右侧登录表单 -->
      <div class="form-area">
        <h2 class="form-title">用户登录</h2>
        <p class="form-sub">欢迎使用智慧校园数据中心管理软件</p>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          size="large"
          @submit.prevent
          @keyup.enter="handleLogin"
        >
          <el-form-item label="账号" prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入登录账号"
              clearable
              :prefix-icon="User"
            />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入登录密码"
              show-password
              :prefix-icon="Lock"
            />
          </el-form-item>

          <el-button
            type="primary"
            class="login-btn"
            size="large"
            native-type="button"
            :loading="loading"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form>

        <div class="demo-tip">
          <div class="tip-title">演示账号</div>
          <div class="tip-line">系统管理员：admin / admin123</div>
          <div class="tip-line">教务管理员：jiaowu / admin123</div>
          <div class="tip-line">班主任：banzhuren / admin123</div>
        </div>
      </div>
    </div>

    <div class="copyright">
      智慧校园数据中心管理软件 V1.0.0 &nbsp;|&nbsp; 面向小学、初中、高中学校
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Lock, User } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import type { LoginRequest } from '@/types/api'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive<LoginRequest>({
  username: '',
  password: ''
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入登录账号', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入登录密码', trigger: 'blur' },
    { min: 4, message: '密码长度不少于 4 位', trigger: 'blur' }
  ]
}

async function handleLogin() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await userStore.login({ ...form })
    ElMessage.success('登录成功，欢迎回来')
    router.push('/')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(circle at 15% 20%, rgba(26, 111, 212, 0.35), transparent 45%),
    radial-gradient(circle at 85% 80%, rgba(23, 168, 148, 0.3), transparent 45%),
    linear-gradient(135deg, #16243a 0%, #1f3350 55%, #223a5c 100%);
  position: relative;
}

.login-box {
  width: 940px;
  max-width: 94vw;
  min-height: 500px;
  display: flex;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.35);
  background: #fff;
}

/* 左侧介绍 */
.intro {
  width: 46%;
  background: linear-gradient(160deg, #1a6fd4 0%, #12508f 100%);
  color: #fff;
  display: flex;
  align-items: center;
  padding: 40px 34px;
}

.intro-icon {
  font-size: 44px;
  margin-bottom: 14px;
  color: #9ed0ff;
}

.intro h1 {
  font-size: 24px;
  margin: 0;
  letter-spacing: 2px;
}

.intro .sub {
  font-size: 11px;
  letter-spacing: 3px;
  color: rgba(255, 255, 255, 0.65);
  margin: 6px 0 30px;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.feature-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13.5px;
  color: rgba(255, 255, 255, 0.92);
  padding: 9px 0;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.16);
}

/* 右侧表单 */
.form-area {
  flex: 1;
  padding: 48px 52px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.form-title {
  font-size: 22px;
  color: #1f2a3c;
  margin: 0 0 6px;
}

.form-sub {
  font-size: 13px;
  color: #909399;
  margin: 0 0 26px;
}

.login-btn {
  width: 100%;
  margin-top: 8px;
  letter-spacing: 4px;
  font-size: 15px;
}

.demo-tip {
  margin-top: 26px;
  padding: 12px 14px;
  background: #f5f8fc;
  border: 1px dashed #cfdcec;
  border-radius: 8px;
  font-size: 12.5px;
  color: #5a6a80;
  line-height: 1.9;
}

.tip-title {
  font-weight: 600;
  color: #1a6fd4;
  margin-bottom: 2px;
}

.copyright {
  margin-top: 22px;
  color: rgba(255, 255, 255, 0.55);
  font-size: 12.5px;
}
</style>
