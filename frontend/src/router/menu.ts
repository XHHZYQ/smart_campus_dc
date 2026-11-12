/**
 * 侧边菜单配置。
 * code 与后端登录返回的 menus 编码一一对应，用于按角色控制菜单显示。
 */

export interface MenuItem {
  code: string
  title: string
  path: string
  icon?: string
}

export interface MenuGroup {
  title: string
  icon: string
  children: MenuItem[]
}

export const menuGroups: MenuGroup[] = [
  {
    title: '首页',
    icon: 'HomeFilled',
    children: [
      { code: 'dashboard', title: '首页概览', path: '/dashboard', icon: 'HomeFilled' }
    ]
  },
  {
    title: '数据看板',
    icon: 'DataLine',
    children: [
      { code: 'dashboard:screen', title: '数据大屏', path: '/dashboard/screen', icon: 'DataBoard' },
      { code: 'dashboard:student', title: '学生构成分析', path: '/dashboard/student-composition', icon: 'PieChart' },
      { code: 'dashboard:score', title: '成绩分析', path: '/dashboard/score-analysis', icon: 'TrendCharts' },
      { code: 'dashboard:asset', title: '资产统计', path: '/dashboard/asset-statistics', icon: 'Histogram' }
    ]
  },
  {
    title: '系统管理',
    icon: 'Setting',
    children: [
      { code: 'system:user', title: '用户管理', path: '/system/users', icon: 'User' },
      { code: 'system:role', title: '角色管理', path: '/system/roles', icon: 'Avatar' },
      { code: 'system:operation-log', title: '操作日志', path: '/system/operation-logs', icon: 'Document' },
      { code: 'system:login-log', title: '登录日志', path: '/system/login-logs', icon: 'Key' }
    ]
  },
  {
    title: '基础数据管理',
    icon: 'Files',
    children: [
      { code: 'base:department', title: '部门管理', path: '/base/departments', icon: 'OfficeBuilding' },
      { code: 'base:grade', title: '年级管理', path: '/base/grades', icon: 'Grid' },
      { code: 'base:class', title: '班级管理', path: '/base/classes', icon: 'School' },
      { code: 'base:semester', title: '学期管理', path: '/base/semesters', icon: 'Calendar' },
      { code: 'base:student', title: '学生学籍', path: '/base/students', icon: 'UserFilled' },
      { code: 'base:teacher', title: '教职工档案', path: '/base/teachers', icon: 'Suitcase' }
    ]
  },
  {
    title: '教学管理',
    icon: 'Notebook',
    children: [
      { code: 'edu:course', title: '学科课程', path: '/edu/courses', icon: 'Collection' },
      { code: 'edu:schedule', title: '排课管理', path: '/edu/schedules', icon: 'AlarmClock' },
      { code: 'edu:score', title: '成绩管理', path: '/edu/scores', icon: 'EditPen' },
      { code: 'edu:attendance', title: '考勤记录', path: '/edu/attendances', icon: 'Finished' }
    ]
  },
  {
    title: '校务管理',
    icon: 'Box',
    children: [
      { code: 'af:asset', title: '资产台账', path: '/af/assets', icon: 'Box' },
      { code: 'af:dorm', title: '宿舍管理', path: '/af/dorms', icon: 'House' }
    ]
  }
]
