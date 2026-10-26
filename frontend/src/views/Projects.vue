<template>
  <div>
    <div class="page-head">
      <div>
        <h1 class="page-title">我的项目</h1>
        <p class="page-sub">管理你的测试项目，进入后可维护接口、用例并查看执行报告</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openCreate">新建项目</el-button>
    </div>

    <div v-loading="loading" class="project-wrap">
      <div v-if="list.length" class="project-grid">
        <article v-for="p in list" :key="p.id" class="project-card">
          <div class="card-top">
            <span class="project-avatar" :class="`accent-${p.id % 4}`">
              {{ (p.name || 'P').charAt(0).toUpperCase() }}
            </span>
            <div class="card-title-wrap">
              <div class="project-name">{{ p.name }}</div>
              <div class="project-id">项目 #{{ p.id }}</div>
            </div>
          </div>

          <div class="url-box mono">{{ p.base_url }}</div>

          <p class="project-desc">{{ p.description || '暂无描述' }}</p>

          <div class="project-meta">
            <el-icon><Clock /></el-icon>
            <span>创建于 {{ formatTime(p.created_at) }}</span>
          </div>

          <div class="project-actions">
            <el-button type="primary" size="small" @click="goApis(p)">进入项目</el-button>
            <el-button size="small" text @click="goRuns(p)">执行报告</el-button>
            <el-button size="small" text type="danger" @click="onDelete(p)">删除</el-button>
          </div>
        </article>
      </div>

      <div v-else-if="!loading" class="empty-hint">
        <el-icon><FolderOpened /></el-icon>
        <div class="empty-title">还没有项目</div>
        <div>创建第一个项目，开始你的接口自动化测试</div>
        <el-button type="primary" :icon="Plus" class="empty-btn" @click="openCreate">新建项目</el-button>
      </div>
    </div>

    <el-dialog v-model="dialog" title="新建项目" width="480px">
      <el-form :model="form" label-position="top">
        <el-form-item label="项目名称">
          <el-input v-model="form.name" placeholder="例如：用户中心" />
        </el-form-item>
        <el-form-item label="Base URL">
          <el-input v-model="form.base_url" placeholder="http://127.0.0.1:8000" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="简单描述这个项目" />
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
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Clock, FolderOpened, Plus } from '@element-plus/icons-vue'
import request from '../api/request'

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

function goApis(row) {
  router.push(`/projects/${row.id}/apis`)
}

function goRuns(row) {
  router.push(`/projects/${row.id}/runs`)
}

function formatTime(value) {
  if (!value) return '—'
  return String(value).replace('T', ' ').slice(0, 19)
}

onMounted(load)
</script>

<style scoped>
.project-wrap {
  min-height: 240px;
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.project-card {
  display: flex;
  flex-direction: column;
  padding: 20px;
  background: #fff;
  border: 1px solid var(--app-card-border);
  border-radius: 14px;
  box-shadow: var(--app-shadow);
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}

.project-card:hover {
  transform: translateY(-2px);
  border-color: #dcd6fb;
  box-shadow: 0 14px 32px rgba(99, 102, 241, 0.12);
}

.card-top {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.project-avatar {
  width: 42px;
  height: 42px;
  flex: 0 0 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
}

.project-avatar.accent-1 {
  background: linear-gradient(135deg, #0ea5e9, #6366f1);
}

.project-avatar.accent-2 {
  background: linear-gradient(135deg, #10b981, #0ea5a4);
}

.project-avatar.accent-3 {
  background: linear-gradient(135deg, #f59e0b, #f97316);
}

.card-title-wrap {
  min-width: 0;
}

.project-name {
  font-size: 15px;
  font-weight: 600;
  color: #111827;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-id {
  margin-top: 3px;
  font-size: 11.5px;
  color: #94a3b8;
}

.url-box {
  padding: 9px 12px;
  border-radius: 9px;
  background: #f8fafc;
  border: 1px solid #eef1f7;
  font-size: 12px;
  color: #475569;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-desc {
  margin: 14px 0 0;
  min-height: 38px;
  font-size: 13px;
  line-height: 1.55;
  color: #64748b;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.project-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 14px;
  font-size: 12px;
  color: #94a3b8;
}

.project-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: auto;
  padding-top: 14px;
  border-top: 1px solid #f1f4f9;
}

.project-actions .el-button + .el-button {
  margin-left: 0;
}

@media (max-width: 560px) {
  .project-grid {
    grid-template-columns: 1fr;
  }
}
</style>
