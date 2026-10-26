<template>
  <div class="page" style="max-width: 420px; margin-top: 80px">
    <el-card>
      <h2 style="margin-top: 0">AITest 接口测试平台</h2>
      <el-tabs v-model="tab">
        <el-tab-pane label="登录" name="login">
          <el-form :model="form" label-width="70px">
            <el-form-item label="用户名">
              <el-input v-model="form.username" placeholder="至少 3 位" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="form.password" type="password" show-password />
            </el-form-item>
            <el-button type="primary" :loading="loading" style="width: 100%" @click="onLogin">登录</el-button>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="注册" name="register">
          <el-form :model="form" label-width="70px">
            <el-form-item label="用户名">
              <el-input v-model="form.username" placeholder="至少 3 位" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="form.password" type="password" placeholder="至少 6 位" />
            </el-form-item>
            <el-button type="success" :loading="loading" style="width: 100%" @click="onRegister">注册</el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const tab = ref('login')
const loading = ref(false)
const form = reactive({ username: '', password: '' })
const store = useUserStore()
const router = useRouter()

async function onLogin() {
  if (!form.username || !form.password) return ElMessage.warning('请填写用户名和密码')
  loading.value = true
  try {
    await store.login({ ...form })
    ElMessage.success('登录成功')
    router.push('/')
  } finally {
    loading.value = false
  }
}

async function onRegister() {
  loading.value = true
  try {
    await store.register({ ...form })
    ElMessage.success('注册成功，请登录')
    tab.value = 'login'
  } finally {
    loading.value = false
  }
}
</script>
