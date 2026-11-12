/**
 * 登录用户状态管理。
 * 保存令牌、用户信息与可访问菜单编码。
 * 用户信息与菜单同时写入 localStorage，保证刷新页面后登录态不丢失。
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, getProfile } from '@/api/auth'
import type { LoginRequest, UserProfile } from '@/types/api'
import { getToken, removeToken, setToken } from '@/utils/request'

const USER_KEY = 'smart_campus_user'
const MENU_KEY = 'smart_campus_menus'

/** 从 localStorage 读取用户信息 */
function readUser(): UserProfile | null {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as UserProfile
  } catch {
    return null
  }
}

/** 从 localStorage 读取菜单编码 */
function readMenus(): string[] {
  const raw = localStorage.getItem(MENU_KEY)
  if (!raw) return []
  try {
    return JSON.parse(raw) as string[]
  } catch {
    return []
  }
}

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(getToken())
  const userInfo = ref<UserProfile | null>(readUser())
  const menus = ref<string[]>(readMenus())

  /** 登录：保存令牌、用户信息与菜单 */
  async function login(payload: LoginRequest) {
    const data = await loginApi(payload)
    token.value = data.access_token
    userInfo.value = data.user
    menus.value = data.menus || []
    setToken(data.access_token)
    localStorage.setItem(USER_KEY, JSON.stringify(data.user))
    localStorage.setItem(MENU_KEY, JSON.stringify(menus.value))
    return data
  }

  /** 拉取当前用户信息（刷新页面后恢复登录态） */
  async function fetchProfile() {
    const data = await getProfile()
    userInfo.value = data
    localStorage.setItem(USER_KEY, JSON.stringify(data))
    return data
  }

  /** 退出登录 */
  function logout() {
    token.value = ''
    userInfo.value = null
    menus.value = []
    removeToken()
    localStorage.removeItem(USER_KEY)
    localStorage.removeItem(MENU_KEY)
  }

  /** 判断是否有权访问某个菜单 */
  function hasMenu(code: string): boolean {
    return menus.value.includes(code)
  }

  return { token, userInfo, menus, login, fetchProfile, logout, hasMenu }
})
