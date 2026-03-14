<template>
  <div class="history">
    <el-card>
      <template #header>
        <div class="header-actions">
           <div class="left-actions">
             <span class="title">历史记录</span>
             <el-radio-group v-model="viewType" size="small" @change="handleViewTypeChange" style="margin-left: 15px;">
                <el-radio-button label="training">训练</el-radio-button>
                <el-radio-button label="study">学习</el-radio-button>
             </el-radio-group>
           </div>
           
           <el-space wrap class="filters">
             <el-select v-model="selectedFriendId" placeholder="查看谁的记录" clearable @change="refreshData" style="width: 150px">
                <el-option label="我自己" :value="null" />
                <el-option v-for="friend in friends" :key="friend.id" :label="friend.username" :value="friend.id" />
             </el-select>
             <el-date-picker 
                v-model="dateRange" 
                type="daterange" 
                range-separator="至" 
                start-placeholder="开始" 
                end-placeholder="结束" 
                value-format="YYYY-MM-DD" 
                style="width: 240px"
             />
           </el-space>
        </div>
      </template>
      
      <!-- Training Table -->
      <el-table v-if="viewType === 'training'" :data="filteredRecords" style="width: 100%" :row-class-name="tableRowClassName">
        <el-table-column prop="date" label="日期" sortable width="110" fixed="left" />
        <el-table-column label="用户" width="80">
             <template #default="scope">
                <el-tag :type="isMyRecord(scope.row) ? '' : 'success'" size="small">
                    {{ isMyRecord(scope.row) ? '我' : getFriendName(scope.row.user_id) }}
                </el-tag>
             </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="80">
           <template #default="scope">
              {{ scope.row.type === 'jogging' ? '慢跑' : scope.row.type === 'interval' ? '间歇' : '素质' }}
           </template>
        </el-table-column>
        <el-table-column label="详情" min-width="200">
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

      <!-- Study Table -->
      <el-table v-else :data="filteredRecords" style="width: 100%" :row-class-name="tableRowClassName">
        <el-table-column prop="date" label="日期" sortable width="110" fixed="left" />
        <el-table-column label="用户" width="80">
             <template #default="scope">
                <el-tag :type="isMyRecord(scope.row) ? '' : 'success'" size="small">
                    {{ isMyRecord(scope.row) ? '我' : getFriendName(scope.row.user_id) }}
                </el-tag>
             </template>
        </el-table-column>
        <el-table-column label="待办完成度" width="120">
           <template #default="scope">
              <el-progress 
                :percentage="calculateProgress(scope.row.todos)" 
                :status="calculateProgress(scope.row.todos) === 100 ? 'success' : ''"
              />
           </template>
        </el-table-column>
        <el-table-column label="复盘摘要" min-width="200" show-overflow-tooltip>
            <template #default="scope">
                {{ scope.row.review || '无复盘' }}
            </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api, { getStudyRecords } from '../api'

const friends = ref([])
const selectedFriendId = ref(null)
const records = ref([])
const dateRange = ref(null)
const currentUser = ref(null)
const viewType = ref('training')

const filteredRecords = computed(() => {
    let data = records.value
    if (dateRange.value) {
        const [start, end] = dateRange.value
        data = data.filter(r => r.date >= start && r.date <= end)
    }
    return data
})

const handleViewTypeChange = () => {
    refreshData()
}

const refreshData = () => {
    if (viewType.value === 'training') {
        fetchRecords()
    } else {
        fetchStudyHistory()
    }
}

const calculateProgress = (todos) => {
    if (!todos || todos.length === 0) return 0
    const completed = todos.filter(t => t.completed).length
    return Math.round((completed / todos.length) * 100)
}

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
  if (friends.value.length > 0 && !selectedFriendId.value) {
      selectedFriendId.value = friends.value[0].id
  }
}

const fetchRecords = async () => {
  const params = { limit: 1000 } 
  if (selectedFriendId.value) {
    params.friend_id = selectedFriendId.value
  }
  const res = await api.get('/records/', { params })
  records.value = res.data
}

const fetchStudyHistory = async () => {
  const params = { limit: 1000 }
  if (selectedFriendId.value) {
    params.friend_id = selectedFriendId.value
  }
  const res = await getStudyRecords(params)
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
  refreshData()
})
</script>

<style scoped>
.history { padding: 20px; }
.header-actions { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
.left-actions { display: flex; align-items: center; }
.title { font-weight: bold; font-size: 1.1em; }
@media (max-width: 600px) {
    .history { padding: 10px; }
    .header-actions { flex-direction: column; align-items: flex-start; }
    .filters { width: 100%; }
    .filters :deep(.el-date-editor) { width: 100% !important; }
    .left-actions { width: 100%; justify-content: space-between; margin-bottom: 10px; }
}
:deep(.el-table .friend-row) { background-color: #f0f9eb; }
</style>
