<template>
  <div class="screen">
    <!-- 顶部标题栏 -->
    <div class="screen-header">
      <div class="title-wrap">
        <span class="screen-title">智慧校园数据中心 · 数据大屏</span>
      </div>
      <el-button class="back-btn" @click="goBack">
        <el-icon><Back /></el-icon> 返回
      </el-button>
    </div>

    <!-- 数字指标 -->
    <div class="metric-row">
      <div v-for="item in metrics" :key="item.label" class="metric-item">
        <div class="metric-value">{{ item.value }}</div>
        <div class="metric-label">{{ item.label }}</div>
      </div>
    </div>

    <!-- 图表网格 -->
    <div class="chart-grid">
      <div class="panel">
        <div class="panel-title">各学段人数分布</div>
        <div ref="stageRef" class="chart"></div>
      </div>
      <div class="panel">
        <div class="panel-title">各年级人数</div>
        <div ref="gradeRef" class="chart"></div>
      </div>
      <div class="panel">
        <div class="panel-title">性别分布</div>
        <div ref="genderRef" class="chart"></div>
      </div>
      <div class="panel">
        <div class="panel-title">资产分类金额 TOP</div>
        <div ref="assetRef" class="chart"></div>
      </div>
      <div class="panel">
        <div class="panel-title">各学科平均分</div>
        <div ref="scoreRef" class="chart"></div>
      </div>
      <div class="panel">
        <div class="panel-title">考勤状态分布</div>
        <div ref="attendanceRef" class="chart"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { getScreenData } from '@/api/dashboard'
import type { NameValue, ScreenData } from '@/types/api'

const router = useRouter()
const screenData = ref<ScreenData | null>(null)

// 深色主题下的通用文字颜色
const AXIS_COLOR = '#9fb3c8'
const SPLIT_COLOR = 'rgba(159, 179, 200, 0.18)'
const COLORS = ['#1a6fd4', '#4d9bf5', '#7fc0ff', '#0f9b8e', '#e8a33d', '#7b5cd6', '#d64545']

const stageRef = ref<HTMLDivElement>()
const gradeRef = ref<HTMLDivElement>()
const genderRef = ref<HTMLDivElement>()
const assetRef = ref<HTMLDivElement>()
const scoreRef = ref<HTMLDivElement>()
const attendanceRef = ref<HTMLDivElement>()
let stageChart: echarts.ECharts | null = null
let gradeChart: echarts.ECharts | null = null
let genderChart: echarts.ECharts | null = null
let assetChart: echarts.ECharts | null = null
let scoreChart: echarts.ECharts | null = null
let attendanceChart: echarts.ECharts | null = null

/** 顶部数字指标 */
const metrics = computed(() => {
  const d = screenData.value
  return [
    { label: '学生总数', value: d?.student_total ?? 0 },
    { label: '教职工数', value: d?.teacher_total ?? 0 },
    { label: '班级数', value: d?.class_total ?? 0 },
    {
      label: '资产总值（元）',
      value: Number(d?.asset_amount ?? 0).toLocaleString('zh-CN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })
    }
  ]
})

/** 深色主题饼图 */
function pieOption(data: NameValue[]) {
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, textStyle: { color: AXIS_COLOR }, type: 'scroll' },
    color: COLORS,
    series: [
      {
        type: 'pie',
        radius: ['38%', '66%'],
        center: ['50%', '44%'],
        label: { color: AXIS_COLOR, formatter: '{b}\n{d}%' },
        data: data.map((i) => ({ name: i.name, value: i.value }))
      }
    ]
  }
}

/** 深色主题柱状图（纵向） */
function barOption(data: NameValue[], unit: string) {
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 46, right: 20, top: 24, bottom: 56 },
    xAxis: {
      type: 'category',
      data: data.map((i) => i.name),
      axisLabel: { color: AXIS_COLOR, interval: 0, rotate: 30 },
      axisLine: { lineStyle: { color: SPLIT_COLOR } }
    },
    yAxis: {
      type: 'value',
      name: unit,
      nameTextStyle: { color: AXIS_COLOR },
      axisLabel: { color: AXIS_COLOR },
      splitLine: { lineStyle: { color: SPLIT_COLOR } }
    },
    series: [
      {
        type: 'bar',
        barMaxWidth: 34,
        data: data.map((i) => i.value),
        itemStyle: { color: '#1a6fd4', borderRadius: [4, 4, 0, 0] }
      }
    ]
  }
}

