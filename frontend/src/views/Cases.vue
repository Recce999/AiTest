<template>
  <div>
    <div class="topbar">
      <div>
        <el-button text style="color: #cfe0f5" @click="$router.back()">← 接口列表</el-button>
        <strong>用例管理</strong>
      </div>
      <div>{{ store.username }}</div>
    </div>

    <div class="page">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px">
        <h3 style="margin: 0">测试用例</h3>
        <div>
          <el-button type="warning" plain :loading="aiLoading" @click="onAiGenerate">AI 生成用例</el-button>
          <el-button type="primary" @click="openCreate">新增用例</el-button>
        </div>
      </div>

      <el-table :data="list" border v-loading="loading">
        <el-table-column prop="name" label="用例名" min-width="200" />
        <el-table-column prop="source" label="来源" width="90">
          <template #default="{ row }">
            <el-tag :type="row.source === 'ai' ? 'warning' : 'info'" size="small">
              {{ row.source === 'ai' ? 'AI' : '手工' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="断言" min-width="240">
          <template #default="{ row }">
            <code style="font-size: 12px">{{ JSON.stringify(row.assertions) }}</code>
          </template>
        </el-table-column>
        <el-table-column label="启用" width="80">
          <template #default="{ row }">{{ row.enabled ? '是' : '否' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" type="danger" plain @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 手工新增 -->
      <el-dialog v-model="dialog" title="新增用例" width="560px">
        <el-form :model="form" label-width="90px">
          <el-form-item label="用例名"><el-input v-model="form.name" /></el-form-item>
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
      <el-dialog v-model="aiDialog" title="AI 生成建议（确认后才入库）" width="640px">
        <el-table :data="candidates" border size="small">
          <el-table-column prop="name" label="建议用例" min-width="260" />
          <el-table-column label="断言" min-width="220">
            <template #default="{ row }">
              <code style="font-size: 12px">{{ JSON.stringify(row.assertions) }}</code>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="90">
            <template #default="{ row }">
              <el-button size="small" type="success" @click="adopt(row)">采纳</el-button>
            </template>
          </el-table-column>
        </el-table>
        <template #footer>
          <el-button type="primary" @click="adoptAll">全部采纳</el-button>
          <el-button @click="aiDialog = false">关闭</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../api/request'
import { useUserStore } from '../stores/user'

const route = useRoute()
const store = useUserStore()
const aid = Number(route.params.aid)
const projectId = ref('')

const list = ref([])
const loading = ref(false)
const aiLoading = ref(false)
const dialog = ref(false)
const aiDialog = ref(false)
const candidates = ref([])
const form = reactive({ name: '', payloadText: '', assertionsText: '' })

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
