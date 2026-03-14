<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <!-- 左侧：添加记录 -->
      <el-col :xs="24" :md="12" class="mb-20">
        <el-card>
          <template #header>添加训练记录</template>
          <el-form :model="form" label-width="100px" :label-position="labelPosition">
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
                <el-space wrap>
                  <el-form-item label="单组距离(m)" label-width="90px">
                    <el-input-number v-model="set.distance" :step="100" />
                  </el-form-item>
                  <el-form-item label="组数" label-width="50px">
                    <el-input-number v-model="set.count" :step="1" />
                  </el-form-item>
                  <el-button type="danger" circle icon="Delete" @click="removeSet(index)" v-if="form.details.sets.length > 1" />
                </el-space>
              </div>
              <el-button type="primary" plain @click="addSet" class="add-set-btn">添加训练组</el-button>
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
      <el-col :xs="24" :md="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>近期记录 (近3天)</span>
              <div v-if="friendId">
                 <el-tag type="success">当前搭子: {{ friendName }}</el-tag>
                 <router-link to="/friends" style="margin-left: 5px; font-size: 0.8em;">更改</router-link>
              </div>
              <router-link to="/friends" v-else><el-button size="small">去寻找搭子</el-button></router-link>
            </div>
          </template>
          
          <el-timeline v-if="recentRecords.length > 0">
            <el-timeline-item v-for="record in recentRecords" :key="record.id" :timestamp="record.date" placement="top" :type="isMyRecord(record) ? 'primary' : 'success'">
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
          <el-empty v-else description="近3天无记录" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, watch, computed } from 'vue'
import api from '../api'
import { ElMessage } from 'element-plus'

const records = ref([])
const currentUser = ref(null)
const labelPosition = ref('right')
const friendId = ref(localStorage.getItem('compareFriendId'))
const friendName = ref(localStorage.getItem('compareFriendName') || '好友')

const handleResize = () => {
  labelPosition.value = window.innerWidth < 768 ? 'top' : 'right'
}

const form = reactive({
  date: new Date().toISOString().split('T')[0],
  type: 'jogging',
  details: {
    distance: 5,
    pace: '',
    heart_rate: 150,
    note: '',
    sets: [{ distance: 400, count: 1 }],
    content: ''
  }
})

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

const fetchRecords = async () => {
  try {
    const params = {}
    if (friendId.value) {
      params.friend_id = friendId.value
    }
    const res = await api.get('/records/', { params })
    records.value = res.data
  } catch (e) {
    ElMessage.error('获取记录失败')
  }
}

const recentRecords = computed(() => {
    const threeDaysAgo = new Date();
    threeDaysAgo.setDate(threeDaysAgo.getDate() - 3);
    // Set to midnight to include the full 3rd day back
    threeDaysAgo.setHours(0,0,0,0);
    
    return records.value.filter(r => {
        const rDate = new Date(r.date);
        rDate.setHours(0,0,0,0); // Ensure time doesn't affect comparison if string parsing adds time
        return rDate >= threeDaysAgo;
    });
})

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
    // If it's the friend we are comparing with, return their name
    if (String(userId) === String(friendId.value)) {
        return friendName.value
    }
    return '好友'
}

onMounted(async () => {
  handleResize()
  window.addEventListener('resize', handleResize)
  await fetchCurrentUser()
  await fetchRecords()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.dashboard { padding: 20px; }
.mb-20 { margin-bottom: 20px; }
@media (min-width: 992px) { .mb-20 { margin-bottom: 0; } }
.interval-set { margin-bottom: 10px; }
.add-set-btn { margin-bottom: 20px; margin-left: 100px; }
@media (max-width: 768px) {
    .add-set-btn { margin-left: 0; width: 100%; }
    .dashboard { padding: 10px; }
}
.record-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.record-header h4 { margin: 0; }
.friend-record { background-color: #f0f9eb; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>