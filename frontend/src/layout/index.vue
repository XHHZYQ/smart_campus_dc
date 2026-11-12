<template>
  <div class="layout">
    <!-- 左侧菜单 -->
    <aside class="sidebar">
      <div class="logo">
        <el-icon class="logo-icon"><School /></el-icon>
        <div class="logo-text">
          <div class="cn">智慧校园数据中心</div>
          <div class="en">CAMPUS DATA CENTER</div>
        </div>
      </div>

      <el-menu
        :default-active="activeMenu"
        background-color="transparent"
        text-color="#c3ccdb"
        active-text-color="#ffffff"
        :collapse="false"
        router
        class="side-menu"
      >
        <template v-for="group in visibleGroups" :key="group.title">
          <!-- 只有一个子项的分组直接展示为一级菜单 -->
          <el-menu-item
            v-if="group.children.length === 1"
            :index="group.children[0].path"
          >
            <el-icon><component :is="group.children[0].icon || group.icon" /></el-icon>
            <span>{{ group.children[0].title }}</span>
          </el-menu-item>

          <el-sub-menu v-else :index="group.title">
            <template #title>
              <el-icon><component :is="group.icon" /></el-icon>
              <span>{{ group.title }}</span>
            </template>
            <el-menu-item
              v-for="item in group.children"
              :key="item.path"
              :index="item.path"
            >
              <el-icon><component :is="item.icon || 'Document'" /></el-icon>
              <span>{{ item.title }}</span>
            </el-menu-item>
          </el-sub-menu>
        </template>
      </el-menu>
    </aside>

    <!-- 右侧主体 -->
    <div class="main">
      <header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="toggleCollapse">
            <Fold v-if="!collapsed" />
            <Expand v-else />
          </el-icon>
          <span class="current-title">{{ route.meta.title || '' }}</span>
        </div>

        <div class="header-right">
          <el-tag type="success" effect="plain" size="small">
            {{ userStore.userInfo?.role_name || '未登录' }}
          </el-tag>
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="30" class="avatar">
                {{ (userStore.userInfo?.real_name || 'U').charAt(0) }}
              </el-avatar>
              <span class="name">{{ userStore.userInfo?.real_name || '未登录' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <main class="content">
        <router-view v-slot="{ Component }">
          <keep-alive :max="10">
            <component :is="Component" />
          </keep-alive>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { menuGroups, type MenuItem, type MenuGroup } from '@/router/menu'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const collapsed = ref(false)

const activeMenu = computed(() => route.path)

/** 只显示：角色有权限 + 路由已注册 的菜单项 */
const visibleGroups = computed<MenuGroup[]>(() => {
  const registered = new Set(router.getRoutes().map((item) => item.path))
  return menuGroups
    .map((group) => ({
      ...group,
      children: group.children.filter(
        (child: MenuItem) =>
          userStore.hasMenu(child.code) && registered.has(child.path)
      )
    }))
    .filter((group) => group.children.length > 0)
})

function toggleCollapse() {
  collapsed.value = !collapsed.value
  const sidebar = document.querySelector('.sidebar')
  sidebar?.classList.toggle('collapsed')
}

function handleCommand(command: string) {
  if (command === 'profile') {
    router.push('/profile')
    return
  }
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      userStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    })
  }
}
</script>

<style scoped>
.layout {
  display: flex;
  height: 100%;
}

/* ------- 左侧菜单 ------- */
.sidebar {
  width: var(--sc-sidebar-width);
  flex-shrink: 0;
  background: var(--sc-sidebar-bg);
  display: flex;
  flex-direction: column;
  transition: width 0.2s;
  overflow: hidden;
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar.collapsed .logo-text,
.sidebar.collapsed :deep(.el-menu-item span),
.sidebar.collapsed :deep(.el-sub-menu__title span) {
  display: none;
}

.logo {
  height: var(--sc-header-height);
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
}

.logo-icon {
  font-size: 26px;
  color: #4d9bf5;
}

.logo-text .cn {
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 1px;
  white-space: nowrap;
}

.logo-text .en {
  color: #7f8b9e;
  font-size: 9px;
  letter-spacing: 1px;
  white-space: nowrap;
}

.side-menu {
  border-right: none;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.side-menu :deep(.el-menu-item),
.side-menu :deep(.el-sub-menu__title) {
  height: 46px;
  line-height: 46px;
  font-size: 14px;
}

.side-menu :deep(.el-menu-item.is-active) {
  background: var(--sc-sidebar-bg-active) !important;
  border-right: 3px solid #7fc0ff;
}

.side-menu :deep(.el-menu-item:hover),
.side-menu :deep(.el-sub-menu__title:hover) {
  background: rgba(255, 255, 255, 0.06) !important;
}

/* ------- 右侧主体 ------- */
.main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.header {
  height: var(--sc-header-height);
  background: #fff;
  border-bottom: 1px solid #e6ebf2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #5a6a80;
}

.current-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2a3c;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  outline: none;
}

.avatar {
  background: var(--sc-primary);
  color: #fff;
  font-size: 14px;
}

.user-info .name {
  font-size: 14px;
  color: #303133;
}

.content {
  flex: 1;
  overflow: auto;
  padding: 16px;
}
</style>
