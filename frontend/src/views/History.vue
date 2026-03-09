<template>
  <div class="history">
    <el-card>
      <template #header>
        <div class="header-actions">
           <span>历史记录查询</span>
           <el-space>
             <el-select v-model="selectedFriendId" placeholder="查看谁的记录" clearable @change="fetchRecords">
                <el-option label="我自己" :value="null" />
                <el-option v-for="friend in friends" :key="friend.id" :label="friend.username" :value="friend.id" />
             </el-select>
             <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" @change="filterRecords" />
           </el-space>
        </div>
      </template>
      
      <el-table :data="filteredRecords" style="width: 100%" :row-class-name="tableRowClassName">
        <el-table-column prop="date" label="日期" sortable width="120" />
        <el-table-column label="用户" width="100">
             <template #default="scope">
                <el-tag :type="isMyRecord(scope.row) ? '' : 'success'">
                    {{ isMyRecord(scope.row) ? '我' : getFriendName(scope.row.user_id) }}
                </el-tag>
             </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="100">
           <template #default="scope">
              {{ scope.row.type === 'jogging' ? '慢跑' : scope.row.type === 'interval' ? '间歇跑' : '素质训练' }}
           </template>
        </el-table-column>
        <el-table-column label="详情">
           <template #default="scope">
                <div v-if="scope.row.type === 'jogging'">
                  {{ scope.row.details.distance }}km, {{ scope.row.details.pace }}, {{ scope.row.details.heart_rate }}bpm
                </div>
                <div v-if="scope.row.type === 'interval'">
                  <span v-for="(set, idx) in scope.row.details.sets" :key="idx">
                    {{ set.distance }}m x {{ set.count }}组; 
                  </span>
                </div>
                <div v-if="scope.row.type === 'quality'">
                  {{ scope.row.details.content }}
                </div>
           </template>
        </el-table-column>
        <el-table-column prop="details.note" label="备注" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../api'

const friends = ref([])
const selectedFriendId = ref(null)
const records = ref([])
const dateRange = ref(null)
const currentUser = ref(null)

const filteredRecords = computed(() => {
    if (!dateRange.value) return records.value
    const [start, end] = dateRange.value
    return records.value.filter(r => r.date >= start && r.date <= end)
})

const fetchCurrentUser = async () => {
    try {
        const res = await api.get('/users/me')
        currentUser.value = res.data
    } catch (e) {
        console.error(e)
    }
}

const fetchFriends = async () => {
  const res = await api.get('/friends/')
  friends.value = res.data
  // 如果有好友，且当前没有选中好友，默认选中第一个好友
  if (friends.value.length > 0 && !selectedFriendId.value) {
      selectedFriendId.value = friends.value[0].id
  }
}

const fetchRecords = async () => {
  const params = { limit: 1000 } // 获取更多记录以便筛选
  if (selectedFriendId.value) {
    // 使用 friend_id 参数来获取混合记录
    params.friend_id = selectedFriendId.value
  }
  const res = await api.get('/records/', { params })
  records.value = res.data
}

const isMyRecord = (record) => {
    return currentUser.value && record.user_id === currentUser.value.id
}

const getFriendName = (userId) => {
    const friend = friends.value.find(f => f.id === userId)
    return friend ? friend.username : '好友'
}

const tableRowClassName = ({ row }) => {
  if (!isMyRecord(row)) {
    return 'friend-row'
  }
  return ''
}

onMounted(async () => {
  await fetchCurrentUser()
  await fetchFriends()
  fetchRecords()
})
</script>

<style scoped>
.history {
    padding: 20px;
}
.header-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
:deep(.el-table .friend-row) {
  background-color: #f0f9eb;
}
</style>
