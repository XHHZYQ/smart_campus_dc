<template>
  <div class="page-container">
    <div class="sc-card">
      <!-- 搜索栏 -->
      <el-form :inline="true" class="search-bar" @submit.prevent>
        <el-form-item label="关键字">
          <el-input
            v-model="query.keyword"
            placeholder="学籍号 / 姓名 / 电话"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="班级">
          <el-select v-model="query.class_id" placeholder="全部班级" clearable style="width: 170px">
            <el-option v-for="item in classOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="学籍状态">
          <el-select v-model="query.status" placeholder="全部状态" clearable style="width: 130px">
            <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格工具栏 -->
      <div class="table-toolbar">
        <span class="title">学生学籍列表</span>
        <el-button type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon> 新增学生
        </el-button>
      </div>

      <!-- 数据表格 -->
      <el-table v-loading="loading" :data="list" border stripe>
        <el-table-column prop="student_no" label="学籍号" min-width="130" />
        <el-table-column prop="name" label="姓名" min-width="90" />
        <el-table-column label="性别" width="70" align="center">
          <template #default="{ row }">{{ row.gender }}</template>
        </el-table-column>
        <el-table-column prop="class_name" label="班级" min-width="120">
          <template #default="{ row }">{{ row.class_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="enroll_year" label="入学年份" width="100" align="center" />
        <el-table-column prop="study_mode" label="就读方式" width="100" align="center" />
        <el-table-column label="学籍状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="联系电话" min-width="130" />
        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row)">详情</el-button>
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="820px" top="6vh" @closed="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-divider content-position="left">基本信息</el-divider>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="学籍号" prop="student_no">
              <el-input v-model="form.student_no" :disabled="!!editId" placeholder="请输入学籍号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="form.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="曾用名" prop="used_name">
              <el-input v-model="form.used_name" placeholder="请输入曾用名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="form.gender">
                <el-radio label="男">男</el-radio>
                <el-radio label="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="民族" prop="nation">
              <el-input v-model="form.nation" placeholder="如 汉族" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出生日期" prop="birth_date">
              <el-date-picker
                v-model="form.birth_date"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="请选择出生日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="身份证号" prop="id_card">
              <el-input v-model="form.id_card" placeholder="请输入身份证号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="政治面貌" prop="political_status">
              <el-input v-model="form.political_status" placeholder="如 群众" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="form.phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="家庭住址" prop="address">
              <el-input v-model="form.address" placeholder="请输入家庭住址" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">学籍信息</el-divider>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="所在班级" prop="class_id">
              <el-select v-model="form.class_id" placeholder="请选择班级" clearable style="width: 100%">
                <el-option v-for="item in classOptions" :key="item.id" :label="item.name" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="入学年份" prop="enroll_year">
              <el-input-number v-model="form.enroll_year" :min="2000" :max="2100" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="就读方式" prop="study_mode">
              <el-select v-model="form.study_mode" placeholder="请选择就读方式" style="width: 100%">
                <el-option label="走读" value="走读" />
                <el-option label="住校" value="住校" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学籍状态" prop="status">
              <el-select v-model="form.status" placeholder="请选择学籍状态" style="width: 100%">
                <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">家庭信息</el-divider>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="父亲姓名" prop="father_name">
              <el-input v-model="form.father_name" placeholder="请输入父亲姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="父亲电话" prop="father_phone">
              <el-input v-model="form.father_phone" placeholder="请输入父亲电话" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="父亲身份证" prop="father_id_card">
              <el-input v-model="form.father_id_card" placeholder="请输入父亲身份证号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="父亲单位" prop="father_work_unit">
              <el-input v-model="form.father_work_unit" placeholder="请输入父亲工作单位" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="父亲职务" prop="father_position">
              <el-input v-model="form.father_position" placeholder="请输入父亲职务" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="母亲姓名" prop="mother_name">
              <el-input v-model="form.mother_name" placeholder="请输入母亲姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="母亲电话" prop="mother_phone">
              <el-input v-model="form.mother_phone" placeholder="请输入母亲电话" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="母亲身份证" prop="mother_id_card">
              <el-input v-model="form.mother_id_card" placeholder="请输入母亲身份证号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="母亲单位" prop="mother_work_unit">
              <el-input v-model="form.mother_work_unit" placeholder="请输入母亲工作单位" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="母亲职务" prop="mother_position">
              <el-input v-model="form.mother_position" placeholder="请输入母亲职务" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="备注" prop="remark">
              <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 详情抽屉 -->
    <el-drawer v-model="detailVisible" title="学生学籍详情" size="620px">
      <div class="detail-grid">
        <div v-for="item in detailItems" :key="item.label" class="detail-item">
          <span class="label">{{ item.label }}</span>
          <span class="value">{{ item.value || '-' }}</span>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  createStudent,
  deleteStudent,
  getStudent,
  listStudents,
  updateStudent
} from '@/api/student'
import { listClassOptions } from '@/api/class'
import type { OptionItem, Student } from '@/types/api'

/** 学籍状态可选项 */
const statusOptions = ['正常', '休学', '转学', '退学', '毕业']

const loading = ref(false)
const list = ref<Student[]>([])
const total = ref(0)
const query = reactive<{
  page: number
  page_size: number
  keyword: string
  class_id: number | undefined
  status: string
}>({
  page: 1,
  page_size: 10,
  keyword: '',
  class_id: undefined,
  status: ''
})
const classOptions = ref<OptionItem[]>([])

const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const editId = ref<number | null>(null)
const dialogTitle = computed(() => (editId.value ? '编辑学生' : '新增学生'))

const detailVisible = ref(false)
const detail = ref<Student | null>(null)

