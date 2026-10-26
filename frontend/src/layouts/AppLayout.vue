<template>
  <div class="app-shell">
    <aside class="sidebar" :class="{ 'is-open': mobileOpen }">
      <div class="brand">
        <div class="brand-logo">AI</div>
        <div class="brand-text">
          <div class="brand-name">AITest</div>
          <div class="brand-sub">接口自动化测试平台</div>
        </div>
      </div>

      <nav class="nav">
        <div class="nav-group">工作台</div>
        <router-link to="/" class="nav-item" :class="{ active: isProjects }">
          <el-icon><Folder /></el-icon>
          <span>项目管理</span>
        </router-link>
        <router-link
          v-if="projectId"
          :to="`/projects/${projectId}/runs`"
          class="nav-item"
          :class="{ active: isRuns }"
        >
          <el-icon><TrendCharts /></el-icon>
          <span>执行报告</span>
        </router-link>
        <div v-else class="nav-item is-disabled" title="请先在项目管理中选择一个项目">
          <el-icon><TrendCharts /></el-icon>
          <span>执行报告</span>
          <span class="nav-hint">先选项目</span>
        </div>

        <div class="nav-group">当前项目</div>
        <router-link
          v-if="projectId"
          :to="`/projects/${projectId}/apis`"
          class="nav-item"
          :class="{ active: isApis }"
        >
          <el-icon><Connection /></el-icon>
          <span>接口管理</span>
        </router-link>
        <div v-else class="nav-item is-disabled" title="请先在项目管理中选择一个项目">
          <el-icon><Connection /></el-icon>
          <span>接口管理</span>
          <span class="nav-hint">先选项目</span>
        </div>

        <router-link
          v-if="apiId"
          :to="`/apis/${apiId}/cases`"
          class="nav-item"
          :class="{ active: isCases }"
        >
          <el-icon><Document /></el-icon>
          <span>用例管理</span>
        </router-link>
        <div v-else class="nav-item is-disabled" title="请从接口列表进入某个接口的用例">
          <el-icon><Document /></el-icon>
          <span>用例管理</span>
          <span class="nav-hint">从接口进入</span>
        </div>
      </nav>

      <div class="sidebar-foot">AITest · v0.2.0</div>
    </aside>

    <div v-if="mobileOpen" class="sidebar-mask" @click="mobileOpen = false"></div>

    <div class="main">
      <header class="app-topbar">
        <el-button class="menu-btn" text :icon="Menu" title="打开菜单" @click="mobileOpen = true" />
        <el-breadcrumb class="crumb" separator="/">
          <el-breadcrumb-item
            v-for="(item, index) in crumbs"
            :key="index"
            :to="item.to || undefined"
          >
            {{ item.label }}
          </el-breadcrumb-item>
        </el-breadcrumb>

        <div class="topbar-right">
          <span class="online"><span class="online-dot"></span>服务在线</span>
          <el-dropdown trigger="click" @command="onCommand">
            <div class="user-chip">
              <span class="avatar">{{ initial }}</span>
              <span class="user-name">{{ store.username || '未登录' }}</span>
              <el-icon class="caret"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <main class="content">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowDown,
  Connection,
  Document,
  Folder,
  Menu,
  TrendCharts
} from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const store = useUserStore()

const mobileOpen = ref(false)

// 从报告详情或接口详情进入时，路由里没有项目 id，用上次访问的项目补全上下文
const lastProjectId = ref(localStorage.getItem('lastProjectId') || '')
const lastApiId = ref(localStorage.getItem('lastApiId') || '')

watch(
  () => route.params.pid,
  (pid) => {
    if (!pid) return
    lastProjectId.value = String(pid)
    localStorage.setItem('lastProjectId', String(pid))
  },
  { immediate: true }
)

watch(
  () => route.params.aid,
  (aid) => {
    if (!aid) return
    lastApiId.value = String(aid)
    localStorage.setItem('lastApiId', String(aid))
  },
  { immediate: true }
)

const projectId = computed(() => route.params.pid || lastProjectId.value)
const apiId = computed(() => route.params.aid || lastApiId.value)

const isProjects = computed(() => route.path === '/')
const isApis = computed(() => !!projectId.value && route.path.startsWith(`/projects/${projectId.value}/apis`))
const isRuns = computed(
  () => (!!projectId.value && route.path.startsWith(`/projects/${projectId.value}/runs`)) || route.path.startsWith('/runs/')
)
const isCases = computed(() => !!apiId.value && route.path.includes('/cases'))

const initial = computed(() => (store.username ? store.username.charAt(0).toUpperCase() : '?'))

