<template>
  <div class="page-container">
    <!-- 欢迎栏 -->
    <div class="welcome sc-card">
      <div class="welcome-left">
        <el-avatar :size="56" class="avatar">
          {{ (userStore.userInfo?.real_name || 'U').charAt(0) }}
        </el-avatar>
        <div>
          <div class="hello">
            {{ greeting }}，{{ userStore.userInfo?.real_name || '用户' }}
          </div>
          <div class="role">
            当前角色：{{ userStore.userInfo?.role_name || '-' }}
            <span class="divider">|</span>
            当前学期：{{ overview?.current_semester || '未设置' }}
          </div>
        </div>
      </div>
      <el-tag type="primary" effect="dark" size="large">智慧校园数据中心管理软件 V1.0.0</el-tag>
    </div>

    <!-- 指标卡片 -->
    <div class="metric-grid">
      <div v-for="item in metrics" :key="item.label" class="sc-card metric-card">
        <div class="metric-icon" :style="{ background: item.color }">
          <el-icon><component :is="item.icon" /></el-icon>
        </div>
        <div class="metric-body">
          <div class="metric-value">
            {{ item.value }}<span class="metric-unit">{{ item.unit }}</span>
          </div>
          <div class="metric-label">{{ item.label }}</div>
        </div>
      </div>
    </div>

    <!-- 图表 -->
    <div class="chart-grid">
      <div class="sc-card">
        <h3 class="page-title">近 6 学期平均分趋势</h3>
        <div ref="trendRef" class="chart"></div>
      </div>
      <div class="sc-card">
        <h3 class="page-title">各年级学生数</h3>
        <div ref="gradeRef" class="chart"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import { useUserStore } from '@/stores/user'
import { getOverview, getScoreAnalysis, getStudentComposition } from '@/api/dashboard'
import type { Overview, ScoreAnalysis, StudentComposition } from '@/types/api'

const userStore = useUserStore()

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '凌晨好'
  if (hour < 12) return '早上好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

const overview = ref<Overview | null>(null)
const composition = ref<StudentComposition | null>(null)
const scoreAnalysis = ref<ScoreAnalysis | null>(null)

/** 金额千分位格式化 */
function formatAmount(value: number): string {
  return Number(value || 0).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

/** 顶部指标卡片 */
const metrics = computed(() => {
  const o = overview.value
  return [
    { label: '在校学生数', value: o?.student_total ?? 0, unit: '人', icon: 'UserFilled', color: '#1a6fd4' },
    { label: '教职工数', value: o?.teacher_total ?? 0, unit: '人', icon: 'Suitcase', color: '#2f9e44' },
    { label: '班级数', value: o?.class_total ?? 0, unit: '个', icon: 'School', color: '#e8a33d' },
    { label: '年级数', value: o?.grade_total ?? 0, unit: '个', icon: 'Grid', color: '#7b5cd6' },
    { label: '资产总值', value: formatAmount(o?.asset_amount ?? 0), unit: '元', icon: 'Money', color: '#d64545' },
    { label: '宿舍床位', value: `${o?.dorm_occupied ?? 0}/${o?.dorm_bed_total ?? 0}`, unit: '已住/总', icon: 'House', color: '#0f9b8e' }
  ]
})

const trendRef = ref<HTMLDivElement>()
const gradeRef = ref<HTMLDivElement>()
let trendChart: echarts.ECharts | null = null
let gradeChart: echarts.ECharts | null = null

/** 渲染两张图表 */
function renderCharts() {
  const trend = scoreAnalysis.value?.semester_trend.slice(-6) ?? []
  if (trendRef.value) {
    trendChart = echarts.init(trendRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 50, right: 24, top: 30, bottom: 60 },
      xAxis: {
        type: 'category',
        data: trend.map((i) => i.name),
        axisLabel: { interval: 0, rotate: 25 }
      },
      yAxis: { type: 'value', name: '平均分', min: 0, max: 100 },
      series: [
        {
          type: 'line',
          smooth: true,
          symbolSize: 8,
          data: trend.map((i) => Number(i.value.toFixed(2))),
          itemStyle: { color: '#1a6fd4' },
          lineStyle: { width: 3 },
          areaStyle: { color: 'rgba(26, 111, 212, 0.15)' }
        }
      ]
    })
  }

  const grades = composition.value?.by_grade ?? []
  if (gradeRef.value) {
    gradeChart = echarts.init(gradeRef.value)
    gradeChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 50, right: 24, top: 30, bottom: 60 },
      xAxis: {
        type: 'category',
        data: grades.map((i) => i.name),
        axisLabel: { interval: 0, rotate: 30 }
      },
      yAxis: { type: 'value', name: '人数' },
      series: [
        {
          type: 'bar',
          barMaxWidth: 36,
          data: grades.map((i) => i.value),
          itemStyle: { color: '#1a6fd4', borderRadius: [4, 4, 0, 0] }
        }
      ]
    })
  }
}

function handleResize() {
  trendChart?.resize()
  gradeChart?.resize()
}

async function loadData() {
  const [overviewData, compositionData, scoreData] = await Promise.all([
    getOverview(),
    getStudentComposition(),
    getScoreAnalysis()
  ])
  overview.value = overviewData
  composition.value = compositionData
  scoreAnalysis.value = scoreData
}

onMounted(async () => {
  await loadData()
  renderCharts()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  gradeChart?.dispose()
})
</script>

<style scoped>
.welcome {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.welcome-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar {
  background: var(--sc-primary);
  color: #fff;
  font-size: 22px;
}

.hello {
  font-size: 18px;
  font-weight: 600;
  color: #1f2a3c;
  margin-bottom: 4px;
}

.role {
  font-size: 13px;
  color: #909399;
}

.divider {
  margin: 0 8px;
  color: #dcdfe6;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 14px;
}

.metric-icon {
  width: 52px;
  height: 52px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 26px;
  flex-shrink: 0;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2a3c;
  line-height: 1.2;
}

.metric-unit {
  font-size: 12px;
  font-weight: 400;
  color: #909399;
  margin-left: 4px;
}

.metric-label {
  margin-top: 4px;
  font-size: 13px;
  color: #909399;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.chart {
  height: 320px;
}

@media (max-width: 1200px) {
  .metric-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .chart-grid {
    grid-template-columns: 1fr;
  }
}
</style>
