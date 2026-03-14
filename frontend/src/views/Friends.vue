<template>
  <div class="friends-page">
    <el-card>
      <template #header>
        <div class="header">
          <span>好友列表</span>
          <div class="add-friend">
            <el-popover placement="bottom" :width="300" trigger="click">
              <template #reference>
                <el-button type="primary">添加好友</el-button>
              </template>
              <div style="display: flex; gap: 10px;">
                <el-input v-model="newFriendUsername" placeholder="输入用户名" />
                <el-button type="primary" @click="addFriend">添加</el-button>
              </div>
            </el-popover>
          </div>
        </div>
      </template>
      
      <el-table :data="friends" style="width: 100%" stripe>
        <el-table-column prop="username" label="用户名" />
        <el-table-column label="状态" width="180">
          <template #default="scope">
            <el-tag v-if="isComparing(scope.row.id)" type="success">当前搭子</el-tag>
            <el-tag v-else type="info">未设定</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="right">
          <template #default="scope">
            <el-button 
              :type="isComparing(scope.row.id) ? 'warning' : 'primary'" 
              size="small" 
              plain
              @click="toggleCompare(scope.row)"
            >
              {{ isComparing(scope.row.id) ? '取消搭子' : '设为搭子' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="tips">
        <el-alert
          title="提示：设置搭子后，将在“训练记录”和“学习记录”页看到 Ta 的动态，互相监督，共同进步！"
          type="info"
          show-icon
          :closable="false"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { ElMessage } from 'element-plus'

const friends = ref([])
const newFriendUsername = ref('')
const currentCompareId = ref(localStorage.getItem('compareFriendId'))

const fetchFriends = async () => {
  try {
    const res = await api.get('/friends/')
    friends.value = res.data
  } catch (e) {
    ElMessage.error('获取好友列表失败')
  }
}

const addFriend = async () => {
    if (!newFriendUsername.value) return
    try {
        await api.post('/friends/', { friend_username: newFriendUsername.value })
        ElMessage.success('添加成功')
        newFriendUsername.value = ''
        fetchFriends()
    } catch (e) {
        ElMessage.error('添加失败：用户不存在或已添加')
    }
}

const isComparing = (id) => {
    return String(currentCompareId.value) === String(id)
}

const toggleCompare = (friend) => {
    if (isComparing(friend.id)) {
        localStorage.removeItem('compareFriendId')
        localStorage.removeItem('compareFriendName')
        currentCompareId.value = null
        ElMessage.info('已取消搭子')
    } else {
        localStorage.setItem('compareFriendId', friend.id)
        localStorage.setItem('compareFriendName', friend.username)
        currentCompareId.value = friend.id
        ElMessage.success(`已设为与 ${friend.username} 成为搭子`)
    }
}

onMounted(() => {
    fetchFriends()
})
</script>

<style scoped>
.friends-page { padding: 20px; max-width: 800px; margin: 0 auto; }
.header { display: flex; justify-content: space-between; align-items: center; }
.tips { margin-top: 20px; }
</style>