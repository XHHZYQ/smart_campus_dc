/**
 * 前后端接口契约类型定义。
 * 与后端 backend/app/schemas.py 一一对应，改动时需同步修改。
 */

/** 通用分页返回结构 */
export interface PageResult<T> {
  total: number
  items: T[]
}

/** 通用消息返回结构 */
export interface MessageOut {
  message: string
}

/** 名称-数值对（图表用） */
export interface NameValue {
  name: string
  value: number
}

/** 下拉选项：id + 名称的精简结构 */
export interface OptionItem {
  id: number
  name: string
}

/* ---------------- 认证 ---------------- */

export interface LoginRequest {
  username: string
  password: string
}

export interface UserProfile {
  id: number
  username: string
  real_name: string
  role_id: number
  role_name: string
  role_code: string
  teacher_id: number | null
  phone: string | null
  email: string | null
  status: string
  last_login_at: string | null
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: UserProfile
  menus: string[]
}

/* ---------------- 系统管理 ---------------- */

export interface Role {
  id: number
  name: string
  code: string
  description: string | null
  sort_order: number
  created_at: string | null
}

export interface User {
  id: number
  username: string
  real_name: string
  role_id: number
  role_name: string
  teacher_id: number | null
  phone: string | null
  email: string | null
  status: string
  last_login_at: string | null
  created_at: string | null
}

export interface OperationLog {
  id: number
  username: string | null
  real_name: string | null
  module: string | null
  action: string | null
  method: string | null
  path: string | null
  ip: string | null
  detail: string | null
  success: boolean
  created_at: string | null
}

export interface LoginLog {
  id: number
  username: string | null
  ip: string | null
  user_agent: string | null
  success: boolean
  message: string | null
  created_at: string | null
}

/* ---------------- 基础数据 ---------------- */

export interface Department {
  id: number
  name: string
  code: string
  dept_type: string
  leader: string | null
  phone: string | null
  sort_order: number
  remark: string | null
  created_at: string | null
}

export interface Grade {
  id: number
  name: string
  code: string
  stage: string
  grade_level: number
  head_teacher_id: number | null
  head_teacher_name: string
  class_count: number
  created_at: string | null
}

export interface ClassInfo {
  id: number
  name: string
  code: string
  grade_id: number
  grade_name: string
  stage: string
  room: string | null
  head_teacher_id: number | null
  head_teacher_name: string
  student_count: number
  enroll_year: number | null
  remark: string | null
  created_at: string | null
}

export interface Semester {
  id: number
  name: string
  academic_year: string
  term: number
  start_date: string | null
  end_date: string | null
  is_current: boolean
  created_at: string | null
}

export interface Student {
  id: number
  student_no: string
  name: string
  used_name: string | null
  gender: string
  nation: string
  birth_date: string | null
  id_card: string | null
  political_status: string | null
  phone: string | null
  address: string | null
  class_id: number | null
  class_name: string
  grade_name: string
  enroll_year: number | null
  study_mode: string
  status: string
  father_name: string | null
  father_id_card: string | null
  father_work_unit: string | null
  father_position: string | null
  father_phone: string | null
  mother_name: string | null
  mother_id_card: string | null
  mother_work_unit: string | null
  mother_position: string | null
  mother_phone: string | null
  remark: string | null
  created_at: string | null
}

export interface Teacher {
  id: number
  teacher_no: string
  name: string
  gender: string
  department_id: number | null
  department_name: string
  subject: string | null
  title: string | null
  phone: string | null
  email: string | null
  hire_date: string | null
  status: string
  remark: string | null
  created_at: string | null
}

/* ---------------- 教学管理 ---------------- */

export interface Course {
  id: number
  code: string
  name: string
  stage: string
  department_id: number | null
  department_name: string
  weekly_hours: number
  course_type: string
  teacher_id: number | null
  teacher_name: string
  created_at: string | null
}

export interface Schedule {
  id: number
  semester_id: number
  semester_name: string
  class_id: number
  class_name: string
  course_id: number
  course_name: string
  teacher_id: number | null
  teacher_name: string
  weekday: number
  period: number
  room: string | null
  created_at: string | null
}

export interface TimetableCell {
  weekday: number
  period: number
  course_name: string
  teacher_name: string
  room: string
}

export interface Score {
  id: number
  student_id: number
  student_no: string
  student_name: string
  class_name: string
  course_id: number
  course_name: string
  semester_id: number
  semester_name: string
  exam_type: string
  score: number | null
  remark: string | null
  created_at: string | null
}

export interface BatchScoreItem {
  student_id: number
  score: number | null
  remark: string | null
}

export interface BatchScoreRequest {
  class_id: number
  course_id: number
  semester_id: number
  exam_type: string
  items: BatchScoreItem[]
}

export interface Attendance {
  id: number
  student_id: number
  student_no: string
  student_name: string
  class_name: string
  course_id: number
  course_name: string
  attend_date: string
  status: string
  remark: string | null
  created_at: string | null
}

/* ---------------- 校务管理 ---------------- */

export interface Asset {
  id: number
  asset_no: string
  name: string
  category: string
  brand: string | null
  model: string | null
  price: number | null
  quantity: number
  purchase_date: string | null
  department_id: number | null
  department_name: string
  keeper: string | null
  status: string
  location: string | null
  created_at: string | null
}

export interface DormRoom {
  id: number
  building: string
  room_no: string
  floor: number | null
  capacity: number
  occupied: number
  gender_type: string
  remark: string | null
  created_at: string | null
}

export interface DormAllocation {
  id: number
  student_id: number
  student_no: string
  student_name: string
  class_name: string
  room_id: number
  building: string
  room_no: string
  bed_no: string | null
  check_in_date: string | null
  status: string
  created_at: string | null
}

/* ---------------- 数据看板 ---------------- */

export interface Overview {
  student_total: number
  teacher_total: number
  class_total: number
  grade_total: number
  asset_count: number
  asset_amount: number
  dorm_room_total: number
  dorm_bed_total: number
  dorm_occupied: number
  current_semester: string
}

export interface StudentComposition {
  by_stage: NameValue[]
  by_grade: NameValue[]
  by_gender: NameValue[]
  by_study_mode: NameValue[]
  by_status: NameValue[]
}

export interface ScoreDistributionItem {
  range_name: string
  count: number
}

export interface CourseScoreItem {
  course_name: string
  average: number
  pass_rate: number
  excellent_rate: number
  count: number
}

export interface ScoreAnalysis {
  by_course: CourseScoreItem[]
  distribution: ScoreDistributionItem[]
  semester_trend: NameValue[]
}

export interface AssetStatistics {
  by_category: NameValue[]
  by_department: NameValue[]
  by_status: NameValue[]
  amount_by_category: NameValue[]
}

export interface ScreenData {
  student_total: number
  teacher_total: number
  class_total: number
  asset_amount: number
  by_stage: NameValue[]
  by_grade: NameValue[]
  by_gender: NameValue[]
  asset_by_category: NameValue[]
  avg_score_by_course: NameValue[]
  attendance_by_status: NameValue[]
}
