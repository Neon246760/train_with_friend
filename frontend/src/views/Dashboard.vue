<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <!-- 左侧：添加记录 -->
      <el-col :span="12">
        <el-card>
          <template #header>添加训练记录</template>
          <el-form :model="form" label-width="100px">
            <el-form-item label="日期">
              <el-date-picker v-model="form.date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" />
            </el-form-item>
            <el-form-item label="类型">
              <el-select v-model="form.type" placeholder="选择训练类型">
                <el-option label="慢跑" value="jogging" />
                <el-option label="间歇跑" value="interval" />
                <el-option label="素质训练" value="quality" />
              </el-select>
            </el-form-item>

            <!-- 慢跑表单 -->
            <template v-if="form.type === 'jogging'">
              <el-form-item label="距离(km)">
                <el-input-number v-model="form.details.distance" :precision="2" :step="0.1" />
              </el-form-item>
              <el-form-item label="配速">
                <el-input v-model="form.details.pace" placeholder="例如 5:30" />
              </el-form-item>
              <el-form-item label="心率">
                <el-input-number v-model="form.details.heart_rate" :step="1" />
              </el-form-item>
              <el-form-item label="备注">
                <el-input v-model="form.details.note" type="textarea" />
              </el-form-item>
            </template>

            <!-- 间歇跑表单 -->
            <template v-if="form.type === 'interval'">
              <div v-for="(set, index) in form.details.sets" :key="index" class="interval-set">
                <el-space>
                  <el-form-item label="单组距离(m)" label-width="90px">
                    <el-input-number v-model="set.distance" :step="100" />
                  </el-form-item>
                  <el-form-item label="组数" label-width="50px">
                    <el-input-number v-model="set.count" :step="1" />
                  </el-form-item>
                  <el-button type="danger" circle icon="Delete" @click="removeSet(index)" v-if="form.details.sets.length > 1" />
                </el-space>
              </div>
              <el-button type="primary" plain @click="addSet" style="margin-bottom: 20px; margin-left: 100px;">添加训练组</el-button>
              <el-form-item label="备注">
                <el-input v-model="form.details.note" type="textarea" />
              </el-form-item>
            </template>

            <!-- 素质训练表单 -->
            <template v-if="form.type === 'quality'">
              <el-form-item label="内容">
                <el-input v-model="form.details.content" type="textarea" rows="4" placeholder="描述你的训练内容" />
              </el-form-item>
            </template>

            <el-form-item>
              <el-button type="primary" @click="submitRecord">提交记录</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧：好友与记录 -->
      <el-col :span="12">
        <el-card style="margin-bottom: 20px;">
          <template #header>好友管理</template>
          <el-space>
            <el-select v-model="selectedFriendId" placeholder="选择好友查看记录" clearable @change="fetchRecords">
              <el-option v-for="friend in friends" :key="friend.id" :label="friend.username" :value="friend.id" />
            </el-select>
            <el-popover placement="bottom" :width="300" trigger="click">
              <template #reference>
                <el-button>添加好友</el-button>
              </template>
              <el-input v-model="newFriendUsername" placeholder="输入好友用户名">
                <template #append>
                  <el-button @click="addFriend">添加</el-button>
                </template>
              </el-input>
            </el-popover>
          </el-space>
          <div v-if="selectedFriendId" style="margin-top: 10px; color: #666; font-size: 0.9em;">
             当前显示：我和 {{ getFriendName(selectedFriendId) }} 的记录
          </div>
        </el-card>

        <el-card>
          <template #header>近期记录</template>
          <el-timeline>
            <el-timeline-item v-for="record in records" :key="record.id" :timestamp="record.date" placement="top" :type="isMyRecord(record) ? 'primary' : 'success'">
              <el-card :class="{ 'friend-record': !isMyRecord(record) }">
                <div class="record-header">
                    <h4>{{ record.type === 'jogging' ? '慢跑' : record.type === 'interval' ? '间歇跑' : '素质训练' }}</h4>
                    <el-tag size="small" :type="isMyRecord(record) ? '' : 'success'">
                        {{ isMyRecord(record) ? '我' : getFriendName(record.user_id) }}
                    </el-tag>
                </div>
                
                <div v-if="record.type === 'jogging'">
                  <p>距离: {{ record.details.distance }} km</p>
                  <p>配速: {{ record.details.pace }}</p>
                  <p>心率: {{ record.details.heart_rate }}</p>
                  <p v-if="record.details.note">备注: {{ record.details.note }}</p>
                </div>

                <div v-if="record.type === 'interval'">
                  <div v-for="(set, idx) in record.details.sets" :key="idx">
                    <p>{{ set.distance }}m x {{ set.count }}组</p>
                  </div>
                  <p v-if="record.details.note">备注: {{ record.details.note }}</p>
                </div>

                <div v-if="record.type === 'quality'">
                  <p>{{ record.details.content }}</p>
                </div>
                
                <div style="margin-top: 10px; text-align: right;" v-if="isMyRecord(record)">
                   <el-button type="danger" size="small" icon="Delete" circle @click="deleteRecord(record.id)" />
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import api from '../api'
import { ElMessage } from 'element-plus'

