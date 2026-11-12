<template>
  <div class="page-container">
    <div class="sc-card">
      <!-- 筛选条 -->
      <el-form :inline="true" class="search-bar" @submit.prevent>
        <el-form-item label="学期">
          <el-select v-model="query.semester_id" placeholder="全部学期" clearable style="width: 180px">
            <el-option v-for="item in semesterOptions" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="考试类型">
          <el-select v-model="query.exam_type" placeholder="全部" clearable style="width: 140px">
            <el-option v-for="item in examTypeOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 图表 -->
      <div class="chart-grid">
        <div class="chart-box">
          <div class="chart-title">各学科平均分 / 及格率 / 优秀率</div>
          <div ref="courseRef" class="chart"></div>
        </div>
        <div class="chart-box">
          <div class="chart-title">分数段分布</div>
          <div ref="distributionRef" class="chart"></div>
        </div>
      </div>

      <!-- 明细表格 -->
      <div class="table-toolbar" style="margin-top: 16px">
        <span class="title">学科成绩明细</span>
      </div>
      <el-table v-loading="loading" :data="analysis?.by_course ?? []" border stripe>
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column prop="course_name" label="学科" min-width="120" />
        <el-table-column prop="average" label="平均分" min-width="100" align="center" />
        <el-table-column label="及格率" min-width="100" align="center">
          <template #default="{ row }">{{ row.pass_rate }}%</template>
        </el-table-column>
        <el-table-column label="优秀率" min-width="100" align="center">
          <template #default="{ row }">{{ row.excellent_rate }}%</template>
        </el-table-column>
        <el-table-column prop="count" label="参考人数" min-width="100" align="center" />
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import * as echarts from 'echarts'
import { getScoreAnalysis } from '@/api/dashboard'
import { listSemesterOptions } from '@/api/semester'
import type { OptionItem, ScoreAnalysis } from '@/types/api'

/** 考试类型可选项 */
const examTypeOptions = ['月考', '期中', '期末', '单元测试']

const loading = ref(false)
const analysis = ref<ScoreAnalysis | null>(null)
const semesterOptions = ref<OptionItem[]>([])
const query = reactive<{ semester_id: number | undefined; exam_type: string | undefined }>({
  semester_id: undefined,
  exam_type: undefined
})

const courseRef = ref<HTMLDivElement>()
const distributionRef = ref<HTMLDivElement>()
let courseChart: echarts.ECharts | null = null
let distributionChart: echarts.ECharts | null = null

function renderCharts() {
  const data = analysis.value
  const courses = data?.by_course ?? []

  if (courseRef.value) {
    if (!courseChart) courseChart = echarts.init(courseRef.value)
    courseChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { top: 0, data: ['平均分', '及格率', '优秀率'] },
      grid: { left: 50, right: 24, top: 40, bottom: 70 },
      xAxis: {
        type: 'category',
        data: courses.map((i) => i.course_name),
        axisLabel: { interval: 0, rotate: 30 }
      },
      yAxis: { type: 'value', name: '数值', max: 100 },
      series: [
        {
          name: '平均分',
          type: 'bar',
          barMaxWidth: 22,
          data: courses.map((i) => i.average),
          itemStyle: { color: '#1a6fd4', borderRadius: [4, 4, 0, 0] }
        },
        {
          name: '及格率',
          type: 'bar',
          barMaxWidth: 22,
          data: courses.map((i) => i.pass_rate),
          itemStyle: { color: '#0f9b8e', borderRadius: [4, 4, 0, 0] }
        },
        {
          name: '优秀率',
          type: 'bar',
          barMaxWidth: 22,
          data: courses.map((i) => i.excellent_rate),
          itemStyle: { color: '#e8a33d', borderRadius: [4, 4, 0, 0] }
        }
      ]
    })
  }

  const dist = data?.distribution ?? []
  if (distributionRef.value) {
    if (!distributionChart) distributionChart = echarts.init(distributionRef.value)
    distributionChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 50, right: 24, top: 30, bottom: 50 },
      xAxis: { type: 'category', data: dist.map((i) => i.range_name) },
      yAxis: { type: 'value', name: '人数' },
      series: [
        {
          type: 'bar',
          barMaxWidth: 46,
          data: dist.map((i) => i.count),
          itemStyle: { color: '#4d9bf5', borderRadius: [4, 4, 0, 0] }
        }
      ]
    })
  }
}

function handleResize() {
  courseChart?.resize()
  distributionChart?.resize()
}

async function loadData() {
  loading.value = true
  try {
    analysis.value = await getScoreAnalysis({
      semester_id: query.semester_id,
      exam_type: query.exam_type
    })
    renderCharts()
  } finally {
    loading.value = false
  }
}

function handleReset() {
  query.semester_id = undefined
  query.exam_type = undefined
  loadData()
}

onMounted(async () => {
  semesterOptions.value = await listSemesterOptions()
  await loadData()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  courseChart?.dispose()
  distributionChart?.dispose()
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