const crumbs = computed(() => {
  const path = route.path
  const items = [{ label: '项目', to: '/' }]

  if (projectId.value) {
    if (path.includes('/apis')) items.push({ label: '接口', to: `/projects/${projectId.value}/apis` })
    if (path.includes('/cases')) items.push({ label: '用例' })
    if (path.includes('/runs') && !path.startsWith('/runs/')) {
      items.push({ label: '报告', to: `/projects/${projectId.value}/runs` })
    }
  } else if (apiId.value) {
    items.push({ label: '接口' })
    if (path.includes('/cases')) items.push({ label: '用例' })
  }

  if (path.startsWith('/runs/')) {
    if (lastProjectId.value) items.push({ label: '报告', to: `/projects/${lastProjectId.value}/runs` })
    else items.push({ label: '报告' })
    items.push({ label: '详情' })
  }

  return items
})

function onCommand(command) {
  if (command === 'logout') {
    store.logout()
    router.push('/login')
  }
}

watch(() => route.fullPath, () => {
  mobileOpen.value = false
})
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: var(--app-bg);
}

.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 224px;
  z-index: 50;
  display: flex;
  flex-direction: column;
  padding: 0 12px 16px;
  background: #111827;
  background-image: radial-gradient(circle at 50% 0%, rgba(99, 102, 241, 0.18), transparent 55%);
  color: #94a3b8;
  overflow-y: auto;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 22px 8px 18px;
}

.brand-logo {
  width: 38px;
  height: 38px;
  flex: 0 0 38px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: #fff;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  box-shadow: 0 8px 18px rgba(99, 102, 241, 0.45);
}

.brand-name {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.brand-sub {
  margin-top: 3px;
  font-size: 11px;
  color: #64748b;
}

.nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-group {
  padding: 14px 10px 6px;
  font-size: 11px;
  letter-spacing: 0.12em;
  color: #475569;
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  height: 42px;
  padding: 0 12px;
  border-radius: 10px;
  font-size: 13.5px;
  color: #94a3b8;
  text-decoration: none;
  cursor: pointer;
  transition: background 0.16s ease, color 0.16s ease, transform 0.16s ease;
}

.nav-item .el-icon {
  font-size: 17px;
}

.nav-item:hover:not(.is-disabled) {
  background: #1e293b;
  color: #e2e8f0;
  transform: translateX(2px);
}

.nav-item.active {
  background: rgba(99, 102, 241, 0.16);
  color: #fff;
  font-weight: 500;
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: -12px;
  top: 9px;
  bottom: 9px;
  width: 3px;
  border-radius: 0 3px 3px 0;
  background: #6366f1;
}

.nav-item.is-disabled {
  color: #475569;
  cursor: not-allowed;
}

.nav-hint {
  margin-left: auto;
  padding: 2px 6px;
  border-radius: 5px;
  background: #1e293b;
  color: #64748b;
  font-size: 10px;
}

.sidebar-foot {
  padding: 14px 10px 0;
  border-top: 1px solid #1f2937;
  font-size: 11px;
  color: #475569;
}

.sidebar-mask {
  position: fixed;
  inset: 0;
  z-index: 45;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(2px);
  display: none;
}

.main {
  margin-left: 224px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-topbar {
  position: sticky;
  top: 0;
  z-index: 30;
  height: 60px;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 0 24px;
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(14px) saturate(1.6);
  border-bottom: 1px solid var(--app-card-border);
}

.menu-btn {
  display: none;
  width: 36px;
  height: 36px;
  padding: 0;
  font-size: 18px;
  color: #475569;
}

.crumb {
  min-width: 0;
}

.topbar-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 18px;
}

.online {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  color: #64748b;
  white-space: nowrap;
}

.online-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.16);
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 4px 8px 4px 4px;
  border-radius: 999px;
  cursor: pointer;
  transition: background 0.15s ease;
  outline: none;
}

.user-chip:hover {
  background: #f5f7fb;
}

.avatar {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
}

.user-name {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  color: #334155;
}

.caret {
  font-size: 12px;
  color: #94a3b8;
}

.content {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px;
  flex: 1;
}

/* 页面切换：轻微上浮 + 淡入，避免生硬跳转 */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (prefers-reduced-motion: reduce) {
  .page-enter-active,
  .page-leave-active,
  .nav-item {
    transition: none;
  }
}

@media (max-width: 900px) {
  .sidebar {
    transform: translateX(-100%);
    transition: transform 0.22s ease;
    box-shadow: 12px 0 32px rgba(15, 23, 42, 0.24);
  }

  .sidebar.is-open {
    transform: translateX(0);
  }

  .sidebar-mask {
    display: block;
  }

  .main {
    margin-left: 0;
  }

  .menu-btn {
    display: inline-flex;
  }

  .content {
    padding: 16px;
  }

  .app-topbar {
    padding: 0 16px;
  }
}

@media (max-width: 600px) {
  .crumb {
    display: none;
  }

  .online {
    display: none;
  }

  .topbar-right {
    margin-left: auto;
  }
}
</style>
