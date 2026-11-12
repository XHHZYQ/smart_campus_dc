/**
 * 路由配置与登录守卫。
 * 未登录访问业务页面会被重定向到登录页。
 */
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { getToken } from '@/utils/request'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: () => import('@/layout/index.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/overview.vue'),
        meta: { title: '首页概览', menu: 'dashboard' }
      },
      {
        path: 'dashboard/student-composition',
        name: 'DashboardStudent',
        component: () => import('@/views/dashboard/student-composition.vue'),
        meta: { title: '学生构成分析', menu: 'dashboard:student' }
      },
      {
        path: 'dashboard/score-analysis',
        name: 'DashboardScore',
        component: () => import('@/views/dashboard/score-analysis.vue'),
        meta: { title: '成绩分析', menu: 'dashboard:score' }
      },
      {
        path: 'dashboard/asset-statistics',
        name: 'DashboardAsset',
        component: () => import('@/views/dashboard/asset-statistics.vue'),
        meta: { title: '资产统计', menu: 'dashboard:asset' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/profile/index.vue'),
        meta: { title: '个人中心' }
      },
      {
        path: 'system/users',
        name: 'SystemUsers',
        component: () => import('@/views/system/users/index.vue'),
        meta: { title: '用户管理', menu: 'system:user' }
      },
      {
        path: 'system/roles',
        name: 'SystemRoles',
        component: () => import('@/views/system/roles/index.vue'),
        meta: { title: '角色管理', menu: 'system:role' }
      },
      {
        path: 'system/operation-logs',
        name: 'SystemOperationLogs',
        component: () => import('@/views/system/operation-logs/index.vue'),
        meta: { title: '操作日志', menu: 'system:operation-log' }
      },
      {
        path: 'system/login-logs',
        name: 'SystemLoginLogs',
        component: () => import('@/views/system/login-logs/index.vue'),
        meta: { title: '登录日志', menu: 'system:login-log' }
      },
      {
        path: 'base/departments',
        name: 'BaseDepartments',
        component: () => import('@/views/base/departments/index.vue'),
        meta: { title: '部门管理', menu: 'base:department' }
      },
      {
        path: 'base/grades',
        name: 'BaseGrades',
        component: () => import('@/views/base/grades/index.vue'),
        meta: { title: '年级管理', menu: 'base:grade' }
      },
      {
        path: 'base/classes',
        name: 'BaseClasses',
        component: () => import('@/views/base/classes/index.vue'),
        meta: { title: '班级管理', menu: 'base:class' }
      },
      {
        path: 'base/semesters',
        name: 'BaseSemesters',
        component: () => import('@/views/base/semesters/index.vue'),
        meta: { title: '学期管理', menu: 'base:semester' }
      },
      {
        path: 'base/students',
        name: 'BaseStudents',
        component: () => import('@/views/base/students/index.vue'),
        meta: { title: '学生学籍', menu: 'base:student' }
      },
      {
        path: 'base/teachers',
        name: 'BaseTeachers',
        component: () => import('@/views/base/teachers/index.vue'),
        meta: { title: '教职工档案', menu: 'base:teacher' }
      },
      {
        path: 'edu/courses',
        name: 'EduCourses',
        component: () => import('@/views/edu/courses/index.vue'),
        meta: { title: '学科课程', menu: 'edu:course' }
      },
      {
        path: 'edu/schedules',
        name: 'EduSchedules',
        component: () => import('@/views/edu/schedules/index.vue'),
        meta: { title: '排课管理', menu: 'edu:schedule' }
      },
      {
        path: 'edu/scores',
        name: 'EduScores',
        component: () => import('@/views/edu/scores/index.vue'),
        meta: { title: '成绩管理', menu: 'edu:score' }
      },
      {
        path: 'edu/attendances',
        name: 'EduAttendances',
        component: () => import('@/views/edu/attendances/index.vue'),
        meta: { title: '考勤记录', menu: 'edu:attendance' }
      },
      {
        path: 'af/assets',
        name: 'AfAssets',
        component: () => import('@/views/af/assets/index.vue'),
        meta: { title: '资产台账', menu: 'af:asset' }
      },
      {
        path: 'af/dorms',
        name: 'AfDorms',
        component: () => import('@/views/af/dorms/index.vue'),
        meta: { title: '宿舍管理', menu: 'af:dorm' }
      }
    ]
  },
  {
    // 数据大屏：全屏深色看板，独立于 layout 之外的顶层路由
    path: '/dashboard/screen',
    name: 'DashboardScreen',
    component: () => import('@/views/dashboard/screen.vue'),
    meta: { title: '数据大屏', menu: 'dashboard:screen' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '页面不存在' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  document.title = to.meta.title
    ? `${to.meta.title} - 智慧校园数据中心管理软件`
    : '智慧校园数据中心管理软件'

  const token = getToken()
  if (to.path === '/login') {
    next(token ? '/' : undefined)
    return
  }
  if (!token) {
    next('/login')
    return
  }
  next()
})

export default router
