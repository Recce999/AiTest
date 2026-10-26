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
  routes
})

// 路由守卫：没 token 一律回登录页，避免前端出现空白页
router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if (!token && to.path !== '/login') return '/login'
  if (token && to.path === '/login') return '/'
  return true
})

export default router
