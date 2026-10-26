<template>
  <div>
    <div class="topbar">
      <div><router-link to="/">← 返回</router-link><strong>报告详情</strong></div>
      <div>{{ store.username }}</div>
    </div>

    <div class="page" v-loading="loading">
      <h3>批次 #{{ run.id }}</h3>
      <el-row :gutter="12" style="margin-bottom: 16px">
        <el-col :span="6"><el-card>总数<br /><strong>{{ run.total }}</strong></el-card></el-col>
        <el-col :span="6"><el-card>通过<br /><strong style="color: #2f6e4e">{{ run.passed }}</strong></el-card></el-col>
        <el-col :span="6"><el-card>失败<br /><strong style="color: #c0392b">{{ run.failed }}</strong></el-card></el-col>
        <el-col :span="6"><el-card>耗时<br /><strong>{{ run.duration_ms }} ms</strong></el-card></el-col>
      </el-row>

      <el-table :data="run.results" border>
        <el-table-column prop="case_name" label="用例" min-width="200" />
        <el-table-column label="结果" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'passed' ? 'success' : 'danger'" size="small">
              {{ row.status === 'passed' ? '通过' : row.status === 'failed' ? '失败' : '异常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status_code" label="状态码" width="90" />
        <el-table-column prop="duration_ms" label="耗时(ms)" width="100" />
        <el-table-column prop="error_msg" label="失败原因" min-width="200" />
        <el-table-column label="响应体" min-width="240">
          <template #default="{ row }">
            <el-popover width="500" trigger="click">
              <template #reference><el-button size="small" text type="primary">查看</el-button></template>
              <pre style="max-height: 300px; overflow: auto; font-size: 12px">{{ row.response_body }}</pre>
            </el-popover>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import request from '../api/request'
import { useUserStore } from '../stores/user'

const route = useRoute()
const store = useUserStore()
const run = ref({ id: '', total: 0, passed: 0, failed: 0, duration_ms: 0, results: [] })
const loading = ref(false)

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
