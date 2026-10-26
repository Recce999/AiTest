import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', component: () => import('../views/Login.vue') },
  { path: '/', component: () => import('../views/Projects.vue') },
  { path: '/projects/:pid/apis', component: () => import('../views/Apis.vue') },
  { path: '/apis/:aid/cases', component: () => import('../views/Cases.vue') },
  { path: '/projects/:pid/runs', component: () => import('../views/Runs.vue') },
  { path: '/runs/:id', component: () => import('../views/RunDetail.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

const TITLES = {
  '/login': '登录',
  '/': '项目管理'
}

// 路由守卫：没 token 一律回登录页，避免前端出现空白页
router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (!token && to.path !== '/login') return '/login'
  if (token && to.path === '/login') return '/'
  return true
})

// 浏览器标签页标题：让每个页面都有独立标识
router.afterEach((to) => {
  let name = TITLES[to.path]
  if (!name) {
    if (to.path.includes('/apis') && to.params.pid) name = '接口管理'
    else if (to.path.includes('/cases')) name = '用例管理'
    else if (to.path.startsWith('/runs/')) name = '报告详情'
    else if (to.path.includes('/runs')) name = '执行报告'
  }
  document.title = name ? `${name} · AITest` : 'AITest · 接口自动化测试平台'
})

export default router
