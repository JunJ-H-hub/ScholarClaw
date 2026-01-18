<template>
  <div class="knowledge-base-container">
    <div class="page-header">
      <h1>RAG知识库管理</h1>
      <div class="header-actions">
        <button class="btn-primary" @click="showCreateModal = true">
          + 创建知识库
        </button>
        <button class="btn-secondary" @click="goBack">
          返回主页
        </button>
      </div>
    </div>
    
    <div class="content-layout">
      <div class="main-content">
        <div class="section-header">
          <h2>知识库列表</h2>
          <div class="selected-info" v-if="selectedDatabase">
            <span class="selected-label">当前选中:</span>
            <span class="selected-name">{{ selectedDatabase.name }}</span>
          </div>
        </div>
        
        <div class="loading-state" v-if="isLoading">
          <div class="spinner"></div>
          <p>加载知识库列表...</p>
        </div>
        
        <div class="empty-state" v-else-if="databases.length === 0">
          <div class="empty-icon">📚</div>
          <p>暂无知识库</p>
          <button class="btn-create" @click="showCreateModal = true">创建第一个知识库</button>
        </div>
        
        <div class="databases-grid" v-else>
          <DatabaseCard
            v-for="database in databases"
            :key="database.id"
            :database="database"
            :is-selected="selectedDatabaseId === database.id"
            @select="handleSelectDatabase"
            @delete="handleDeleteDatabase"
          />
        </div>
      </div>
      
      <div class="side-panel" v-if="selectedDatabase">
        <div class="panel-section">
          <h3>文件上传</h3>
          <FileUpload
            :selected-database-id="selectedDatabaseId"
            @upload-complete="handleUploadComplete"
            @upload-error="handleUploadError"
          />
        </div>
        
        <div class="panel-section">
          <h3>查询测试</h3>
          <QueryTest
            :selected-database-id="selectedDatabaseId"
            ref="queryTestRef"
          />
        </div>
      </div>
    </div>
    
    <CreateDatabaseModal
      v-model:visible="showCreateModal"
      @submit="handleCreateDatabase"
    />
    
    <div class="toast" v-if="toast.show" :class="toast.type">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { knowledgeApi } from '../api/knowledge'
import DatabaseCard from '../components/DatabaseCard.vue'
import CreateDatabaseModal from '../components/CreateDatabaseModal.vue'
import FileUpload from '../components/FileUpload.vue'
import QueryTest from '../components/QueryTest.vue'

const router = useRouter()

const databases = ref([])
const selectedDatabaseId = ref('')
const selectedDatabase = ref(null)
const isLoading = ref(false)
const showCreateModal = ref(false)
const queryTestRef = ref(null)

const toast = ref({
  show: false,
  message: '',
  type: 'success'
})

onMounted(() => {
  loadDatabases()
})

const loadDatabases = async () => {
  isLoading.value = true
  try {
    const response = await knowledgeApi.getDatabases()
    databases.value = response.data.databases || []
  } catch (error) {
    console.error('加载知识库列表失败:', error)
    showToast('加载知识库列表失败', 'error')
  } finally {
    isLoading.value = false
  }
}

const handleSelectDatabase = async (database) => {
  selectedDatabaseId.value = database.id
  selectedDatabase.value = database
  
  try {
    await knowledgeApi.selectDatabase(database.id)
    showToast(`已选择知识库: ${database.name}`, 'success')
    
    if (queryTestRef.value) {
      queryTestRef.value.clearResults()
    }
  } catch (error) {
    console.error('选择知识库失败:', error)
    showToast('选择知识库失败', 'error')
  }
}

const handleDeleteDatabase = async (database) => {
  if (!confirm(`确定要删除知识库"${database.name}"吗？此操作不可恢复。`)) {
    return
  }
  
  try {
    await knowledgeApi.deleteDatabase(database.id)
    
    if (selectedDatabaseId.value === database.id) {
      selectedDatabaseId.value = ''
      selectedDatabase.value = null
    }
    
    await loadDatabases()
    showToast('知识库删除成功', 'success')
  } catch (error) {
    console.error('删除知识库失败:', error)
    showToast('删除知识库失败', 'error')
  }
}

const handleCreateDatabase = async (data) => {
  try {
    await knowledgeApi.createDatabase(data)
    await loadDatabases()
    showToast('知识库创建成功', 'success')
  } catch (error) {
    console.error('创建知识库失败:', error)
    showToast('创建知识库失败', 'error')
    throw error
  }
}

const handleUploadComplete = (file) => {
  showToast(`文件 "${file.name}" 上传成功`, 'success')
}

const handleUploadError = (file) => {
  showToast(`文件 "${file.name}" 上传失败: ${file.error}`, 'error')
}

const showToast = (message, type = 'success') => {
  toast.value = {
    show: true,
    message,
    type
  }
  
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

const goBack = () => {
  router.push('/')
}
</script>

<style scoped>
.knowledge-base-container {
  max-width: 1400px;
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
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-primary,
.btn-secondary,
.btn-create {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
}

.btn-secondary {
  background: #f8f9fa;
  color: #6c757d;
  border: 1px solid #ced4da;
}

.btn-secondary:hover {
  background: #e9ecef;
  color: #495057;
}

.btn-create {
  background: #3498db;
  color: white;
}

.btn-create:hover {
  background: #2980b9;
}

.content-layout {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 24px;
}

.main-content {
  min-width: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
}

.selected-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.selected-label {
  color: #6c757d;
}

.selected-name {
  color: #3498db;
  font-weight: 500;
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

.databases-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.side-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.panel-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 24px;
  border-radius: 6px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  z-index: 2000;
  animation: slideInRight 0.3s ease;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.toast.success {
  background: #28a745;
}

.toast.error {
  background: #dc3545;
}

@media (max-width: 1024px) {
  .content-layout {
    grid-template-columns: 1fr;
  }
  
  .side-panel {
    order: -1;
  }
}
</style>
