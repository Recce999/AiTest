<template>
  <div>
    <div class="page-head">
      <div>
        <button class="back-link" type="button" @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回接口列表
        </button>
        <h1 class="page-title">用例管理</h1>
        <p class="page-sub">
          接口 <span class="mono">#{{ aid }}</span> · AI 生成的建议需确认后才会写入用例库
        </p>
      </div>
      <div class="page-actions">
        <el-button class="ai-btn" :icon="MagicStick" :loading="aiLoading" @click="onAiGenerate">
          AI 生成用例
        </el-button>
        <el-button :icon="Plus" @click="openCreate">新增用例</el-button>
      </div>
    </div>

    <div class="section-card list-card">
      <el-table :data="list" v-loading="loading" class="case-table">
        <el-table-column label="用例名" min-width="210">
          <template #default="{ row }">
            <span class="case-name">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="来源" width="92">
          <template #default="{ row }">
            <el-tag class="source-tag" :class="row.source === 'ai' ? 'source-ai' : 'source-manual'" disable-transitions>
              {{ row.source === 'ai' ? 'AI' : '手工' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="断言" min-width="300">
          <template #default="{ row }">
            <div v-if="assertionChips(row.assertions).length" class="chips">
              <span
                v-for="(chip, index) in assertionChips(row.assertions)"
                :key="index"
                class="chip"
                :class="chip.cls"
              >
                {{ chip.text }}
              </span>
            </div>
            <span v-else class="muted">无断言</span>
          </template>
        </el-table-column>
        <el-table-column label="启用" width="96">
          <template #default="{ row }">
            <span class="enabled-cell" :class="{ 'is-on': row.enabled }">
              <span class="status-dot"></span>
              {{ row.enabled ? '启用' : '停用' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="90" align="right">
          <template #default="{ row }">
            <el-button size="small" type="danger" link @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>

        <template #empty>
          <div class="empty-hint">
            <el-icon><Document /></el-icon>
            <div class="empty-title">还没有测试用例</div>
            <div>可以手动新增，或让 AI 根据接口定义生成候选用例</div>
          </div>
        </template>
      </el-table>
    </div>

    <!-- 手工新增 -->
    <el-dialog v-model="dialog" title="新增用例" width="560px">
      <el-form :model="form" label-position="top">
        <el-form-item label="用例名">
          <el-input v-model="form.name" placeholder="例如：健康检查 - 正常返回" />
        </el-form-item>
        <el-form-item label="请求参数">
          <el-input v-model="form.payloadText" type="textarea" :rows="2" placeholder='{"username":"test"}' />
        </el-form-item>
        <el-form-item label="断言">
          <el-input v-model="form.assertionsText" type="textarea" :rows="5"
            placeholder='[{"type":"status_code","expected":200}]' />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="onCreate">确定</el-button>
      </template>
    </el-dialog>

    <!-- AI 建议 -->
    <el-dialog v-model="aiDialog" title="AI 生成建议" width="720px">
      <p class="ai-tip">共 {{ candidates.length }} 条建议，确认后才会写入用例库</p>

      <div v-if="candidates.length" class="ai-list">
        <div v-for="(item, index) in candidates" :key="index" class="ai-card">
          <div class="ai-card-head">
            <span class="ai-index">{{ index + 1 }}</span>
            <span class="ai-name">{{ item.name }}</span>
            <el-button type="primary" size="small" @click="adopt(item)">采纳</el-button>
          </div>
          <div class="ai-payload mono">{{ payloadSummary(item.payload) }}</div>
          <div v-if="assertionChips(item.assertions).length" class="chips">
            <span
              v-for="(chip, i) in assertionChips(item.assertions)"
              :key="i"
              class="chip"
              :class="chip.cls"
            >
              {{ chip.text }}
            </span>
          </div>
        </div>
      </div>

      <div v-else class="empty-hint">
        <el-icon><MagicStick /></el-icon>
        <div class="empty-title">暂时没有可采纳的建议</div>
        <div>关闭弹窗后可以再试一次</div>
      </div>

      <template #footer>
        <el-button @click="aiDialog = false">关闭</el-button>
        <el-button type="primary" :disabled="!candidates.length" @click="adoptAll">全部采纳</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Document, MagicStick, Plus } from '@element-plus/icons-vue'
import request from '../api/request'

const route = useRoute()
const aid = Number(route.params.aid)

const list = ref([])
const loading = ref(false)
const aiLoading = ref(false)
const dialog = ref(false)
const aiDialog = ref(false)
const candidates = ref([])
const form = reactive({ name: '', payloadText: '', assertionsText: '' })

function assertionChips(assertions) {
  if (!Array.isArray(assertions) || !assertions.length) return []
  return assertions.map((item) => {
    const type = item?.type
    if (type === 'status_code') {
      return { text: `状态码 = ${item.expected}`, cls: 'chip-status' }
    }
    if (type === 'json_field') {
      return { text: `字段 ${item.path || '?'} = ${item.expected}`, cls: 'chip-field' }
    }
    if (type === 'max_duration') {
      return { text: `耗时 ≤ ${item.expected}ms`, cls: 'chip-time' }
    }
    return { text: `${type || '断言'} ${item?.expected ?? ''}`.trim(), cls: '' }
  })
}

function payloadSummary(payload) {
  if (!payload || (typeof payload === 'object' && !Object.keys(payload).length)) return '无请求参数'
  const text = typeof payload === 'string' ? payload : JSON.stringify(payload)
  return text.length > 120 ? `${text.slice(0, 120)}…` : text
}

async function load() {
  loading.value = true
  try {
    list.value = await request.get('/cases', { params: { api_id: aid } })
  } finally {
    loading.value = false
  }
}

function openCreate() {
  Object.assign(form, { name: '', payloadText: '', assertionsText: '[{"type":"status_code","expected":200}]' })
  dialog.value = true
}

async function onCreate() {
  let payload = {}
  let assertions = []
  try {
    payload = form.payloadText ? JSON.parse(form.payloadText) : {}
    assertions = JSON.parse(form.assertionsText || '[]')
  } catch {
    return ElMessage.error('JSON 格式不正确')
  }
  await request.post('/cases', { api_id: aid, name: form.name, payload, assertions, enabled: true })
  ElMessage.success('创建成功')
  dialog.value = false
  load()
}

async function onAiGenerate() {
  aiLoading.value = true
  try {
    candidates.value = await request.post('/cases/ai-generate', { api_id: aid, limit: 5 })
    aiDialog.value = true
  } finally {
    aiLoading.value = false
  }
}

async function adopt(row) {
  await request.post('/cases', {
    api_id: aid, name: row.name, payload: row.payload || {}, assertions: row.assertions, enabled: true
  })
  ElMessage.success('已采纳')
  load()
}

async function adoptAll() {
  for (const row of candidates.value) await adopt(row)
  aiDialog.value = false
}

async function onDelete(row) {
  await ElMessageBox.confirm(`确定删除用例「${row.name}」？`, '提示', { type: 'warning' })
  await request.delete(`/cases/${row.id}`)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<style scoped>
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 8px;
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

.list-card {
  padding: 6px 18px 10px;
  overflow: hidden;
}

.case-name {
  font-weight: 500;
  color: #1f2937;
}

.enabled-cell {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 12.5px;
  color: #94a3b8;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #cbd5e1;
}

.enabled-cell.is-on {
  color: #047857;
}

.enabled-cell.is-on .status-dot {
  background: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15);
}

.ai-btn {
  color: #fff;
  border: none;
  background: linear-gradient(135deg, #f59e0b, #f97316);
  box-shadow: 0 6px 16px rgba(245, 158, 11, 0.3);
}

.ai-btn:hover {
  color: #fff;
  background: linear-gradient(135deg, #fbbf24, #fb923c);
}

.ai-btn.is-loading {
  color: #fff;
}

.ai-tip {
  margin: -4px 0 16px;
  font-size: 12.5px;
  color: #64748b;
}

.ai-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 56vh;
  overflow-y: auto;
  padding-right: 2px;
}

.ai-card {
  padding: 14px 16px;
  border: 1px solid #e9edf5;
  border-radius: 12px;
  background: #fbfbfe;
  transition: border-color 0.16s ease, box-shadow 0.16s ease;
}

.ai-card:hover {
  border-color: #dcd6fb;
  box-shadow: 0 6px 18px rgba(99, 102, 241, 0.08);
}

.ai-card-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.ai-index {
  width: 22px;
  height: 22px;
  flex: 0 0 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 7px;
  background: #eef2ff;
  color: #4f46e5;
  font-size: 11px;
  font-weight: 700;
}

.ai-name {
  flex: 1;
  min-width: 0;
  font-size: 13.5px;
  font-weight: 600;
  color: #1f2937;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ai-payload {
  margin-bottom: 10px;
  padding: 8px 10px;
  border-radius: 8px;
  background: #f5f7fb;
  color: #64748b;
  font-size: 11.5px;
  word-break: break-all;
}
</style>
