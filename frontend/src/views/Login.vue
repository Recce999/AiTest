<template>
  <div class="login-page">
    <section class="brand-side">
      <div class="grid-deco"></div>
      <div class="glow glow-1"></div>
      <div class="glow glow-2"></div>

      <div class="brand-content">
        <div class="brand-mark">
          <span class="brand-logo">AI</span>
          <span class="brand-word">AITest</span>
        </div>

        <h1 class="brand-title">让接口测试<br />像写文档一样简单</h1>
        <p class="brand-desc">录入接口 → AI 生成用例 → 一键执行 → 可视化报告</p>

        <ul class="feature-list">
          <li>
            <span class="feature-icon"><el-icon><Key /></el-icon></span>
            <div>
              <div class="feature-title">JWT 鉴权</div>
              <div class="feature-text">登录态全链路校验，接口数据按用户隔离</div>
            </div>
          </li>
          <li>
            <span class="feature-icon"><el-icon><CircleCheck /></el-icon></span>
            <div>
              <div class="feature-title">三类断言</div>
              <div class="feature-text">状态码、JSON 字段与响应耗时，一次覆盖</div>
            </div>
          </li>
          <li>
            <span class="feature-icon"><el-icon><Lock /></el-icon></span>
            <div>
              <div class="feature-title">SSRF 防护</div>
              <div class="feature-text">执行前校验目标地址，阻断内网探测风险</div>
            </div>
          </li>
        </ul>
      </div>

      <div class="brand-foot">AITest · 接口自动化测试平台 v0.2.0</div>
    </section>

    <section class="form-side">
      <div class="form-card">
        <div class="form-head">
          <h2>欢迎回来</h2>
          <p>登录后开始管理你的接口与用例</p>
        </div>

        <el-tabs v-model="tab" class="auth-tabs">
          <el-tab-pane label="登录" name="login">
            <el-form :model="form" label-position="top" size="large">
              <el-form-item label="用户名">
                <el-input v-model="form.username" placeholder="至少 3 位" :prefix-icon="User" />
              </el-form-item>
              <el-form-item label="密码">
                <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" :prefix-icon="Lock" />
              </el-form-item>
              <el-button type="primary" size="large" class="submit-btn" :loading="loading" @click="onLogin">
                登录
              </el-button>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="注册" name="register">
            <el-form :model="form" label-position="top" size="large">
              <el-form-item label="用户名">
                <el-input v-model="form.username" placeholder="至少 3 位" :prefix-icon="User" />
              </el-form-item>
              <el-form-item label="密码">
                <el-input v-model="form.password" type="password" placeholder="至少 6 位" :prefix-icon="Lock" />
              </el-form-item>
              <el-button type="primary" size="large" class="submit-btn" :loading="loading" @click="onRegister">
                注册
              </el-button>
            </el-form>
          </el-tab-pane>
        </el-tabs>

        <p class="form-tip">登录即表示同意 AITest 的使用条款与隐私说明</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { CircleCheck, Key, Lock, User } from '@element-plus/icons-vue'
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

<style scoped>
.login-page {
  display: flex;
  min-height: 100vh;
  background: #f5f7fb;
}

/* ---------- 左侧品牌区 ---------- */
.brand-side {
  position: relative;
  flex: 0 0 55%;
  max-width: 55%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 64px 8% 64px 9%;
  color: #fff;
  background: linear-gradient(135deg, #4f46e5 0%, #6366f1 42%, #8b5cf6 100%);
}

.grid-deco {
  position: absolute;
  inset: 0;
  opacity: 0.32;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.08) 1px, transparent 1px);
  background-size: 46px 46px;
  mask-image: radial-gradient(ellipse at 30% 20%, #000 20%, transparent 75%);
}

.glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(2px);
  pointer-events: none;
}

.glow-1 {
  width: 360px;
  height: 360px;
  right: -80px;
  top: -90px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.24), transparent 68%);
}