/** 深色主题横向柱状图 */
function hBarOption(data: NameValue[]) {
  const sorted = [...data].sort((a, b) => a.value - b.value)
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 90, right: 30, top: 20, bottom: 24 },
    xAxis: {
      type: 'value',
      axisLabel: { color: AXIS_COLOR },
      splitLine: { lineStyle: { color: SPLIT_COLOR } }
    },
    yAxis: {
      type: 'category',
      data: sorted.map((i) => i.name),
      axisLabel: { color: AXIS_COLOR },
      axisLine: { lineStyle: { color: SPLIT_COLOR } }
    },
    series: [
      {
        type: 'bar',
        barMaxWidth: 20,
        data: sorted.map((i) => Number(i.value.toFixed(2))),
        itemStyle: { color: '#4d9bf5', borderRadius: [0, 4, 4, 0] }
      }
    ]
  }
}

function renderCharts() {
  const d = screenData.value

  if (stageRef.value) {
    stageChart = echarts.init(stageRef.value)
    stageChart.setOption(pieOption(d?.by_stage ?? []))
  }
  if (gradeRef.value) {
    gradeChart = echarts.init(gradeRef.value)
    gradeChart.setOption(barOption(d?.by_grade ?? [], '人数'))
  }
  if (genderRef.value) {
    genderChart = echarts.init(genderRef.value)
    genderChart.setOption(pieOption(d?.by_gender ?? []))
  }
  if (assetRef.value) {
    assetChart = echarts.init(assetRef.value)
    assetChart.setOption(hBarOption(d?.asset_by_category ?? []))
  }
  if (scoreRef.value) {
    scoreChart = echarts.init(scoreRef.value)
    scoreChart.setOption(barOption(d?.avg_score_by_course ?? [], '平均分'))
  }
  if (attendanceRef.value) {
    attendanceChart = echarts.init(attendanceRef.value)
    attendanceChart.setOption(pieOption(d?.attendance_by_status ?? []))
  }
}

function handleResize() {
  stageChart?.resize()
  gradeChart?.resize()
  genderChart?.resize()
  assetChart?.resize()
  scoreChart?.resize()
  attendanceChart?.resize()
}

function goBack() {
  router.push('/dashboard')
}

onMounted(async () => {
  screenData.value = await getScreenData()
  renderCharts()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  stageChart?.dispose()
  gradeChart?.dispose()
  genderChart?.dispose()
  assetChart?.dispose()
  scoreChart?.dispose()
  attendanceChart?.dispose()
})
</script>

<style scoped>
.screen {
  min-height: 100vh;
  background: #0b1a2b;
  padding: 16px 20px 24px;
  box-sizing: border-box;
}

.screen-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(127, 192, 255, 0.25);
  margin-bottom: 16px;
}

.screen-title {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 2px;
  color: #7fc0ff;
}

.back-btn {
  background: transparent;
  border-color: rgba(127, 192, 255, 0.5);
  color: #cfe0f5;
}

.metric-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.metric-item {
  background: rgba(26, 111, 212, 0.12);
  border: 1px solid rgba(127, 192, 255, 0.28);
  border-radius: 8px;
  padding: 18px 20px;
  text-align: center;
}

.metric-value {
  font-size: 30px;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.2;
}

.metric-label {
  margin-top: 6px;
  font-size: 14px;
  color: #9fb3c8;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.panel {
  background: rgba(15, 40, 66, 0.6);
  border: 1px solid rgba(127, 192, 255, 0.2);
  border-radius: 8px;
  padding: 12px;
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
  color: #cfe0f5;
  margin-bottom: 8px;
  padding-left: 8px;
  border-left: 3px solid #1a6fd4;
}

.chart {
  height: 260px;
}

@media (max-width: 1400px) {
  .chart-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 900px) {
  .metric-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .chart-grid {
    grid-template-columns: 1fr;
  }
}
</style>
