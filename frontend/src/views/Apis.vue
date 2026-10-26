<template>
  <div>
    <div class="topbar">
      <div>
        <router-link to="/">← 项目列表</router-link>
        <strong>接口管理</strong>
      </div>
      <div>{{ store.username }}</div>
    </div>

    <div class="page">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px">
        <h3 style="margin: 0">接口列表</h3>
        <div>
          <el-button @click="$router.push(`/projects/${pid}/runs`)">执行报告</el-button>
          <el-button type="primary" @click="openCreate">新增接口</el-button>
        </div>
      </div>

      <el-table :data="list" border v-loading="loading">
        <el-table-column prop="method" label="方法" width="90" />
        <el-table-column prop="name" label="接口名" min-width="140" />
        <el-table-column prop="path" label="路径" min-width="180" />
        <el-table-column prop="expected_status" label="期望状态码" width="110" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/apis/${row.id}/cases`)">用例</el-button>
            <el-button size="small" type="danger" plain @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-dialog v-model="dialog" title="新增接口" width="520px">
        <el-form :model="form" label-width="100px">
          <el-form-item label="接口名"><el-input v-model="form.name" /></el-form-item>
          <el-form-item label="请求方法">
            <el-select v-model="form.method" style="width: 100%">
              <el-option v-for="m in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']" :key="m" :label="m" :value="m" />
            </el-select>
          </el-form-item>
          <el-form-item label="路径"><el-input v-model="form.path" placeholder="/health" /></el-form-item>
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
const pid = route.params.pid
const list = ref([])
const loading = ref(false)
const dialog = ref(false)
const form = reactive({
  name: '', method: 'GET', path: '/', headersText: '', bodyText: '', expected_status: 200
})

function parseJson(text, fallback) {
  if (!text || !text.trim()) return fallback
  try {
    return JSON.parse(text)
  } catch {
    ElMessage.error('JSON 格式不正确')
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

onMounted(load)
</script>