.glow-2 {
  width: 300px;
  height: 300px;
  left: -60px;
  bottom: -80px;
  background: radial-gradient(circle, rgba(129, 140, 248, 0.5), transparent 70%);
}

.brand-content {
  position: relative;
  z-index: 1;
  max-width: 520px;
}

.brand-mark {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 46px;
}

.brand-logo {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 13px;
  background: rgba(255, 255, 255, 0.16);
  border: 1px solid rgba(255, 255, 255, 0.28);
  font-size: 15px;
  font-weight: 700;
  backdrop-filter: blur(6px);
}

.brand-word {
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.brand-title {
  margin: 0 0 18px;
  font-size: 40px;
  line-height: 1.28;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.brand-desc {
  margin: 0 0 46px;
  font-size: 15px;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.8);
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.feature-list li {
  display: flex;
  align-items: flex-start;
  gap: 14px;
}

.feature-icon {
  width: 38px;
  height: 38px;
  flex: 0 0 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 11px;
  background: rgba(255, 255, 255, 0.13);
  border: 1px solid rgba(255, 255, 255, 0.18);
  font-size: 18px;
}

.feature-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 3px;
}

.feature-text {
  font-size: 12.5px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.68);
}

.brand-foot {
  position: absolute;
  left: 9%;
  bottom: 28px;
  z-index: 1;
  font-size: 11px;
  letter-spacing: 0.06em;
  color: rgba(255, 255, 255, 0.45);
}

/* ---------- 右侧表单区 ---------- */
.form-side {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 32px;
}

.form-card {
  width: 100%;
  max-width: 420px;
  padding: 36px 34px;
  background: #fff;
  border: 1px solid var(--app-card-border);
  border-radius: 14px;
  box-shadow: 0 6px 20px rgba(17, 24, 39, 0.05);
}

.form-head h2 {
  margin: 0 0 8px;
  font-size: 26px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: #111827;
}

.form-head p {
  margin: 0 0 26px;
  font-size: 13px;
  color: #64748b;
}

.auth-tabs :deep(.el-tabs__header) {
  margin-bottom: 24px;
}

.auth-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background: #eef1f7;
}

.auth-tabs :deep(.el-tabs__item) {
  height: 44px;
  padding: 0 4px;
  margin-right: 26px;
  font-size: 15px;
  font-weight: 500;
  color: #64748b;
}

.auth-tabs :deep(.el-tabs__item.is-active) {
  color: #111827;
}

.auth-tabs :deep(.el-tabs__active-bar) {
  height: 3px;
  border-radius: 2px;
  background: #6366f1;
}

.auth-tabs :deep(.el-form-item) {
  margin-bottom: 20px;
}

.auth-tabs :deep(.el-form-item__label) {
  padding-bottom: 6px;
  font-size: 13px;
  font-weight: 500;
  color: #475569;
}

.auth-tabs :deep(.el-input__wrapper) {
  border-radius: 11px;
  background: #f8fafc;
  box-shadow: 0 0 0 1px #e2e8f0 inset;
  padding: 2px 14px;
}

.auth-tabs :deep(.el-input__wrapper.is-focus) {
  background: #fff;
  box-shadow: 0 0 0 1px #6366f1 inset, 0 0 0 3px rgba(99, 102, 241, 0.12);
}

.submit-btn {
  width: 100%;
  height: 46px;
  margin-top: 6px;
  border-radius: 11px;
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0.04em;
}

.form-tip {
  margin: 22px 0 0;
  text-align: center;
  font-size: 11.5px;
  color: #94a3b8;
}

@media (max-width: 900px) {
  .brand-side {
    display: none;
  }

  .form-side {
    width: 100%;
    padding: 32px 24px;
  }

  .form-head {
    text-align: center;
  }

  .form-card {
    max-width: 420px;
    padding: 28px 22px;
  }
}
</style>
