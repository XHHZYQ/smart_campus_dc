<template>
  <div class="page-container">
    <div class="sc-card">
      <!-- 搜索栏 -->
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
          <el-select v-model="query.semester_id" placeholder="全部学期" clearable style="width: 180px">
            <el-option v-for="item in semesterOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="考试类型">
          <el-select v-model="query.exam_type" placeholder="全部" clearable style="width: 130px">
            <el-option v-for="item in examTypeOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 工具栏 -->
      <div class="table-toolbar">
        <span class="title">成绩列表</span>
        <div>
          <el-button type="primary" @click="openSingle">
            <el-icon><Plus /></el-icon> 新增成绩
          </el-button>
          <el-button type="success" @click="openBatch">批量录入</el-button>
        </div>
      </div>

      <!-- 表格 -->
      <el-table v-loading="loading" :data="list" border stripe>
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column prop="student_no" label="学籍号" min-width="120" />
        <el-table-column prop="student_name" label="学生姓名" min-width="100" />
        <el-table-column prop="class_name" label="班级" min-width="110" />
        <el-table-column prop="course_name" label="课程" min-width="100" />
        <el-table-column prop="semester_name" label="学期" min-width="130" />
        <el-table-column prop="exam_type" label="考试类型" width="100" align="center" />
        <el-table-column label="分数" width="90" align="center">
          <template #default="{ row }">{{ row.score ?? '-' }}</template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="120">
          <template #default="{ row }">{{ row.remark || '-' }}</template>
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

    <!-- 单条录入弹窗 -->
    <el-dialog v-model="singleVisible" title="成绩录入" width="520px" @closed="resetSingleForm">
      <el-form ref="singleFormRef" :model="singleForm" :rules="singleRules" label-width="100px">
        <el-form-item label="学生" prop="student_id">
          <el-select
            v-model="singleForm.student_id"
            placeholder="请选择学生"
            filterable
            style="width: 100%"
          >
            <el-option v-for="item in studentOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程" prop="course_id">
          <el-select v-model="singleForm.course_id" placeholder="请选择课程" filterable style="width: 100%">
            <el-option v-for="item in courseOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="学期" prop="semester_id">
          <el-select v-model="singleForm.semester_id" placeholder="请选择学期" style="width: 100%">
            <el-option v-for="item in semesterOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="考试类型" prop="exam_type">
          <el-select v-model="singleForm.exam_type" placeholder="请选择考试类型" style="width: 100%">
            <el-option v-for="item in examTypeOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="分数" prop="score">
          <el-input-number v-model="singleForm.score" :min="0" :max="200" :precision="1" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="singleForm.remark" type="textarea" :rows="2" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="singleVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitSingle">确定</el-button>
      </template>
    </el-dialog>

    <!-- 批量录入弹窗 -->
    <el-dialog v-model="batchVisible" title="批量录入成绩" width="760px" @closed="resetBatchForm">
      <el-form :inline="true" class="search-bar">
        <el-form-item label="班级">
          <el-select
            v-model="batchForm.class_id"
            placeholder="请选择班级"
            filterable
            style="width: 160px"
            @change="loadBatchStudents"
          >
            <el-option v-for="item in classOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="课程">
          <el-select v-model="batchForm.course_id" placeholder="请选择课程" filterable style="width: 150px">
            <el-option v-for="item in courseOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="学期">
          <el-select v-model="batchForm.semester_id" placeholder="请选择学期" style="width: 170px">
            <el-option v-for="item in semesterOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="考试类型">
          <el-select v-model="batchForm.exam_type" placeholder="请选择" style="width: 130px">
            <el-option v-for="item in examTypeOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
      </el-form>

      <el-table v-loading="batchLoading" :data="batchRows" border height="320" style="margin-top: 12px">
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column prop="student_no" label="学籍号" min-width="130" />
        <el-table-column prop="name" label="学生姓名" min-width="110" />
        <el-table-column label="分数" min-width="160" align="center">
          <template #default="{ row }">
            <el-input-number v-model="row.score" :min="0" :max="200" :precision="1" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="180">
          <template #default="{ row }">
            <el-input v-model="row.remark" size="small" placeholder="可选" />
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="batchVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitBatch">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  batchCreateScores,
  createScore,
  deleteScore,
  listScores,
  updateScore,
  type ScoreForm
} from '@/api/score'
import { listClassOptions } from '@/api/class'
import { listCourseOptions } from '@/api/course'
import { listSemesterOptions } from '@/api/semester'
import { listStudentOptions } from '@/api/student'
import type { BatchScoreRequest, OptionItem, Score } from '@/types/api'

/** 考试类型可选项 */
const examTypeOptions = ['月考', '期中', '期末', '单元测试']

const loading = ref(false)
const list = ref<Score[]>([])
const total = ref(0)
const query = reactive<{
  page: number
  page_size: number
  class_id: number | undefined
  course_id: number | undefined
  semester_id: number | undefined
  exam_type: string | undefined
}>({
  page: 1,
  page_size: 10,
  class_id: undefined,
  course_id: undefined,
  semester_id: undefined,
  exam_type: undefined
})

const classOptions = ref<OptionItem[]>([])
const courseOptions = ref<OptionItem[]>([])
const semesterOptions = ref<OptionItem[]>([])
const studentOptions = ref<OptionItem[]>([])
const submitting = ref(false)

