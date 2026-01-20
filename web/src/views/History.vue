<template>
  <div class="history-container">
    <div class="page-header">
      <h1>历史报告 （此功能还在开发中，暂不可使用）</h1>
      <div class="header-actions">
        <button 
          class="btn-refresh"
          @click="loadHistory"
          :disabled="isLoading"
        >
          🔄 刷新
        </button>
      </div>
    </div>

    <div class="loading-state" v-if="isLoading">
      <div class="spinner"></div>
      <p>加载历史报告...</p>
    </div>

    <div class="empty-state" v-else-if="historyList.length === 0">
      <div class="empty-icon">📋</div>
      <p>暂无历史报告</p>
      <button class="btn-create" @click="goToCreate">创建第一个报告</button>
    </div>

    <div class="history-list" v-else>
      <div 
        v-for="item in historyList" 
        :key="item.id"
        class="history-card"
      >
        <div class="card-header">
          <div class="report-title">
            <span class="report-icon">📄</span>
            <span class="title-text">{{ item.title || '未命名报告' }}</span>
          </div>
          <div class="report-status" :class="item.status">
            {{ getStatusText(item.status) }}
          </div>
        </div>

        <div class="card-content">
          <div class="report-query">
            <span class="label">查询内容:</span>
            <span class="content">{{ item.query }}</span>
          </div>
          
          <div class="report-meta">
            <div class="meta-item">
              <span class="meta-icon">📅</span>
              <span class="meta-text">{{ formatDate(item.createdAt) }}</span>
            </div>
            <div class="meta-item" v-if="item.knowledgeBase">
              <span class="meta-icon">📚</span>
              <span class="meta-text">{{ item.knowledgeBase }}</span>
            </div>
          </div>
        </div>

        <div class="card-actions">
          <button 
            class="btn-view"
            @click="viewReport(item)"
          >
            👁️ 查看详情
          </button>
          <button 
            class="btn-delete"
            @click="deleteReport(item)"
          >
            🗑️ 删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const isLoading = ref(false)
const historyList = ref([])

const loadHistory = async () => {
  isLoading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    const saved = localStorage.getItem('reportHistory')
    historyList.value = saved ? JSON.parse(saved) : []
  } catch (error) {
    console.error('加载历史报告失败:', error)
    historyList.value = []
  } finally {
    isLoading.value = false
  }
}

const getStatusText = (status) => {
  const statusMap = {
    completed: '已完成',
    processing: '处理中',
    failed: '失败',
    pending: '待处理'
  }
  return statusMap[status] || '未知'
}

const formatDate = (dateString) => {
  if (!dateString) return '未知时间'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const viewReport = (item) => {
  router.push({
    path: '/',
    query: { reportId: item.id }
  })
}

const deleteReport = (item) => {
  if (!confirm(`确定要删除报告"${item.title || '未命名报告'}"吗？此操作不可恢复。`)) {
    return
  }
  
  try {
    historyList.value = historyList.value.filter(h => h.id !== item.id)
    localStorage.setItem('reportHistory', JSON.stringify(historyList.value))
  } catch (error) {
    console.error('删除报告失败:', error)
    alert('删除失败，请重试')
  }
}

const goToCreate = () => {
  router.push('/')
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.history-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e9ecef;
}

.page-header h1 {
  margin: 0;
  font-size: clamp(24px, 3vw, 32px);
  font-weight: 600;
  color: #2c3e50;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-refresh {
  padding: 10px 20px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-refresh:hover:not(:disabled) {
  background: #2980b9;
  transform: translateY(-1px);
}

.btn-refresh:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
  transform: none;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #6c757d;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p {
  margin: 0;
  font-size: 14px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  background: #f8f9fa;
  border-radius: 12px;
  color: #6c757d;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state p {
  margin: 0 0 20px 0;
  font-size: 16px;
}

.btn-create {
  background: #3498db;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-create:hover {
  background: #2980b9;
  transform: translateY(-1px);
}

.history-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.history-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: 1px solid #e9ecef;
}

.history-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e9ecef;
}

.report-title {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.report-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.title-text {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.report-status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.report-status.completed {
  background: #d4edda;
  color: #155724;
}

.report-status.processing {
  background: #cce5ff;
  color: #004085;
}

.report-status.failed {
  background: #f8d7da;
  color: #721c24;
}

.report-status.pending {
  background: #fff3cd;
  color: #856404;
}

.card-content {
  margin-bottom: 16px;
}

.report-query {
  margin-bottom: 12px;
}

.report-query .label {
  display: block;
  font-size: 12px;
  color: #6c757d;
  margin-bottom: 4px;
}

.report-query .content {
  display: block;
  font-size: 14px;
  color: #2c3e50;
  line-height: 1.5;
  word-break: break-word;
}

.report-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #6c757d;
}

.meta-icon {
  font-size: 14px;
}

.meta-text {
  color: #495057;
}

.card-actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #e9ecef;
}

.btn-view,
.btn-delete {
  flex: 1;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-view {
  background: #e3f2fd;
  color: #3498db;
}

.btn-view:hover {
  background: #3498db;
  color: white;
}

.btn-delete {
  background: #f8f9fa;
  color: #dc3545;
  border: 1px solid #e9ecef;
}

.btn-delete:hover {
  background: #dc3545;
  color: white;
  border-color: #dc3545;
}

@media (max-width: 768px) {
  .history-container {
    padding: 15px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .history-list {
    grid-template-columns: 1fr;
  }

  .card-actions {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .history-container {
    padding: 12px;
  }

  .page-header h1 {
    font-size: 24px;
  }

  .history-card {
    padding: 16px;
  }
}
</style>
