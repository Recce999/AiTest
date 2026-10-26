<template>
  <div>
    <div class="topbar">
      <div>
        <router-link :to="`/projects/${pid}/apis`">← 接口列表</router-link>
        <strong>执行报告</strong>
      </div>
      <div>{{ store.username }}</div>
    </div>

    <div class="page">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px">
        <h3 style="margin: 0">执行历史</h3>
        <el-button type="primary" :loading="running" @click="onRun">执行全部启用的用例</el-button>
      </div>

      <el-table :data="list" border v-loading="loading">
        <el-table-column prop="id" label="批次" width="80" />
        <el-table-column prop="total" label="总数" width="80" />
        <el-table-column prop="passed" label="通过" width="80" />
        <el-table-column prop="failed" label="失败" width="80" />
        <el-table-column label="通过率" width="100">
          <template #default="{ row }">
            {{ row.total ? Math.round((row.passed / row.total) * 100) : 0 }}%
          </template>
        </el-table-column>
        <el-table-column prop="duration_ms" label="耗时(ms)" width="110" />
        <el-table-column prop="created_at" label="执行时间" min-width="180" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/runs/${row.id}`)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '../api/request'
import { useUserStore } from '../stores/user'

const route = useRoute()
const store = useUserStore()
const pid = Number(route.params.pid)
const list = ref([])
const loading = ref(false)
const running = ref(false)

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