/* ---------------- 单条录入 ---------------- */
const singleVisible = ref(false)
const singleFormRef = ref<FormInstance>()
const editId = ref<number | null>(null)
const singleForm = reactive<{
  student_id: number | null
  course_id: number | null
  semester_id: number | null
  exam_type: string
  score: number | null
  remark: string
}>({
  student_id: null,
  course_id: null,
  semester_id: null,
  exam_type: '期末',
  score: null,
  remark: ''
})
const singleRules: FormRules = {
  student_id: [{ required: true, message: '请选择学生', trigger: 'change' }],
  course_id: [{ required: true, message: '请选择课程', trigger: 'change' }],
  semester_id: [{ required: true, message: '请选择学期', trigger: 'change' }],
  exam_type: [{ required: true, message: '请选择考试类型', trigger: 'change' }]
}

/* ---------------- 批量录入 ---------------- */
const batchVisible = ref(false)
const batchLoading = ref(false)
const batchForm = reactive<{
  class_id: number | null
  course_id: number | null
  semester_id: number | null
  exam_type: string
}>({
  class_id: null,
  course_id: null,
  semester_id: null,
  exam_type: '期末'
})
const batchRows = ref<
  { student_id: number; student_no: string; name: string; score: number | null; remark: string }[]
>([])

/** 加载成绩分页列表 */
async function loadList() {
  loading.value = true
  try {
    const res = await listScores({
      page: query.page,
      page_size: query.page_size,
      class_id: query.class_id,
      course_id: query.course_id,
      semester_id: query.semester_id,
      exam_type: query.exam_type
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
  studentOptions.value = await listStudentOptions()
}

function handleSearch() {
  query.page = 1
  loadList()
}

function handleReset() {
  query.class_id = undefined
  query.course_id = undefined
  query.semester_id = undefined
  query.exam_type = undefined
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

function resetSingleForm() {
  Object.assign(singleForm, {
    student_id: null,
    course_id: null,
    semester_id: null,
    exam_type: '期末',
    score: null,
    remark: ''
  })
  singleFormRef.value?.clearValidate()
}

function openSingle() {
  editId.value = null
  resetSingleForm()
  singleVisible.value = true
}

function openEdit(row: Score) {
  Object.assign(singleForm, {
    student_id: row.student_id,
    course_id: row.course_id,
    semester_id: row.semester_id,
    exam_type: row.exam_type,
    score: row.score,
    remark: row.remark || ''
  })
  editId.value = row.id
  singleVisible.value = true
}

async function submitSingle() {
  const valid = await singleFormRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (editId.value) {
      await updateScore(editId.value, {
        exam_type: singleForm.exam_type,
        score: singleForm.score,
        remark: singleForm.remark || null
      })
      ElMessage.success('修改成功')
    } else {
      const data: ScoreForm = {
        student_id: singleForm.student_id as number,
        course_id: singleForm.course_id as number,
        semester_id: singleForm.semester_id as number,
        exam_type: singleForm.exam_type,
        score: singleForm.score,
        remark: singleForm.remark || null
      }
      await createScore(data)
      ElMessage.success('录入成功')
    }
    singleVisible.value = false
    loadList()
  } catch {
    // 错误提示由请求拦截器统一处理
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row: Score) {
  try {
    await ElMessageBox.confirm(
      `确定删除「${row.student_name}」的 ${row.course_name} 成绩吗？`,
      '提示',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }

  try {
    await deleteScore(row.id)
    ElMessage.success('删除成功')
    loadList()
  } catch {
    // 错误提示由请求拦截器统一处理
  }
}

function resetBatchForm() {
  Object.assign(batchForm, { class_id: null, course_id: null, semester_id: null, exam_type: '期末' })
  batchRows.value = []
}

function openBatch() {
  resetBatchForm()
  batchVisible.value = true
}

/** 根据所选班级加载学生名单，生成待录入表格 */
async function loadBatchStudents() {
  batchRows.value = []
  if (!batchForm.class_id) return
  batchLoading.value = true
  try {
    const students = await listStudentOptions(batchForm.class_id)
    batchRows.value = students.map((s) => ({
      student_id: s.id,
      student_no: s.name.includes(' ') ? s.name.split(' ')[0] : String(s.id),
      name: s.name.includes(' ') ? s.name.split(' ').slice(1).join(' ') : s.name,
      score: null,
      remark: ''
    }))
  } finally {
    batchLoading.value = false
  }
}

async function submitBatch() {
  if (!batchForm.class_id || !batchForm.course_id || !batchForm.semester_id) {
    ElMessage.warning('请先选择班级、课程与学期')
    return
  }
  if (batchRows.value.length === 0) {
    ElMessage.warning('当前班级没有可录入的学生')
    return
  }

  const payload: BatchScoreRequest = {
    class_id: batchForm.class_id,
    course_id: batchForm.course_id,
    semester_id: batchForm.semester_id,
    exam_type: batchForm.exam_type,
    items: batchRows.value.map((r) => ({
      student_id: r.student_id,
      score: r.score,
      remark: r.remark || null
    }))
  }

  submitting.value = true
  try {
    await batchCreateScores(payload)
    ElMessage.success('批量录入成功')
    batchVisible.value = false
    loadList()
  } catch {
    // 错误提示由请求拦截器统一处理
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadList()
  loadOptions()
})
</script>