const form = reactive<{
  student_no: string
  name: string
  used_name: string
  gender: string
  nation: string
  birth_date: string | null
  id_card: string
  political_status: string
  phone: string
  address: string
  class_id: number | null
  enroll_year: number | null
  study_mode: string
  status: string
  father_name: string
  father_id_card: string
  father_work_unit: string
  father_position: string
  father_phone: string
  mother_name: string
  mother_id_card: string
  mother_work_unit: string
  mother_position: string
  mother_phone: string
  remark: string
}>({
  student_no: '',
  name: '',
  used_name: '',
  gender: '男',
  nation: '汉族',
  birth_date: null,
  id_card: '',
  political_status: '群众',
  phone: '',
  address: '',
  class_id: null,
  enroll_year: null,
  study_mode: '走读',
  status: '正常',
  father_name: '',
  father_id_card: '',
  father_work_unit: '',
  father_position: '',
  father_phone: '',
  mother_name: '',
  mother_id_card: '',
  mother_work_unit: '',
  mother_position: '',
  mother_phone: '',
  remark: ''
})

const rules: FormRules = {
  student_no: [{ required: true, message: '请输入学籍号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  status: [{ required: true, message: '请选择学籍状态', trigger: 'change' }]
}

/** 学籍状态标签颜色 */
function statusTagType(status: string) {
  if (status === '正常') return 'success'
  if (status === '休学') return 'warning'
  if (status === '毕业') return 'info'
  return 'danger'
}

/** 详情展示项（覆盖全部学籍字段） */
const detailItems = computed(() => {
  const d = detail.value
  if (!d) return []
  return [
    { label: '学籍号', value: d.student_no },
    { label: '姓名', value: d.name },
    { label: '曾用名', value: d.used_name },
    { label: '性别', value: d.gender },
    { label: '民族', value: d.nation },
    { label: '出生日期', value: d.birth_date },
    { label: '身份证号', value: d.id_card },
    { label: '政治面貌', value: d.political_status },
    { label: '联系电话', value: d.phone },
    { label: '家庭住址', value: d.address },
    { label: '所在班级', value: d.class_name },
    { label: '所属年级', value: d.grade_name },
    { label: '入学年份', value: d.enroll_year },
    { label: '就读方式', value: d.study_mode },
    { label: '学籍状态', value: d.status },
    { label: '父亲姓名', value: d.father_name },
    { label: '父亲身份证号', value: d.father_id_card },
    { label: '父亲工作单位', value: d.father_work_unit },
    { label: '父亲职务', value: d.father_position },
    { label: '父亲电话', value: d.father_phone },
    { label: '母亲姓名', value: d.mother_name },
    { label: '母亲身份证号', value: d.mother_id_card },
    { label: '母亲工作单位', value: d.mother_work_unit },
    { label: '母亲职务', value: d.mother_position },
    { label: '母亲电话', value: d.mother_phone },
    { label: '备注', value: d.remark }
  ]
})

/** 加载学生分页列表 */
async function loadList() {
  loading.value = true
  try {
    const res = await listStudents({
      page: query.page,
      page_size: query.page_size,
      keyword: query.keyword || undefined,
      class_id: query.class_id,
      status: query.status || undefined
    })
    list.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

/** 加载班级下拉选项 */
async function loadOptions() {
  classOptions.value = await listClassOptions()
}

function handleSearch() {
  query.page = 1
  loadList()
}

function handleReset() {
  query.keyword = ''
  query.class_id = undefined
  query.status = ''
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

/** 重置表单为默认值 */
function resetForm() {
  Object.assign(form, {
    student_no: '',
    name: '',
    used_name: '',
    gender: '男',
    nation: '汉族',
    birth_date: null,
    id_card: '',
    political_status: '群众',
    phone: '',
    address: '',
    class_id: null,
    enroll_year: null,
    study_mode: '走读',
    status: '正常',
    father_name: '',
    father_id_card: '',
    father_work_unit: '',
    father_position: '',
    father_phone: '',
    mother_name: '',
    mother_id_card: '',
    mother_work_unit: '',
    mother_position: '',
    mother_phone: '',
    remark: ''
  })
  formRef.value?.clearValidate()
}

function openCreate() {
  editId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: Student) {
  editId.value = row.id
  Object.assign(form, {
    student_no: row.student_no,
    name: row.name,
    used_name: row.used_name || '',
    gender: row.gender,
    nation: row.nation || '',
    birth_date: row.birth_date,
    id_card: row.id_card || '',
    political_status: row.political_status || '',
    phone: row.phone || '',
    address: row.address || '',
    class_id: row.class_id,
    enroll_year: row.enroll_year,
    study_mode: row.study_mode,
    status: row.status,
    father_name: row.father_name || '',
    father_id_card: row.father_id_card || '',
    father_work_unit: row.father_work_unit || '',
    father_position: row.father_position || '',
    father_phone: row.father_phone || '',
    mother_name: row.mother_name || '',
    mother_id_card: row.mother_id_card || '',
    mother_work_unit: row.mother_work_unit || '',
    mother_position: row.mother_position || '',
    mother_phone: row.mother_phone || '',
    remark: row.remark || ''
  })
  dialogVisible.value = true
}

/** 打开详情抽屉，按 ID 拉取完整信息 */
async function openDetail(row: Student) {
  detail.value = row
  detailVisible.value = true
  try {
    detail.value = await getStudent(row.id)
  } catch {
    // 错误提示由请求拦截器统一处理
  }
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (editId.value) {
      await updateStudent(editId.value, { ...form })
      ElMessage.success('修改成功')
    } else {
      await createStudent({ ...form })
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

async function handleDelete(row: Student) {
  try {
    await ElMessageBox.confirm(`确定删除学生「${row.name}」的学籍吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch {
    return
  }

  try {
    await deleteStudent(row.id)
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
