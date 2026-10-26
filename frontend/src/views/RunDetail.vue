<template>
  <div v-loading="loading" class="detail-page">
    <div class="detail-head">
      <button class="back-link" type="button" @click="router.back()">
        <el-icon><ArrowLeft /></el-icon>
        返回报告
      </button>
      <div class="head-row">
        <h1 class="page-title">批次 <span class="mono">#{{ run.id }}</span></h1>
        <el-tag class="batch-tag" round size="small">执行详情</el-tag>
      </div>
      <p class="page-sub">共 {{ run.total }} 条用例结果 · 失败 {{ run.failed }} 条</p>
    </div>

    <div class="section-card hero">
      <div class="ring-wrap">
        <el-progress
          type="circle"
          :percentage="passRate"
          :width="140"
          :stroke-width="10"
          :color="ringColor"
        >
          <template #default="{ percentage }">
            <div class="ring-value">{{ percentage }}<span class="ring-unit">%</span></div>
            <div class="ring-label">通过率</div>
          </template>
        </el-progress>
      </div>

      <div class="detail-stats">
        <div class="stat-card mini">
          <span class="stat-icon bg-indigo"><el-icon><Tickets /></el-icon></span>
          <div>
            <div class="stat-value">{{ run.total }}</div>
            <div class="stat-label">用例总数</div>
          </div>
        </div>
        <div class="stat-card mini">
          <span class="stat-icon bg-emerald"><el-icon><CircleCheckFilled /></el-icon></span>
          <div>
            <div class="stat-value value-pass">{{ run.passed }}</div>
            <div class="stat-label">通过</div>
          </div>
        </div>
        <div class="stat-card mini">
          <span class="stat-icon bg-rose"><el-icon><CircleCloseFilled /></el-icon></span>
          <div>
            <div class="stat-value value-fail">{{ run.failed }}</div>
            <div class="stat-label">失败</div>
          </div>
        </div>
        <div class="stat-card mini">
          <span class="stat-icon bg-amber"><el-icon><Timer /></el-icon></span>
          <div>
            <div class="stat-value">{{ run.duration_ms }}<span class="unit">ms</span></div>
            <div class="stat-label">总耗时</div>
          </div>
        </div>
      </div>
    </div>

    <div class="section-card result-card">
      <div class="card-head">
        <div class="card-title">用例结果</div>
        <span class="muted card-sub">{{ run.results.length }} 条记录</span>
      </div>

      <el-table :data="run.results" class="result-table">
        <el-table-column prop="case_name" label="用例" min-width="200">
          <template #default="{ row }">
            <span class="case-name">{{ row.case_name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="96">
          <template #default="{ row }">
            <el-tag
              size="small"
              :type="row.status === 'passed' ? 'success' : row.status === 'failed' ? 'danger' : 'info'"
              disable-transitions
            >
              {{ row.status === 'passed' ? '通过' : row.status === 'failed' ? '失败' : '异常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态码" width="90">
          <template #default="{ row }">
            <span class="mono">{{ row.status_code ?? '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="耗时" width="104">
          <template #default="{ row }">
            <span class="mono">{{ row.duration_ms }} ms</span>
          </template>
        </el-table-column>
        <el-table-column label="失败原因" min-width="220">
          <template #default="{ row }">
            <span v-if="row.error_msg" class="error-text">{{ row.error_msg }}</span>
            <span v-else class="muted">—</span>
          </template>
        </el-table-column>
        <el-table-column label="响应体" width="100" align="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="openBody(row)">查看</el-button>
          </template>
        </el-table-column>

        <template #empty>
          <div class="empty-hint">
            <el-icon><Document /></el-icon>
            <div class="empty-title">本次执行没有结果</div>
            <div>请确认项目中存在已启用的用例</div>
          </div>
        </template>
      </el-table>
    </div>

    <el-drawer v-model="drawerVisible" size="560px" class="body-drawer">
      <template #header>
        <div class="drawer-head">
          <div>
            <div class="drawer-title">响应体</div>
            <div class="drawer-sub muted">{{ currentCase }}</div>
          </div>
          <el-button size="small" :icon="CopyDocument" @click="copyBody">复制</el-button>
        </div>
      </template>
      <pre class="json-view mono">{{ prettyBody }}</pre>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  CircleCheckFilled,
  CircleCloseFilled,
  CopyDocument,
  Document,
  Tickets,
  Timer
} from '@element-plus/icons-vue'
import request from '../api/request'

const route = useRoute()
const router = useRouter()
const run = ref({ id: '', total: 0, passed: 0, failed: 0, duration_ms: 0, results: [] })
const loading = ref(false)
const drawerVisible = ref(false)
const currentRow = ref(null)

const passRate = computed(() => {
  if (!run.value.total) return 0
  return Math.round((run.value.passed / run.value.total) * 100)
})

const ringColor = computed(() => (passRate.value >= 80 ? '#10B981' : '#6366F1'))

const currentCase = computed(() => currentRow.value?.case_name || '')

const prettyBody = computed(() => formatJson(currentRow.value?.response_body))

function formatJson(value) {
  if (value === null || value === undefined || value === '') return '（空响应）'
  if (typeof value === 'object') {
    try {
      return JSON.stringify(value, null, 2)
    } catch {
      return String(value)
    }
  }
  try {
    return JSON.stringify(JSON.parse(value), null, 2)
  } catch {
    return String(value)
  }
}

function openBody(row) {
  currentRow.value = row
  drawerVisible.value = true
}

async function copyBody() {
  const text = prettyBody.value
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text)
    } else {
      const textarea = document.createElement('textarea')
      textarea.value = text
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
    }
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败，请手动选择文本')
  }
}

async function load() {
  loading.value = true
  try {
    run.value = await request.get(`/runs/${route.params.id}`)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.detail-page {
  min-height: 320px;
}

.detail-head {
  margin-bottom: 22px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 10px;
  padding: 0;
  border: none;
  background: none;
  color: #64748b;
  font-size: 12.5px;
  font-family: inherit;
  cursor: pointer;
}

.back-link:hover {
  color: #6366f1;
}

.head-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.batch-tag {
  background: #eef2ff;
  color: #4f46e5;
  border-color: transparent;
}

.hero {
  display: flex;
  align-items: center;
  gap: 36px;
  padding: 26px 28px;
  margin-bottom: 20px;
}

.ring-wrap {
  flex: 0 0 140px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ring-value {
  font-size: 26px;
  font-weight: 700;
  color: #111827;
  line-height: 1.1;
}

.ring-unit {
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
}

.ring-label {
  margin-top: 4px;
  font-size: 12px;
  color: #64748b;
}

.detail-stats {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.stat-card.mini {
  padding: 16px;
  box-shadow: none;
  background: #fbfbfe;
  border-color: #eef1f7;
}

.stat-card.mini .stat-icon {
  width: 40px;
  height: 40px;
  flex: 0 0 40px;
  border-radius: 11px;
  font-size: 18px;
}

.stat-card.mini .stat-value {
  font-size: 21px;
}

.stat-icon.bg-indigo {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
}

.stat-icon.bg-emerald {
  background: linear-gradient(135deg, #10b981, #34d399);
}

.stat-icon.bg-rose {
  background: linear-gradient(135deg, #ef4444, #f87171);
}

.stat-icon.bg-amber {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
}

.value-pass {
  color: #059669;
}

.value-fail {
  color: #dc2626;
}

.unit {
  margin-left: 2px;
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
}

.result-card {
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
  font-size: 12px;
}

.case-name {
  font-weight: 500;
  color: #1f2937;
}

.error-text {
  color: #dc2626;
  font-size: 12.5px;
  line-height: 1.5;
}

.drawer-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.drawer-title {
  font-size: 15px;
  font-weight: 600;
  color: #111827;
}

.drawer-sub {
  margin-top: 3px;
  font-size: 12px;
  font-weight: 400;
}

.json-view {
  margin: 0;
  padding: 18px;
  border-radius: 12px;
  background: #0f172a;
  color: #e2e8f0;
  font-size: 12px;
  line-height: 1.75;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: calc(100vh - 190px);
  overflow: auto;
}

@media (max-width: 900px) {
  .hero {
    flex-direction: column;
    gap: 24px;
  }

  .detail-stats {
    width: 100%;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 520px) {
  .detail-stats {
    grid-template-columns: 1fr;
  }
}
</style>