const friends = ref([])
const selectedFriendId = ref(null)
const newFriendUsername = ref('')
const records = ref([])
const currentUser = ref(null)

const form = reactive({
  date: new Date().toISOString().split('T')[0],
  type: 'jogging',
  details: {
    distance: 5,
    pace: '',
    heart_rate: 150,
    note: '',
    sets: [{ distance: 400, count: 1 }], // interval default
    content: '' // quality default
  }
})

// 监听类型变化，重置或调整 details 结构
watch(() => form.type, (newType) => {
  if (newType === 'jogging') {
    form.details = { distance: 5, pace: '', heart_rate: 150, note: '' }
  } else if (newType === 'interval') {
    form.details = { sets: [{ distance: 400, count: 1 }], note: '' }
  } else {
    form.details = { content: '' }
  }
})

const addSet = () => {
  form.details.sets.push({ distance: 400, count: 1 })
}

const removeSet = (index) => {
  form.details.sets.splice(index, 1)
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
  try {
    const res = await api.get('/friends/')
    friends.value = res.data
    // 如果有好友，且当前没有选中好友，默认选中第一个好友
    if (friends.value.length > 0 && !selectedFriendId.value) {
        selectedFriendId.value = friends.value[0].id
        // 重新获取记录以应用默认好友
        fetchRecords()
    }
  } catch (e) {
    ElMessage.error('获取好友列表失败')
  }
}

const addFriend = async () => {
  if (!newFriendUsername.value) return
  try {
    await api.post('/friends/', { friend_username: newFriendUsername.value })
    ElMessage.success('好友添加成功')
    newFriendUsername.value = ''
    fetchFriends()
  } catch (e) {
    ElMessage.error('添加失败：用户不存在或已添加')
  }
}

const fetchRecords = async () => {
  try {
    const params = {}
    if (selectedFriendId.value) {
      // 改用 friend_id 参数，以触发“我和好友混合展示”的逻辑
      params.friend_id = selectedFriendId.value
    }
    const res = await api.get('/records/', { params })
    records.value = res.data
  } catch (e) {
    ElMessage.error('获取记录失败')
  }
}

const submitRecord = async () => {
  try {
    await api.post('/records/', form)
    ElMessage.success('记录添加成功')
    fetchRecords()
  } catch (e) {
    ElMessage.error('添加失败')
  }
}

const deleteRecord = async (id) => {
    try {
        await api.delete(`/records/${id}`)
        ElMessage.success('删除成功')
        fetchRecords()
    } catch (e) {
        ElMessage.error('删除失败')
    }
}

const isMyRecord = (record) => {
    return currentUser.value && record.user_id === currentUser.value.id
}

const getFriendName = (userId) => {
    const friend = friends.value.find(f => f.id === userId)
    return friend ? friend.username : '好友'
}

onMounted(async () => {
  await fetchCurrentUser()
  await fetchFriends()
  // fetchRecords 在 fetchFriends 内部如果选中了好友会自动调用，或者在这里调用一次初始状态（无好友）
  if (friends.value.length === 0) {
      fetchRecords()
  }
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}
.interval-set {
  margin-bottom: 10px;
}
.record-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}
.record-header h4 {
    margin: 0;
}
.friend-record {
    background-color: #f0f9eb; /* 浅绿色背景区分好友记录 */
}
</style>
