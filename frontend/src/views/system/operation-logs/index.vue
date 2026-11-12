<template>
  <div class="page-container">
    <div class="sc-card">
      <!-- 搜索栏 -->
      <el-form :inline="true" class="search-bar" @submit.prevent>
        <el-form-item label="关键字">
          <el-input
            v-model="query.keyword"
            placeholder="操作人 / 模块 / 操作类型"
            clearable
            style="width: 220px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="操作时间">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            value-format="YYYY-MM-DD"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 260px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格工具栏 -->
      <div class="table-toolbar">
        <span class="title">操作日志</span>
      </div>

      <!-- 数据表格（只读） -->
      <el-table v-loading="loading" :data="list" border stripe>
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column prop="real_name" label="操作人" min-width="110">
          <template #default="{ row }">{{ row.real_name || row.username || '-' }}</template>
        </el-table-column>
        <el-table-column prop="module" label="功能模块" min-width="120" />
        <el-table-column prop="action" label="操作类型" width="100" align="center" />
        <el-table-column prop="method" label="请求方法" width="100" align="center" />
        <el-table-column prop="path" label="请求路径" min-width="220" show-overflow-tooltip />
        <el-table-column prop="ip" label="客户端IP" min-width="140" />
        <el-table-column label="结果" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.success ? 'success' : 'danger'">{{ row.success ? '成功' : '失败' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="操作时间" min-width="170" />
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
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { listOperationLogs } from '@/api/log'
import type { OperationLog } from '@/types/api'

const loading = ref(false)
const list = ref<OperationLog[]>([])
const total = ref(0)
const query = reactive({ page: 1, page_size: 10, keyword: '' })
const dateRange = ref<[string, string] | null>(null)

/** 加载操作日志分页列表 */
async function loadList() {
  loading.value = true
  try {
    const res = await listOperationLogs({
      ...query,
      start_date: dateRange.value?.[0],
      end_date: dateRange.value?.[1]
    })
    list.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  query.page = 1
  loadList()
}

function handleReset() {
  query.keyword = ''
  dateRange.value = null
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

onMounted(loadList)
</script>
