<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <span>登录</span>
        </div>
      </template>
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onSubmit">登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const form = reactive({
  username: '',
  password: '',
})

const onSubmit = async () => {
  try {
    const formData = new FormData()
    formData.append('username', form.username)
    formData.append('password', form.password)
    
    const response = await api.post('/token', formData)
    localStorage.setItem('token', response.data.access_token)
    ElMessage.success('登录成功')
    router.push('/')
    // Force reload to update App.vue state
    setTimeout(() => window.location.reload(), 100)
  } catch (error) {
    ElMessage.error('登录失败: ' + (error.response?.data?.detail || error.message))
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}
.login-card {
  width: 100%;
  max-width: 400px;
  margin: 0 10px;
}
</style>
