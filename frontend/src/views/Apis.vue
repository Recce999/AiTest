<template>
  <div>
    <div class="page-head">
      <div>
        <div class="project-crumb">
          <span class="mono">项目 #{{ pid }}</span>
          <span class="dot">·</span>
          <span>{{ projectName }}</span>
        </div>
        <h1 class="page-title">接口管理</h1>
        <p class="page-sub">维护当前项目的接口定义，进入某个接口即可管理测试用例</p>
      </div>
      <div class="page-actions">
        <el-button text :icon="TrendCharts" @click="$router.push(`/projects/${pid}/runs`)">执行报告</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreate">新增接口</el-button>
      </div>
    </div>

    <div class="section-card list-card">
      <div class="filter-bar">
        <el-input
          v-model="keyword"
          class="filter-search"
          placeholder="搜索接口名或路径"
          clearable
          :prefix-icon="Search"
        />
        <span class="filter-label">请求方法</span>
        <div class="method-seg">
          <button
            v-for="m in ['ALL', ...methods]"
            :key="m"
            type="button"
            class="seg-btn"
            :class="{ active: methodFilter === m }"
            :title="m === 'ALL' ? '全部请求方法' : methodLabel(m)"
            @click="methodFilter = m"
          >
            {{ m === 'ALL' ? '全部' : m }}
          </button>
        </div>
        <span class="filter-count muted">共 {{ filtered.length }} 个接口</span>
      </div>

      <el-table :data="filtered" v-loading="loading" class="api-table">
        <el-table-column label="请求方法" width="100">
          <template #default="{ row }">
            <el-tag
              class="method-tag"
              :class="methodClass(row.method)"
              :title="methodLabel(row.method)"
              disable-transitions
            >
              {{ row.method }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="接口名" min-width="160">
          <template #default="{ row }">
            <span class="api-name">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="路径" min-width="220">
          <template #default="{ row }">
            <code class="mono path-code">{{ row.path }}</code>
          </template>
        </el-table-column>
        <el-table-column label="期望状态码" width="120">
          <template #default="{ row }">
            <span class="status-code mono">{{ row.expected_status }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="$router.push(`/projects/${pid}/apis/${row.id}/cases`)">用例</el-button>
            <el-button size="small" type="danger" link @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>

        <template #empty>
          <div class="empty-hint">
            <el-icon><Connection /></el-icon>
            <div class="empty-title">{{ list.length ? '没有匹配的接口' : '还没有接口' }}</div>
            <div>{{ list.length ? '换个关键字或请求方法再试试' : '点击右上角「新增接口」，录入第一个接口' }}</div>
          </div>
        </template>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="新增接口" width="520px">
      <el-form :model="form" label-position="top">
        <el-form-item label="接口名">
          <el-input v-model="form.name" placeholder="例如：健康检查" />
        </el-form-item>
        <el-form-item label="请求方法">
          <el-select v-model="form.method" style="width: 100%">
            <el-option v-for="m in methods" :key="m" :label="methodLabel(m)" :value="m" />
          </el-select>
        </el-form-item>
        <el-form-item label="路径">
          <el-input v-model="form.path" placeholder="/health" />
        </el-form-item>
        <el-form-item label="请求头">
          <el-input v-model="form.headersText" type="textarea" :rows="2" placeholder='{"Content-Type":"application/json"}' />
        </el-form-item>
        <el-form-item label="请求体">
          <el-input v-model="form.bodyText" type="textarea" :rows="3" placeholder='{"username":"test"}' />
        </el-form-item>
        <el-form-item label="期望状态码">
          <el-input-number v-model="form.expected_status" :min="100" :max="599" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="onCreate">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Connection, Plus, Search, TrendCharts } from '@element-plus/icons-vue'
import request from '../api/request'

const route = useRoute()
const pid = route.params.pid
const methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']

// HTTP 方法名是通用专有名词，界面上中文在前、英文原名放在括号里
const methodNames = {
  GET: '查询',
  POST: '新增',
  PUT: '更新',
  DELETE: '删除',
  PATCH: '局部更新'
}

function methodLabel(method) {
  return methodNames[method] ? `${methodNames[method]}（${method}）` : method
}

const list = ref([])
const loading = ref(false)
const dialog = ref(false)
const keyword = ref('')
const methodFilter = ref('ALL')
const projectName = ref(`项目 #${pid}`)

const form = reactive({
  name: '', method: 'GET', path: '/', headersText: '', bodyText: '', expected_status: 200
})

const filtered = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  return list.value.filter((row) => {
    const matchKeyword = !kw
      || (row.name || '').toLowerCase().includes(kw)
      || (row.path || '').toLowerCase().includes(kw)
    const matchMethod = methodFilter.value === 'ALL' || row.method === methodFilter.value
    return matchKeyword && matchMethod
  })
})

