<template>
  <div class="study-page">
    <el-row :gutter="20">
      <el-col :xs="24" :md="12">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>我的学习记录</span>
              <el-date-picker 
                v-model="currentDate" 
                type="date" 
                value-format="YYYY-MM-DD" 
                :clearable="false"
                @change="fetchData" 
                style="width: 140px;"
              />
            </div>
          </template>
          
          <el-form label-position="top">
            <div class="section-title">今日待办 (To-Do List)</div>
            <div v-for="(todo, index) in myRecord.todos" :key="index" class="todo-item">
              <el-checkbox v-model="todo.completed" />
              <el-input 
                v-model="todo.text" 
                placeholder="输入待办事项" 
                class="todo-input"
              />
              <el-button type="danger" icon="Delete" circle size="small" @click="removeTodo(index)" />
            </div>
            <el-button type="primary" plain size="small" @click="addTodo" style="margin-top: 10px; width: 100%;">+ 添加待办</el-button>

            <div class="section-title" style="margin-top: 20px;">每日复盘</div>
            <el-input 
              v-model="myRecord.review" 
              type="textarea" 
              :rows="6" 
              placeholder="总结今天的学习情况，记录收获与不足..." 
            />
            
            <div style="margin-top: 20px; text-align: right;">
              <el-button type="primary" @click="saveRecord" :loading="saving">保存记录</el-button>
            </div>
          </el-form>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12" class="friend-col">
        <el-card class="box-card friend-card" v-if="friendId">
          <template #header>
            <div class="card-header">
              <span>搭子的学习记录 ({{ friendName }})</span>
            </div>
          </template>
          
          <div v-if="friendRecord">
            <div class="section-title">Ta 的待办</div>
            <div v-if="friendRecord.todos && friendRecord.todos.length > 0">
              <div v-for="(todo, index) in friendRecord.todos" :key="index" class="todo-item-readonly">
                <el-checkbox :model-value="todo.completed" disabled />
                <span :class="{ 'completed-text': todo.completed }">{{ todo.text }}</span>
              </div>
            </div>
            <el-empty v-else description="暂无待办" :image-size="60" />

            <div class="section-title" style="margin-top: 20px;">Ta 的复盘</div>
            <div class="review-content" v-if="friendRecord.review">
              {{ friendRecord.review }}
            </div>
            <el-empty v-else description="暂无复盘" :image-size="60" />
          </div>
          <el-empty v-else description="搭子今日未打卡" />
        </el-card>

        <el-card class="box-card" v-else>
          <el-empty description="未设置搭子">
             <template #extra>
               <router-link to="/friends">
                 <el-button type="primary">去寻找搭子</el-button>
               </router-link>
             </template>
          </el-empty>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getStudyRecords, saveStudyRecord } from '../api'
import { ElMessage } from 'element-plus'

const currentDate = ref(new Date().toISOString().split('T')[0])
const myRecord = reactive({
  todos: [],
  review: ''
})
const friendRecord = ref(null)
const friendId = ref(localStorage.getItem('compareFriendId'))
const friendName = ref(localStorage.getItem('compareFriendName') || '好友')
const saving = ref(false)

const addTodo = () => {
  myRecord.todos.push({ text: '', completed: false })
}

const removeTodo = (index) => {
  myRecord.todos.splice(index, 1)
}

const fetchData = async () => {
  // Fetch My Record
  try {
      // 获取最近记录，并在前端筛选日期
      const res = await getStudyRecords({ limit: 30 }) 
      const todayRecord = res.data.find(r => r.date === currentDate.value)
      if (todayRecord) {
          // Deep copy todos to avoid reactivity issues if needed, but here simple assignment is ok
          // Ensure todos is an array
          myRecord.todos = todayRecord.todos ? JSON.parse(JSON.stringify(todayRecord.todos)) : []
          myRecord.review = todayRecord.review || ''
      } else {
          myRecord.todos = []
          myRecord.review = ''
      }
  } catch (e) {
      console.error(e)
      ElMessage.error('获取我的记录失败')
  }

  // Fetch Friend Record
  if (friendId.value) {
      try {
           const res = await getStudyRecords({ friend_id: friendId.value, limit: 30 })
           // res.data contains mixed records (mine and theirs). Filter for theirs + date.
           const targetRecord = res.data.find(r => String(r.user_id) === String(friendId.value) && r.date === currentDate.value)
           friendRecord.value = targetRecord || null
      } catch (e) {
          console.error(e)
          // Silent fail for friend record
      }
  }
}

const saveRecord = async () => {
  if (saving.value) return
  saving.value = true
  try {
      await saveStudyRecord({
          date: currentDate.value,
          todos: myRecord.todos,
          review: myRecord.review
      })
      ElMessage.success('保存成功')
      // No need to fetch again, local state is latest
  } catch (e) {
      ElMessage.error('保存失败')
  } finally {
      saving.value = false
  }
}

onMounted(() => {
    fetchData()
})
</script>

<style scoped>
.study-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.section-title { font-weight: bold; margin-bottom: 10px; color: #606266; }
.todo-item { display: flex; align-items: center; margin-bottom: 10px; }
.todo-input { margin-left: 10px; flex-grow: 1; margin-right: 10px; }
.todo-item-readonly { display: flex; align-items: center; margin-bottom: 8px; }
.completed-text { text-decoration: line-through; color: #909399; }
.review-content { white-space: pre-wrap; line-height: 1.5; color: #303133; background: #f9f9f9; padding: 10px; border-radius: 4px; }
.friend-col { margin-top: 20px; }
@media (min-width: 992px) {
    .friend-col { margin-top: 0; }
}
.friend-card { background-color: #fdfdfd; }
</style>