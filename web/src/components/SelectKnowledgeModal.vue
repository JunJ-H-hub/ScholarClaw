<template>
  <div class="modal-overlay" v-if="isVisible" @click="handleOverlayClick">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h2>选择知识库</h2>
        <button class="btn-close" @click="close">✕</button>
      </div>
      
      <div class="modal-body">
        <div class="loading-state" v-if="isLoading">
          <div class="spinner"></div>
          <p>加载知识库列表...</p>
        </div>
        
        <div class="empty-state" v-else-if="databases.length === 0">
          <div class="empty-icon">📚</div>
          <p>暂无可用知识库</p>
          <button class="btn-create" @click="handleCreateDatabase">创建知识库</button>
        </div>
        
        <div class="database-list" v-else>
          <div 
            v-for="database in databases"
            :key="database.id"
            class="database-item"
            :class="{ 'selected': isSelected(database.id) }"
            @click="handleSelect(database)"
          >
            <div class="database-info">
              <h4 class="database-name">{{ database.name }}</h4>
              <p class="database-description">{{ database.description || '暂无描述' }}</p>
            </div>
            <div class="database-check">
              <div class="check-icon" v-if="isSelected(database.id)">✓</div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn-cancel" @click="close">取消</button>
          <button 
            class="btn-confirm" 
            @click="handleConfirm"
            :disabled="!selectedDatabaseId"
          >
            确认选择
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { knowledgeApi } from '../api/knowledge'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  currentDatabaseId: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:visible', 'select', 'create-database'])

const isVisible = ref(false)
const isLoading = ref(false)
const databases = ref([])
const selectedDatabaseId = ref('')

watch(() => props.visible, (newVal) => {
  isVisible.value = newVal
  if (newVal) {
    selectedDatabaseId.value = props.currentDatabaseId
    loadDatabases()
  }
})

onMounted(() => {
  selectedDatabaseId.value = props.currentDatabaseId
})

const loadDatabases = async () => {
  isLoading.value = true
  try {
    const response = await knowledgeApi.getDatabases()
    databases.value = response.data.databases || []
  } catch (error) {
    console.error('加载知识库列表失败:', error)
    databases.value = []
  } finally {
    isLoading.value = false
  }
}

const isSelected = (dbId) => {
  return selectedDatabaseId.value === dbId
}

const handleSelect = (database) => {
  selectedDatabaseId.value = database.id
}

const handleConfirm = () => {
  if (selectedDatabaseId.value) {
    const database = databases.value.find(db => db.id === selectedDatabaseId.value)
    emit('select', database)
    close()
  }
}

const handleCreateDatabase = () => {
  emit('create-database')
}

const close = () => {
  isVisible.value = false
  emit('update:visible', false)
}

const handleOverlayClick = () => {
  close()
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-container {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
}

.btn-close {
  width: 32px;
  height: 32px;
  border: none;
  background: #f8f9fa;
  color: #6c757d;
  border-radius: 6px;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-close:hover {
  background: #e9ecef;
  color: #495057;
}

.modal-body {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
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
  padding: 60px 20px;
  color: #6c757d;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-state p {
  margin: 0 0 20px 0;
  font-size: 14px;
}

.btn-create {
  padding: 10px 24px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-create:hover {
  background: #2980b9;
}

.database-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.database-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.database-item:hover {
  border-color: #3498db;
  background: #f0f8ff;
}

.database-item.selected {
  border-color: #3498db;
  background: #e3f2fd;
}

.database-info {
  flex: 1;
}

.database-name {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.database-description {
  margin: 0;
  font-size: 13px;
  color: #6c757d;
}

.database-check {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.check-icon {
  width: 20px;
  height: 20px;
  background: #3498db;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
}

.btn-cancel,
.btn-confirm {
  padding: 10px 24px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: #f8f9fa;
  color: #6c757d;
}

.btn-cancel:hover {
  background: #e9ecef;
  color: #495057;
}

.btn-confirm {
  background: #3498db;
  color: white;
}

.btn-confirm:hover:not(:disabled) {
  background: #2980b9;
}

.btn-confirm:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}
</style>
