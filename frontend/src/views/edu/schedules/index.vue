<template>
  <div class="page-container">
    <!-- 周课表 -->
    <div class="sc-card" style="margin-bottom: 16px">
      <div class="table-toolbar">
        <span class="title">周课表</span>
      </div>
      <el-form :inline="true" class="search-bar" @submit.prevent>
        <el-form-item label="查看方式">
          <el-radio-group v-model="timetableMode" @change="handleTimetableModeChange">
            <el-radio label="class">按班级</el-radio>
            <el-radio label="teacher">按教师</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="timetableMode === 'class'" label="班级">
          <el-select v-model="timetableClassId" placeholder="请选择班级" clearable filterable style="width: 180px">
            <el-option v-for="item in classOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item v-else label="教师">
          <el-select v-model="timetableTeacherId" placeholder="请选择教师" clearable filterable style="width: 180px">
            <el-option v-for="item in teacherOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="学期">
          <el-select v-model="timetableSemesterId" placeholder="全部学期" clearable style="width: 180px">
            <el-option v-for="item in semesterOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadTimetable">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table v-loading="timetableLoading" :data="timetableRows" border>
        <el-table-column prop="period" label="节次" width="80" align="center" />
        <el-table-column
          v-for="day in weekdays"
          :key="day.value"
          :label="day.label"
          min-width="120"
          align="center"
        >
          <template #default="{ row }">
            <div v-if="row.cells[day.value]" class="tt-cell">
              <div class="tt-course">{{ row.cells[day.value].course_name }}</div>
              <div class="tt-sub">
                {{ row.cells[day.value].teacher_name }}
                <span v-if="row.cells[day.value].room"> · {{ row.cells[day.value].room }}</span>
              </div>
            </div>
            <span v-else class="tt-empty">-</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 排课记录 -->
    <div class="sc-card">
      <el-form :inline="true" class="search-bar" @submit.prevent>
        <el-form-item label="班级">
          <el-select v-model="query.class_id" placeholder="全部班级" clearable filterable style="width: 160px">
            <el-option v-for="item in classOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程">
          <el-select v-model="query.course_id" placeholder="全部课程" clearable filterable style="width: 160px">
            <el-option v-for="item in courseOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="学期">
          <el-select v-model="query.semester_id" placeholder="全部学期" clearable style="width: 160px">
            <el-option v-for="item in semesterOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="星期">
          <el-select v-model="query.weekday" placeholder="全部" clearable style="width: 120px">
            <el-option v-for="day in weekdays" :key="day.value" :label="day.label" :value="day.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <div class="table-toolbar">
        <span class="title">排课记录列表</span>
        <el-button type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon> 新增排课
        </el-button>
      </div>

      <el-table v-loading="loading" :data="list" border stripe>
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column prop="semester_name" label="学期" min-width="130" />
        <el-table-column prop="class_name" label="班级" min-width="110" />
        <el-table-column prop="course_name" label="课程" min-width="110" />
        <el-table-column prop="teacher_name" label="教师" min-width="100">
          <template #default="{ row }">{{ row.teacher_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="星期" width="80" align="center">
          <template #default="{ row }">{{ weekdayText(row.weekday) }}</template>
        </el-table-column>
        <el-table-column label="节次" width="80" align="center">
          <template #default="{ row }">第 {{ row.period }} 节</template>
        </el-table-column>
        <el-table-column prop="room" label="教室" min-width="110">
          <template #default="{ row }">{{ row.room || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

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
        <el-form-item label="学期" prop="semester_id">
          <el-select v-model="form.semester_id" placeholder="请选择学期" style="width: 100%">
            <el-option v-for="item in semesterOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="班级" prop="class_id">
          <el-select v-model="form.class_id" placeholder="请选择班级" filterable style="width: 100%">
            <el-option v-for="item in classOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程" prop="course_id">
          <el-select v-model="form.course_id" placeholder="请选择课程" filterable style="width: 100%">
            <el-option v-for="item in courseOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="任课教师" prop="teacher_id">
          <el-select v-model="form.teacher_id" placeholder="可不选" clearable filterable style="width: 100%">
            <el-option v-for="item in teacherOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="星期" prop="weekday">
          <el-select v-model="form.weekday" placeholder="请选择星期" style="width: 100%">
            <el-option
              v-for="day in weekdays.filter((d) => d.value <= 5)"
              :key="day.value"
              :label="day.label"
              :value="day.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="节次" prop="period">
          <el-select v-model="form.period" placeholder="请选择节次" style="width: 100%">
            <el-option v-for="p in periodList" :key="p" :label="`第 ${p} 节`" :value="p" />
          </el-select>
        </el-form-item>
        <el-form-item label="上课教室" prop="room">
          <el-input v-model="form.room" placeholder="请输入上课教室" />
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
  createSchedule,
  deleteSchedule,
  getTimetable,
  listSchedules,
  updateSchedule,
  type ScheduleForm
} from '@/api/schedule'
import { listClassOptions } from '@/api/class'
import { listCourseOptions } from '@/api/course'
import { listSemesterOptions } from '@/api/semester'
import { listTeacherOptions } from '@/api/teacher'
import type { OptionItem, Schedule, TimetableCell } from '@/types/api'

/** 星期列表（周一到周日） */
const weekdays = [
  { label: '周一', value: 1 },
  { label: '周二', value: 2 },
  { label: '周三', value: 3 },
  { label: '周四', value: 4 },
  { label: '周五', value: 5 },
  { label: '周六', value: 6 },
  { label: '周日', value: 7 }
]
/** 节次列表 */
const periodList = [1, 2, 3, 4, 5, 6, 7, 8]

