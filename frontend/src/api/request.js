import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const request = axios.create({
  baseURL: '/api',
  timeout: 15000
})

// 请求拦截：自动带 token，业务代码里不用每次写
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 响应拦截：统一处理 code，业务代码只关心 data
request.interceptors.response.use(
  (res) => {
    const body = res.data
    if (body.code === 0) return body.data
    if (body.code === 401) {
      localStorage.removeItem('token')
      router.push('/login')
      ElMessage.warning(body.msg || '请先登录')
      return Promise.reject(new Error(body.msg))
    }
    ElMessage.error(body.msg || '请求失败')
    return Promise.reject(new Error(body.msg))
  },
  (err) => {
    ElMessage.error('网络异常，请确认后端已启动')
    return Promise.reject(err)
  }
)

export default request
