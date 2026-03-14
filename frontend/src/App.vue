<template>
  <el-container class="layout-container">
    <el-header v-if="isLoggedIn">
      <el-menu mode="horizontal" router :default-active="$route.path">
        <el-menu-item index="/">训练记录</el-menu-item>
        <el-menu-item index="/study">学习记录</el-menu-item>
        <el-menu-item index="/friends">好友</el-menu-item>
        <el-menu-item index="/history">历史记录</el-menu-item>
        <div class="flex-grow" />
        <el-menu-item @click="logout">退出</el-menu-item>
      </el-menu>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isLoggedIn = computed(() => !!localStorage.getItem('token'));

const logout = () => {
  localStorage.removeItem('token');
  router.push('/login');
  // Force reload to update isLoggedIn state properly if not using a store
  window.location.reload(); 
};
</script>

<style>
.layout-container {
  height: 100vh;
}
.flex-grow {
  flex-grow: 1;
}
body {
  margin: 0;
}
@media (max-width: 600px) {
  .el-menu-item {
    padding: 0 10px !important;
  }
}
</style>
