<template>
  <div class="page-container">
    <div class="sc-card">
      <h3 class="page-title">资产统计</h3>
      <p class="page-desc">按资产分类与所属部门统计资产数量与金额分布。</p>

      <div class="chart-grid">
        <div class="chart-box">
          <div class="chart-title">分类资产金额占比</div>
          <div ref="amountPieRef" class="chart"></div>
        </div>
        <div class="chart-box">
          <div class="chart-title">分类资产数量</div>
          <div ref="categoryRef" class="chart"></div>
        </div>
        <div class="chart-box">
          <div class="chart-title">部门资产数量</div>
          <div ref="departmentRef" class="chart"></div>
        </div>
      </div>

      <div class="table-toolbar" style="margin-top: 16px">
        <span class="title">分类明细</span>
      </div>
      <el-table v-loading="loading" :data="detailRows" border stripe>
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column prop="category" label="资产分类" min-width="140" />
        <el-table-column prop="count" label="资产数量" min-width="120" align="center" />
        <el-table-column label="资产金额（元）" min-width="160" align="center">
          <template #default="{ row }">{{ formatAmount(row.amount) }}</template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import { getAssetStatistics } from '@/api/dashboard'
import type { AssetStatistics } from '@/types/api'

const loading = ref(false)
const statistics = ref<AssetStatistics | null>(null)

const amountPieRef = ref<HTMLDivElement>()
const categoryRef = ref<HTMLDivElement>()
const departmentRef = ref<HTMLDivElement>()
let amountPieChart: echarts.ECharts | null = null
let categoryChart: echarts.ECharts | null = null
let departmentChart: echarts.ECharts | null = null

const COLORS = ['#1a6fd4', '#4d9bf5', '#7fc0ff', '#0f9b8e', '#e8a33d', '#7b5cd6', '#d64545']

/** 金额千分位格式化 */
function formatAmount(value: number): string {
  return Number(value || 0).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

/** 分类明细：合并数量与金额 */
const detailRows = computed(() => {
  const data = statistics.value
  const amountMap = new Map((data?.amount_by_category ?? []).map((i) => [i.name, i.value]))
  return (data?.by_category ?? []).map((i) => ({
    category: i.name,
    count: i.value,
    amount: amountMap.get(i.name) ?? 0
  }))
})

function renderCharts() {
  const data = statistics.value

  const amountByCategory = data?.amount_by_category ?? []
  if (amountPieRef.value) {
    if (!amountPieChart) amountPieChart = echarts.init(amountPieRef.value)
    amountPieChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} 元 ({d}%)' },
      legend: { bottom: 0, type: 'scroll' },
      color: COLORS,
      series: [
        {
          type: 'pie',
          radius: ['40%', '68%'],
          center: ['50%', '45%'],
          label: { formatter: '{b}\n{d}%' },
          data: amountByCategory.map((i) => ({ name: i.name, value: Number(i.value.toFixed(2)) }))
        }
      ]
    })
  }

  const byCategory = data?.by_category ?? []
  if (categoryRef.value) {
    if (!categoryChart) categoryChart = echarts.init(categoryRef.value)
    categoryChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 50, right: 24, top: 30, bottom: 70 },
      xAxis: {
        type: 'category',
        data: byCategory.map((i) => i.name),
        axisLabel: { interval: 0, rotate: 30 }
      },
      yAxis: { type: 'value', name: '数量' },
      series: [
        {
          type: 'bar',
          barMaxWidth: 40,
          data: byCategory.map((i) => i.value),
          itemStyle: { color: '#1a6fd4', borderRadius: [4, 4, 0, 0] }
        }
      ]
    })
  }

  const byDepartment = data?.by_department ?? []
  if (departmentRef.value) {
    if (!departmentChart) departmentChart = echarts.init(departmentRef.value)
    departmentChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 50, right: 24, top: 30, bottom: 70 },
      xAxis: {
        type: 'category',
        data: byDepartment.map((i) => i.name),
        axisLabel: { interval: 0, rotate: 30 }
      },
      yAxis: { type: 'value', name: '数量' },
      series: [
        {
          type: 'bar',
          barMaxWidth: 40,
          data: byDepartment.map((i) => i.value),
          itemStyle: { color: '#0f9b8e', borderRadius: [4, 4, 0, 0] }
        }
      ]
    })
  }
}

function handleResize() {
  amountPieChart?.resize()
  categoryChart?.resize()
  departmentChart?.resize()
}

async function loadData() {
  loading.value = true
  try {
    statistics.value = await getAssetStatistics()
    renderCharts()
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadData()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  amountPieChart?.dispose()
  categoryChart?.dispose()
  departmentChart?.dispose()
})
</script>

<style scoped>
.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.chart-box {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: #1f2a3c;
  margin-bottom: 8px;
}

.chart {
  height: 320px;
}

@media (max-width: 1200px) {
  .chart-grid {
    grid-template-columns: 1fr;
  }
}
</style>