function methodClass(method) {
  const m = String(method || '').toLowerCase()
  return ['get', 'post', 'put', 'delete', 'patch'].includes(m) ? `method-${m}` : 'method-default'
}

function parseJson(text, fallback) {
  if (!text || !text.trim()) return fallback
  try {
    return JSON.parse(text)
  } catch {
    ElMessage.error('数据格式不正确（JSON）')
    throw new Error('invalid json')
  }
}

async function load() {
  loading.value = true
  try {
    list.value = await request.get('/apis', { params: { project_id: pid } })
  } finally {
    loading.value = false
  }
}

async function loadProjectName() {
  try {
    const projects = await request.get('/projects')
    const hit = (projects || []).find((p) => String(p.id) === String(pid))
    if (hit) projectName.value = hit.name
  } catch {
    // 项目名仅用于页头展示，失败时保留默认文案
  }
}

function openCreate() {
  Object.assign(form, { name: '', method: 'GET', path: '/', headersText: '', bodyText: '', expected_status: 200 })
  dialog.value = true
}

async function onCreate() {
  let headers = {}
  let body = {}
  try {
    headers = parseJson(form.headersText, {})
    body = parseJson(form.bodyText, {})
  } catch {
    return
  }
  await request.post('/apis', {
    project_id: Number(pid),
    name: form.name,
    method: form.method,
    path: form.path,
    headers,
    body,
    expected_status: form.expected_status
  })
  ElMessage.success('创建成功')
  dialog.value = false
  load()
}

async function onDelete(row) {
  await ElMessageBox.confirm(`确定删除接口「${row.name}」？`, '提示', { type: 'warning' })
  await request.delete(`/apis/${row.id}`)
  ElMessage.success('已删除')
  load()
}

onMounted(() => {
  load()
  loadProjectName()
})
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

.list-card {
  padding: 0;
  overflow: hidden;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 18px;
  border-bottom: 1px solid #eef1f7;
}

.filter-search {
  max-width: 300px;
}

.filter-label {
  font-size: 12px;
  color: #94a3b8;
  white-space: nowrap;
}

/* 方法筛选：分段控件，比下拉更直观 */
.method-seg {
  display: inline-flex;
  gap: 2px;
  padding: 3px;
  border-radius: 10px;
  background: #f1f4f9;
}

.seg-btn {
  height: 28px;
  padding: 0 12px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #64748b;
  font-family: var(--app-mono);
  font-size: 11.5px;
  font-weight: 600;
  letter-spacing: 0.03em;
  cursor: pointer;
  transition: background 0.16s ease, color 0.16s ease, box-shadow 0.16s ease;
}

.seg-btn:hover {
  color: #334155;
}

.seg-btn.active {
  background: #fff;
  color: #4f46e5;
  box-shadow: 0 1px 3px rgba(17, 24, 39, 0.1);
}

.filter-count {
  margin-left: auto;
  font-size: 12px;
  white-space: nowrap;
}

.api-table {
  padding: 0 6px;
}

.api-name {
  font-weight: 500;
  color: #1f2937;
}

.path-code {
  padding: 3px 8px;
  border-radius: 6px;
  background: #f5f7fb;
  color: #475569;
  font-size: 12px;
}

.status-code {
  color: #475569;
  font-size: 12px;
}

@media (max-width: 640px) {
  .filter-bar {
    flex-wrap: wrap;
  }

  .filter-search {
    max-width: none;
    flex: 1 1 100%;
  }

  .filter-count {
    margin-left: 0;
  }
}
</style>
