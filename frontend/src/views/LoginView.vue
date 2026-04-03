<template>
  <div class="login-page">
    <div class="login-card">
      <div class="brand">
        <h1>Mango Talk</h1>
        <p>标准聊天室 · 登录入口</p>
      </div>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-item">
          <label for="identifier">用户名或手机号</label>
          <input
            id="identifier"
            v-model.trim="form.identifier"
            type="text"
            placeholder="请输入用户名或手机号"
            autocomplete="username"
          />
        </div>

        <div class="form-item">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            autocomplete="current-password"
          />
        </div>

        <p v-if="errorMessage" class="error-text">
          {{ errorMessage }}
        </p>

        <button class="submit-btn" type="submit" :disabled="authStore.loading">
          {{ authStore.loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <div class="footer-tip">
        <p>当前阶段先打通登录主链路</p>
        <p>下一步再接 /users/me 与房间列表</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  identifier: '',
  password: '',
})

const errorMessage = ref('')

async function handleLogin() {
  errorMessage.value = ''

  if (!form.identifier) {
    errorMessage.value = '请输入用户名或手机号'
    return
  }

  if (!form.password) {
    errorMessage.value = '请输入密码'
    return
  }

  try {
    await authStore.login(form.identifier, form.password)
    router.push('/chat')
  } catch (error) {
    errorMessage.value =
      error?.response?.data?.detail || '登录失败，请检查后端服务或输入信息'
  }
}
</script>

<style scoped lang="scss">
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(circle at top left, rgba(255, 181, 71, 0.28), transparent 30%),
    linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
  padding: 24px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 36px 32px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 18px 50px rgba(15, 23, 42, 0.12);
  backdrop-filter: blur(6px);
}

.brand {
  margin-bottom: 28px;
  text-align: center;

  h1 {
    margin: 0 0 10px;
    font-size: 34px;
    font-weight: 700;
    color: #f97316;
    letter-spacing: 0.5px;
  }

  p {
    margin: 0;
    font-size: 14px;
    color: #64748b;
  }
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;

  label {
    font-size: 14px;
    color: #334155;
    font-weight: 600;
  }

  input {
    height: 46px;
    padding: 0 14px;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    outline: none;
    font-size: 15px;
    color: #0f172a;
    background: #fff;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;

    &:focus {
      border-color: #fb923c;
      box-shadow: 0 0 0 4px rgba(251, 146, 60, 0.14);
    }
  }
}

.error-text {
  margin: -4px 0 0;
  font-size: 14px;
  color: #dc2626;
}

.submit-btn {
  height: 46px;
  border: none;
  border-radius: 14px;
  background: linear-gradient(135deg, #fb923c 0%, #f97316 100%);
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;

  &:hover:enabled {
    transform: translateY(-1px);
    box-shadow: 0 10px 20px rgba(249, 115, 22, 0.22);
  }

  &:disabled {
    opacity: 0.72;
    cursor: not-allowed;
  }
}

.footer-tip {
  margin-top: 22px;
  text-align: center;

  p {
    margin: 4px 0;
    font-size: 13px;
    color: #94a3b8;
  }
}
</style>
