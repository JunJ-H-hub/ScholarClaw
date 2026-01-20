<template>
  <div class="file-upload-container">
    <div 
      class="upload-zone"
      :class="{ 
        'drag-over': isDragOver, 
        'disabled': !selectedDatabaseId 
      }"
      @dragover.prevent="handleDragOver"
      @dragleave.prevent="handleDragLeave"
      @drop.prevent="handleDrop"
      @click="triggerFileInput"
    >
      <div class="upload-icon">📁</div>
      <p class="upload-text">
        {{ selectedDatabaseId ? '拖拽文件到此处或点击上传' : '请先选择知识库' }}
      </p>
      <p class="upload-hint" v-if="selectedDatabaseId">
        支持的文件类型: {{ supportedTypes.join(', ') }}
      </p>
      <input 
        ref="fileInput"
        type="file" 
        multiple
        :accept="acceptTypes"
        @change="handleFileSelect"
        style="display: none"
      />
    </div>
    
    <div class="upload-progress" v-if="uploadQueue.length > 0">
      <h3>上传队列</h3>
      <div class="file-list">
        <div 
          v-for="(file, index) in uploadQueue" 
          :key="index"
          class="file-item"
        >
          <div class="file-info">
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">{{ formatFileSize(file.size) }}</span>
          </div>
          <div class="file-status">
            <span 
              class="status-badge"
              :class="file.status"
            >
              {{ getStatusText(file.status) }}
            </span>
            <span 
              v-if="file.status === 'uploading'"
              class="progress-text"
            >
              {{ file.progress }}%
            </span>
          </div>
        </div>
      </div>
      
      <div class="upload-actions">
        <button 
          class="btn-clear"
          @click="clearQueue"
          :disabled="isUploading"
        >
          清空队列
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { knowledgeApi } from '../api/knowledge'

const props = defineProps({
  selectedDatabaseId: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['upload-complete', 'upload-error'])

const fileInput = ref(null)
const isDragOver = ref(false)
const uploadQueue = ref([])
const isUploading = ref(false)
const supportedTypes = ref([])

const acceptTypes = computed(() => {
  return supportedTypes.value.map(type => `${type}`).join(',')
})

onMounted(async () => {
  await loadSupportedTypes()
})

const loadSupportedTypes = async () => {
  try {
    const response = await knowledgeApi.getSupportedTypes()
    supportedTypes.value = response.data.file_types || []
  } catch (error) {
    console.error('加载支持的文件类型失败:', error)
    supportedTypes.value = ['pdf', 'docx', 'txt', 'md']
  }
}

const handleDragOver = () => {
  if (!props.selectedDatabaseId) return
  isDragOver.value = true
}

const handleDragLeave = () => {
  isDragOver.value = false
}

const handleDrop = (event) => {
  if (!props.selectedDatabaseId) return
  isDragOver.value = false
  
  const files = Array.from(event.dataTransfer.files)
  addFilesToQueue(files)
}

const triggerFileInput = () => {
  if (!props.selectedDatabaseId) return
  fileInput.value.click()
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  addFilesToQueue(files)
  event.target.value = ''
}

const addFilesToQueue = (files) => {
  files.forEach(file => {
    uploadQueue.value.push({
      file,
      name: file.name,
      size: file.size,
      status: 'pending',
      progress: 0,
      error: null
    })
  })
  
  processQueue()
}

const processQueue = async () => {
  if (isUploading.value) return
  
  isUploading.value = true
  
  for (let i = 0; i < uploadQueue.value.length; i++) {
    const item = uploadQueue.value[i]
    
    if (item.status === 'pending' || item.status === 'failed') {
      await uploadFile(item)
    }
  }
  
  isUploading.value = false
}

const uploadFile = async (item) => {
  item.status = 'uploading'
  item.progress = 0
  
  try {
    const response = await knowledgeApi.uploadFile(item.file, props.selectedDatabaseId)
    
    item.status = 'success'
    item.progress = 100
    
    const filePath = response.data.file_path
    await knowledgeApi.addDocuments(props.selectedDatabaseId, [filePath], { content_type: 'file' })
    
    emit('upload-complete', item)
  } catch (error) {
    item.status = 'failed'
    item.error = error.response?.data?.detail || error.message || '上传失败'
    emit('upload-error', item)
  }
}

const clearQueue = () => {
  uploadQueue.value = []
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const getStatusText = (status) => {
  const statusMap = {
    pending: '等待中',
    uploading: '上传中',
    success: '成功',
    failed: '失败'
  }
  return statusMap[status] || status
}

defineExpose({
  clearQueue
})
</script>

<style scoped>
.file-upload-container {
  margin-top: 20px;
}

.upload-zone {
  border: 2px dashed #ced4da;
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #f8f9fa;
}

.upload-zone:hover:not(.disabled) {
  border-color: #3498db;
  background: #f0f8ff;
}

.upload-zone.drag-over {
  border-color: #3498db;
  background: #e3f2fd;
}

.upload-zone.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.upload-text {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #495057;
  font-weight: 500;
}

.upload-hint {
  margin: 0;
  font-size: 13px;
  color: #6c757d;
}

.upload-progress {
  margin-top: 20px;
}

.upload-progress h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.file-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  background: white;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e9ecef;
}

.file-item:last-child {
  border-bottom: none;
}

.file-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #2c3e50;
}

.file-size {
  font-size: 12px;
  color: #6c757d;
}

.file-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending {
  background: #f8f9fa;
  color: #6c757d;
}

.status-badge.uploading {
  background: #e3f2fd;
  color: #3498db;
}

.status-badge.success {
  background: #d4edda;
  color: #28a745;
}

.status-badge.failed {
  background: #f8d7da;
  color: #dc3545;
}

.progress-text {
  font-size: 12px;
  color: #3498db;
  font-weight: 500;
}

.upload-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}

.btn-clear {
  padding: 8px 16px;
  border: 1px solid #ced4da;
  background: white;
  color: #6c757d;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-clear:hover:not(:disabled) {
  background: #f8f9fa;
  border-color: #adb5bd;
}

.btn-clear:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
