<template>
  <div>
    <div class="topbar">
      <div><strong>AITest</strong> · 接口自动化测试平台</div>
      <div>
        <span style="margin-right: 12px">{{ store.username }}</span>
        <el-button size="small" @click="onLogout">退出</el-button>
      </div>
    </div>

    <div class="page">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px">
        <h3 style="margin: 0">我的项目</h3>
        <el-button type="primary" @click="openCreate">新建项目</el-button>
      </div>

      <el-table :data="list" border v-loading="loading">
        <el-table-column prop="name" label="项目名称" min-width="160" />
        <el-table-column prop="base_url" label="Base URL" min-width="220" />
        <el-table-column prop="description" label="描述" min-width="180" />
        <el-table-column label="操作" width="240">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/projects/${row.id}/apis`)">接口</el-button>
            <el-button size="small" @click="$router.push(`/projects/${row.id}/runs`)">报告</el-button>
            <el-button size="small" type="danger" plain @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-dialog v-model="dialog" title="新建项目" width="480px">
        <el-form :model="form" label-width="90px">
          <el-form-item label="项目名称"><el-input v-model="form.name" /></el-form-item>
          <el-form-item label="Base URL">
            <el-input v-model="form.base_url" placeholder="http://127.0.0.1:8000" />
          </el-form-item>
          <el-form-item label="描述"><el-input v-model="form.description" /></el-form-item>
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
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '../api/request'
import { useUserStore } from '../stores/user'

const store = useUserStore()
const router = useRouter()
const list = ref([])
const loading = ref(false)
const dialog = ref(false)
const form = reactive({ name: '', base_url: '', description: '' })

async function load() {
  loading.value = true
  try {
    list.value = await request.get('/projects')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  Object.assign(form, { name: '', base_url: '', description: '' })
  dialog.value = true
}

async function onCreate() {
  if (!form.name || !form.base_url) return ElMessage.warning('名称和 Base URL 必填')
  await request.post('/projects', { ...form })
  ElMessage.success('创建成功')
  dialog.value = false
  load()
}

async function onDelete(row) {
  await ElMessageBox.confirm(`确定删除「${row.name}」？其下接口和用例会一并删除`, '提示', { type: 'warning' })
  await request.delete(`/projects/${row.id}`)
  ElMessage.success('已删除')
  load()
}

function onLogout() {
  store.logout()
  router.push('/login')
}

onMounted(load)
</script>
