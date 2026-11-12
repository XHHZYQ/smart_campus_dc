<template>
  <div class="page-container">
    <div class="sc-card">
      <h3 class="page-title">学生构成分析</h3>
      <p class="page-desc">按学段、年级与性别多维度查看在校学生分布情况。</p>

      <div class="chart-grid">
        <div class="chart-box">
          <div class="chart-title">按学段占比</div>
          <div ref="stageRef" class="chart"></div>
        </div>
        <div class="chart-box">
          <div class="chart-title">按年级人数</div>
          <div ref="gradeRef" class="chart"></div>
        </div>
        <div class="chart-box">
          <div class="chart-title">按性别占比</div>
          <div ref="genderRef" class="chart"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import { getStudentComposition } from '@/api/dashboard'
import type { NameValue } from '@/types/api'

const stageRef = ref<HTMLDivElement>()
const gradeRef = ref<HTMLDivElement>()
const genderRef = ref<HTMLDivElement>()
let stageChart: echarts.ECharts | null = null
let gradeChart: echarts.ECharts | null = null
let genderChart: echarts.ECharts | null = null

const COLORS = ['#1a6fd4', '#4d9bf5', '#7fc0ff', '#0f9b8e', '#e8a33d', '#7b5cd6']

/** 生成饼图配置 */
function pieOption(data: NameValue[]) {
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} 人 ({d}%)' },
    legend: { bottom: 0 },
    color: COLORS,
    series: [
      {
        type: 'pie',
        radius: ['40%', '68%'],
        center: ['50%', '45%'],
        label: { formatter: '{b}\n{d}%' },
        data: data.map((i) => ({ name: i.name, value: i.value }))
      }
    ]
  }
}

/** 生成柱状图配置 */
function barOption(data: NameValue[], unit: string) {
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 50, right: 24, top: 30, bottom: 70 },
    xAxis: {
      type: 'category',
      data: data.map((i) => i.name),
      axisLabel: { interval: 0, rotate: 30 }
    },
    yAxis: { type: 'value', name: unit },
    series: [
      {
        type: 'bar',
        barMaxWidth: 36,
        data: data.map((i) => i.value),
        itemStyle: { color: '#1a6fd4', borderRadius: [4, 4, 0, 0] }
      }
    ]
  }
}

function handleResize() {
  stageChart?.resize()
  gradeChart?.resize()
  genderChart?.resize()
}

onMounted(async () => {
  const data = await getStudentComposition()

  if (stageRef.value) {
    stageChart = echarts.init(stageRef.value)
    stageChart.setOption(pieOption(data.by_stage))
  }
  if (gradeRef.value) {
    gradeChart = echarts.init(gradeRef.value)
    gradeChart.setOption(barOption(data.by_grade, '人数'))
  }
  if (genderRef.value) {
    genderChart = echarts.init(genderRef.value)
    genderChart.setOption(pieOption(data.by_gender))
  }

  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  stageChart?.dispose()
  gradeChart?.dispose()
  genderChart?.dispose()
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
