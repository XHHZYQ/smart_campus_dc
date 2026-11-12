<template>
  <div class="page-container">
    <div class="sc-card">
      <!-- 搜索栏 -->
      <el-form :inline="true" class="search-bar" @submit.prevent>
        <el-form-item label="关键字">
          <el-input
            v-model="query.keyword"
            placeholder="登录账号 / IP"
            clearable
            style="width: 220px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="登录时间">
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
        <span class="title">登录日志</span>
      </div>

      <!-- 数据表格（只读） -->
      <el-table v-loading="loading" :data="list" border stripe>
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column prop="username" label="登录账号" min-width="140" />
        <el-table-column prop="ip" label="客户端IP" min-width="140" />
        <el-table-column label="结果" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.success ? 'success' : 'danger'">{{ row.success ? '成功' : '失败' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="提示信息" min-width="160" />
        <el-table-column prop="user_agent" label="浏览器标识" min-width="240" show-overflow-tooltip />
        <el-table-column prop="created_at" label="登录时间" min-width="170" />
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
import { listLoginLogs } from '@/api/log'
import type { LoginLog } from '@/types/api'

const loading = ref(false)
const list = ref<LoginLog[]>([])
const total = ref(0)
const query = reactive({ page: 1, page_size: 10, keyword: '' })
const dateRange = ref<[string, string] | null>(null)

/** 加载登录日志分页列表 */
async function loadList() {
  loading.value = true
  try {
    const res = await listLoginLogs({
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