function weekdayText(weekday: number) {
  return weekdays.find((d) => d.value === weekday)?.label || `星期${weekday}`
}

/* ---------------- 周课表 ---------------- */
const timetableMode = ref<'class' | 'teacher'>('class')
const timetableClassId = ref<number | undefined>(undefined)
const timetableTeacherId = ref<number | undefined>(undefined)
const timetableSemesterId = ref<number | undefined>(undefined)
const timetableLoading = ref(false)
const timetableCells = ref<TimetableCell[]>([])

/** 把单元格数据整理成“行=节次、列=星期”的网格数据 */
const timetableRows = computed(() => {
  return periodList.map((period) => {
    const cells: Record<number, TimetableCell> = {}
    timetableCells.value
      .filter((c) => c.period === period)
      .forEach((c) => {
        cells[c.weekday] = c
      })
    return { period, cells }
  })
})

function handleTimetableModeChange() {
  timetableClassId.value = undefined
  timetableTeacherId.value = undefined
  timetableCells.value = []
}

async function loadTimetable() {
  if (timetableMode.value === 'class' && !timetableClassId.value) {
    ElMessage.warning('请先选择班级')
    return
  }
  if (timetableMode.value === 'teacher' && !timetableTeacherId.value) {
    ElMessage.warning('请先选择教师')
    return
  }
  timetableLoading.value = true
  try {
    timetableCells.value = await getTimetable({
      class_id: timetableMode.value === 'class' ? timetableClassId.value : undefined,
      teacher_id: timetableMode.value === 'teacher' ? timetableTeacherId.value : undefined,
      semester_id: timetableSemesterId.value
    })
  } finally {
    timetableLoading.value = false
  }
}

/* ---------------- 排课记录 ---------------- */
const loading = ref(false)
const list = ref<Schedule[]>([])
const total = ref(0)
const query = reactive<{
  page: number
  page_size: number
  class_id: number | undefined
  course_id: number | undefined
  semester_id: number | undefined
  weekday: number | undefined
}>({
  page: 1,
  page_size: 10,
  class_id: undefined,
  course_id: undefined,
  semester_id: undefined,
  weekday: undefined
})

const classOptions = ref<OptionItem[]>([])
const courseOptions = ref<OptionItem[]>([])
const semesterOptions = ref<OptionItem[]>([])
const teacherOptions = ref<OptionItem[]>([])

const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const editId = ref<number | null>(null)
const dialogTitle = computed(() => (editId.value ? '编辑排课' : '新增排课'))

const form = reactive<{
  semester_id: number | null
  class_id: number | null
  course_id: number | null
  teacher_id: number | null
  weekday: number | null
  period: number | null
  room: string
}>({
  semester_id: null,
  class_id: null,
  course_id: null,
  teacher_id: null,
  weekday: null,
  period: null,
  room: ''
})

const rules: FormRules = {
  semester_id: [{ required: true, message: '请选择学期', trigger: 'change' }],
  class_id: [{ required: true, message: '请选择班级', trigger: 'change' }],
  course_id: [{ required: true, message: '请选择课程', trigger: 'change' }],
  weekday: [{ required: true, message: '请选择星期', trigger: 'change' }],
  period: [{ required: true, message: '请选择节次', trigger: 'change' }]
}

/** 加载排课分页列表 */
async function loadList() {
  loading.value = true
  try {
    const res = await listSchedules({
      page: query.page,
      page_size: query.page_size,
      class_id: query.class_id,
      course_id: query.course_id,
      semester_id: query.semester_id,
      weekday: query.weekday
    })
    list.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

/** 加载下拉选项 */
async function loadOptions() {
  classOptions.value = await listClassOptions()
  courseOptions.value = await listCourseOptions()
  semesterOptions.value = await listSemesterOptions()
  teacherOptions.value = await listTeacherOptions()
}

function handleSearch() {
  query.page = 1
  loadList()
}

function handleReset() {
  query.class_id = undefined
  query.course_id = undefined
  query.semester_id = undefined
  query.weekday = undefined
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
  Object.assign(form, {
    semester_id: null,
    class_id: null,
    course_id: null,
    teacher_id: null,
    weekday: null,
    period: null,
    room: ''
  })
  formRef.value?.clearValidate()
}

function openCreate() {
  editId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: Schedule) {
  editId.value = row.id
  Object.assign(form, {
    semester_id: row.semester_id,
    class_id: row.class_id,
    course_id: row.course_id,
    teacher_id: row.teacher_id,
    weekday: row.weekday,
    period: row.period,
    room: row.room || ''
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const data = {
      semester_id: form.semester_id as number,
      class_id: form.class_id as number,
      course_id: form.course_id as number,
      teacher_id: form.teacher_id,
      weekday: form.weekday as number,
      period: form.period as number,
      room: form.room || null
    } as ScheduleForm
    if (editId.value) {
      await updateSchedule(editId.value, data)
      ElMessage.success('修改成功')
    } else {
      await createSchedule(data)
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

async function handleDelete(row: Schedule) {
  try {
    await ElMessageBox.confirm(
      `确定删除「${row.class_name}」${weekdayText(row.weekday)}第 ${row.period} 节的排课吗？`,
      '提示',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }

  try {
    await deleteSchedule(row.id)
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

<style scoped>
.tt-cell {
  line-height: 1.5;
}
.tt-course {
  font-weight: 600;
  color: #1f2a3c;
}
.tt-sub {
  font-size: 12px;
  color: #909399;
}
.tt-empty {
  color: #c0c4cc;
}
</style>
