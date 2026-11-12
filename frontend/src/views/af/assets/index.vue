<template>
  <div class="page-container">
    <div class="sc-card">
      <!-- 搜索栏 -->
      <el-form :inline="true" class="search-bar" @submit.prevent>
        <el-form-item label="关键字">
          <el-input
            v-model="query.keyword"
            placeholder="资产编号 / 名称 / 品牌 / 保管人"
            clearable
            style="width: 220px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="资产分类">
          <el-select v-model="query.category" placeholder="全部分类" clearable style="width: 150px">
            <el-option v-for="item in categoryOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="使用状态">
          <el-select v-model="query.status" placeholder="全部状态" clearable style="width: 140px">
            <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属部门">
          <el-select v-model="query.department_id" placeholder="全部部门" clearable filterable style="width: 180px">
            <el-option v-for="item in departmentOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 工具栏 -->
      <div class="table-toolbar">
        <span class="title">资产台账列表</span>
        <el-button type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon> 新增资产
        </el-button>
      </div>

      <!-- 表格 -->
      <el-table v-loading="loading" :data="list" border stripe>
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column prop="asset_no" label="资产编号" min-width="130" />
        <el-table-column prop="name" label="资产名称" min-width="140" />
        <el-table-column prop="category" label="分类" width="110" align="center" />
        <el-table-column prop="brand" label="品牌" min-width="100">
          <template #default="{ row }">{{ row.brand || '-' }}</template>
        </el-table-column>
        <el-table-column prop="model" label="规格型号" min-width="120">
          <template #default="{ row }">{{ row.model || '-' }}</template>
        </el-table-column>
        <el-table-column label="单价(元)" width="110" align="right">
          <template #default="{ row }">{{ row.price ?? '-' }}</template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="80" align="center" />
        <el-table-column prop="department_name" label="所属部门" min-width="130">
          <template #default="{ row }">{{ row.department_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="keeper" label="保管人" min-width="100">
          <template #default="{ row }">{{ row.keeper || '-' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="存放位置" min-width="120">
          <template #default="{ row }">{{ row.location || '-' }}</template>
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
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="640px" @closed="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="资产编号" prop="asset_no">
              <el-input v-model="form.asset_no" :disabled="!!editId" placeholder="请输入资产编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="资产名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入资产名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="资产分类" prop="category">
              <el-select v-model="form.category" placeholder="请选择分类" style="width: 100%">
                <el-option v-for="item in categoryOptions" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="使用状态" prop="status">
              <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
                <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="品牌" prop="brand">
              <el-input v-model="form.brand" placeholder="可选" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="规格型号" prop="model">
              <el-input v-model="form.model" placeholder="可选" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单价(元)" prop="price">
              <el-input-number v-model="form.price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="数量" prop="quantity">
              <el-input-number v-model="form.quantity" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="购置日期" prop="purchase_date">
              <el-date-picker
                v-model="form.purchase_date"
                type="date"
                placeholder="请选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属部门" prop="department_id">
              <el-select v-model="form.department_id" placeholder="可不选" clearable filterable style="width: 100%">
                <el-option v-for="item in departmentOptions" :key="item.id" :label="item.name" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="保管人" prop="keeper">
              <el-input v-model="form.keeper" placeholder="可选" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="存放位置" prop="location">
              <el-input v-model="form.location" placeholder="可选" />
            </el-form-item>
          </el-col>
        </el-row>
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
import { createAsset, deleteAsset, listAssets, updateAsset, type AssetForm } from '@/api/asset'
import { listDepartmentOptions } from '@/api/department'
import type { Asset, OptionItem } from '@/types/api'

/** 资产分类可选项 */
const categoryOptions = ['教学设备', '办公设备', '网络设备', '实验器材', '图书资料', '体育器材', '家具用具', '其他']
/** 资产状态可选项 */
const statusOptions = ['在用', '闲置', '维修', '报废']

function statusTagType(status: string) {
  if (status === '在用') return 'success'
  if (status === '维修') return 'warning'
  if (status === '报废') return 'danger'
  return 'info'
}

const loading = ref(false)
const list = ref<Asset[]>([])
const total = ref(0)
const query = reactive<{
  page: number
  page_size: number
  keyword: string
  category: string | undefined
  status: string | undefined
  department_id: number | undefined
}>({
  page: 1,
  page_size: 10,
  keyword: '',
  category: undefined,
  status: undefined,
  department_id: undefined
})

const departmentOptions = ref<OptionItem[]>([])

const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()
const editId = ref<number | null>(null)
const dialogTitle = computed(() => (editId.value ? '编辑资产' : '新增资产'))

const form = reactive<{
  asset_no: string
  name: string
  category: string
  status: string
  brand: string
  model: string
  price: number | null
  quantity: number
  purchase_date: string
  department_id: number | null
  keeper: string
  location: string
}>({
  asset_no: '',
  name: '',
  category: '教学设备',
  status: '在用',
  brand: '',
  model: '',
  price: null,
  quantity: 1,
  purchase_date: '',
  department_id: null,
  keeper: '',
  location: ''
})

const rules: FormRules = {
  asset_no: [{ required: true, message: '请输入资产编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入资产名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择资产分类', trigger: 'change' }],
  status: [{ required: true, message: '请选择使用状态', trigger: 'change' }]
}

/** 加载资产分页列表 */
async function loadList() {
  loading.value = true
  try {
    const res = await listAssets({
      page: query.page,
      page_size: query.page_size,
      keyword: query.keyword || undefined,
      category: query.category,
      status: query.status,
      department_id: query.department_id
    })
    list.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

/** 加载部门选项 */
async function loadOptions() {
  departmentOptions.value = await listDepartmentOptions()
}

function handleSearch() {
  query.page = 1
  loadList()
}

function handleReset() {
  query.keyword = ''
  query.category = undefined
  query.status = undefined
  query.department_id = undefined
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
    asset_no: '',
    name: '',
    category: '教学设备',
    status: '在用',
    brand: '',
    model: '',
    price: null,
    quantity: 1,
    purchase_date: '',
    department_id: null,
    keeper: '',
    location: ''
  })
  formRef.value?.clearValidate()
}

function openCreate() {
  editId.value = null
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: Asset) {
  editId.value = row.id
  Object.assign(form, {
    asset_no: row.asset_no,
    name: row.name,
    category: row.category,
    status: row.status,
    brand: row.brand || '',
    model: row.model || '',
    price: row.price,
    quantity: row.quantity,
    purchase_date: row.purchase_date || '',
    department_id: row.department_id,
    keeper: row.keeper || '',
    location: row.location || ''
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const data: AssetForm = {
      asset_no: form.asset_no,
      name: form.name,
      category: form.category,
      status: form.status,
      brand: form.brand || null,
      model: form.model || null,
      price: form.price,
      quantity: form.quantity,
      purchase_date: form.purchase_date || null,
      department_id: form.department_id,
      keeper: form.keeper || null,
      location: form.location || null
    }
    if (editId.value) {
      const { asset_no: _assetNo, ...rest } = data
      await updateAsset(editId.value, rest)
      ElMessage.success('修改成功')
    } else {
      await createAsset(data)
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

async function handleDelete(row: Asset) {
  try {
    await ElMessageBox.confirm(`确定删除资产「${row.name}」吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch {
    return
  }

  try {
    await deleteAsset(row.id)
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
