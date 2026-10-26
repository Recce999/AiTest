<template>
  <div>
    <div class="page-head">
      <div>
        <div class="project-crumb">
          <span class="mono">项目 #{{ pid }}</span>
          <span class="dot">·</span>
          <span>执行报告</span>
        </div>
        <h1 class="page-title">执行报告</h1>
        <p class="page-sub">查看历史执行批次、通过率与失败情况</p>
      </div>
      <el-button type="primary" :icon="VideoPlay" :loading="running" @click="onRun">
        执行全部启用用例
      </el-button>
    </div>

    <div class="stat-grid runs-stats">
      <div class="stat-card">
        <span class="stat-icon bg-indigo"><el-icon><Tickets /></el-icon></span>
        <div>
          <div class="stat-value">{{ list.length }}</div>
          <div class="stat-label">执行批次</div>
        </div>
      </div>
      <div class="stat-card">
        <span class="stat-icon bg-violet"><el-icon><TrendCharts /></el-icon></span>
        <div>
          <div class="stat-value">{{ latest ? latestRate : 0 }}<span class="unit">%</span></div>
          <div class="stat-label">最近一次通过率</div>
        </div>
      </div>
      <div class="stat-card">
        <span class="stat-icon bg-emerald"><el-icon><CircleCheckFilled /></el-icon></span>
        <div>
          <div class="stat-value">{{ latest ? latest.passed : 0 }}</div>
          <div class="stat-label">最近通过</div>
        </div>
      </div>
      <div class="stat-card">
        <span class="stat-icon bg-rose"><el-icon><CircleCloseFilled /></el-icon></span>
        <div>
          <div class="stat-value">{{ latest ? latest.failed : 0 }}</div>
          <div class="stat-label">最近失败</div>
        </div>
      </div>
    </div>

    <div class="section-card list-card">
      <div class="card-head">
        <div>
          <div class="card-title">执行历史</div>
          <div class="card-sub muted">最近 20 次执行批次</div>
        </div>
      </div>

      <el-table :data="list" v-loading="loading" class="run-table">
        <el-table-column label="批次" width="88">
          <template #default="{ row }">
            <span class="mono batch-id">#{{ row.id }}</span>
          </template>
        </el-table-column>
        <el-table-column label="通过率" width="170">
          <template #default="{ row }">
            <el-progress
              :percentage="rate(row)"
              :stroke-width="7"
              :color="progressColor(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="total" label="总数" width="84" />
        <el-table-column label="通过" width="84">
          <template #default="{ row }">
            <span class="num-pass">{{ row.passed }}</span>
          </template>
        </el-table-column>
        <el-table-column label="失败" width="84">
          <template #default="{ row }">
            <span class="num-fail">{{ row.failed }}</span>
          </template>
        </el-table-column>
        <el-table-column label="耗时" width="104">
          <template #default="{ row }">
            <span class="mono">{{ row.duration_ms }} 毫秒</span>
          </template>
        </el-table-column>
        <el-table-column label="执行时间" min-width="170">
          <template #default="{ row }">
            <span class="muted">{{ formatTime(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="90" align="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="$router.push(`/runs/${row.id}`)">详情</el-button>
          </template>
        </el-table-column>

        <template #empty>
          <div class="empty-hint">
            <el-icon><DataAnalysis /></el-icon>
            <div class="empty-title">还没有执行记录</div>
            <div>先录入接口与用例，然后执行全部启用用例生成第一份报告</div>
            <el-button type="primary" :icon="VideoPlay" class="empty-btn" :loading="running" @click="onRun">
              立即执行
            </el-button>
          </div>
        </template>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  CircleCheckFilled,
  CircleCloseFilled,
  DataAnalysis,
  Tickets,
  TrendCharts,
  VideoPlay
} from '@element-plus/icons-vue'
import request from '../api/request'

const route = useRoute()
const pid = Number(route.params.pid)
const list = ref([])
const loading = ref(false)
const running = ref(false)

const latest = computed(() => list.value[0] || null)
const latestRate = computed(() => (latest.value ? rate(latest.value) : 0))

function rate(row) {
  if (!row || !row.total) return 0
  return Math.round((row.passed / row.total) * 100)
}

function progressColor(row) {
  const value = rate(row)
  if (value >= 80) return '#10B981'
  if (value >= 50) return '#F59E0B'
  return '#EF4444'
}

function formatTime(value) {
  if (!value) return '—'
  return String(value).replace('T', ' ').slice(0, 19)
}

async function load() {
  loading.value = true
  try {
    list.value = await request.get('/runs', { params: { project_id: pid } })
  } finally {
    loading.value = false
  }
}

async function onRun() {
  running.value = true
  try {
    const data = await request.post('/runs', { project_id: pid })
    ElMessage.success(`执行完成：总 ${data.total}，通过 ${data.passed}，失败 ${data.failed}`)
    load()
  } finally {
    running.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.project-crumb {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 12px;
  color: #6366f1;
}

.project-crumb .dot {
  color: #cbd5e1;
}

.runs-stats {
  margin-bottom: 20px;
}

.unit {
  margin-left: 1px;
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
}

.stat-icon.bg-indigo {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  box-shadow: 0 6px 14px rgba(99, 102, 241, 0.28);
}

.stat-icon.bg-violet {
  background: linear-gradient(135deg, #8b5cf6, #c084fc);
  box-shadow: 0 6px 14px rgba(139, 92, 246, 0.28);
}

.stat-icon.bg-emerald {
  background: linear-gradient(135deg, #10b981, #34d399);
  box-shadow: 0 6px 14px rgba(16, 185, 129, 0.28);
}

.stat-icon.bg-rose {
  background: linear-gradient(135deg, #ef4444, #f87171);
  box-shadow: 0 6px 14px rgba(239, 68, 68, 0.28);
}

.list-card {
  padding: 0 18px 10px;
  overflow: hidden;
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 2px 14px;
  border-bottom: 1px solid #eef1f7;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
}

.card-sub {
  margin-top: 3px;
  font-size: 12px;
}

.batch-id {
  color: #4f46e5;
  font-weight: 600;
}

.num-pass {
  color: #059669;
  font-weight: 600;
}

.num-fail {
  color: #dc2626;
  font-weight: 600;
}

.run-table :deep(.el-progress__text) {
  min-width: 34px;
  font-size: 12px !important;
  color: #475569;
}

@media (max-width: 1024px) {
  .stat-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  .stat-grid {
    grid-template-columns: 1fr;
  }
}
</style>
