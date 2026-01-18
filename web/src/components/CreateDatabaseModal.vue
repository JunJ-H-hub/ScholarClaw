<template>
  <div class="modal-overlay" v-if="isVisible" @click="handleOverlayClick">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h2>创建知识库</h2>
        <button class="btn-close" @click="close">✕</button>
      </div>
      
      <div class="modal-body">
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label for="databaseName">知识库名称 *</label>
            <input 
              id="databaseName"
              v-model="formData.name"
              type="text"
              placeholder="请输入知识库名称"
              :class="{ 'error': errors.name }"
              @blur="validateName"
            />
            <span class="error-message" v-if="errors.name">{{ errors.name }}</span>
          </div>
          
          <div class="form-group">
            <label for="description">描述</label>
            <textarea 
              id="description"
              v-model="formData.description"
              placeholder="请输入知识库描述（可选）"
              rows="3"
            ></textarea>
          </div>
          
          <div class="form-actions">
            <button type="button" class="btn-cancel" @click="close">取消</button>
            <button type="submit" class="btn-submit" :disabled="isSubmitting">
              {{ isSubmitting ? '创建中...' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:visible', 'submit'])

const isVisible = ref(false)
const isSubmitting = ref(false)
const formData = reactive({
  name: '',
  description: ''
})
const errors = reactive({
  name: ''
})

watch(() => props.visible, (newVal) => {
  isVisible.value = newVal
  if (newVal) {
    resetForm()
  }
})

const resetForm = () => {
  formData.name = ''
  formData.description = ''
  errors.name = ''
}

const validateName = () => {
  if (!formData.name.trim()) {
    errors.name = '知识库名称不能为空'
    return false
  }
  if (formData.name.length < 2) {
    errors.name = '知识库名称至少需要2个字符'
    return false
  }
  if (formData.name.length > 50) {
    errors.name = '知识库名称不能超过50个字符'
    return false
  }
  errors.name = ''
  return true
}

const handleSubmit = async () => {
  if (!validateName()) {
    return
  }
  
  isSubmitting.value = true
  try {
    await emit('submit', {
      database_name: formData.name,
      description: formData.description
    })
    close()
  } catch (error) {
    console.error('创建知识库失败:', error)
  } finally {
    isSubmitting.value = false
  }
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
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
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
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #495057;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-group input.error {
  border-color: #e74c3c;
}

.form-group input.error:focus {
  box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1);
}

.error-message {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: #e74c3c;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn-cancel,
.btn-submit {
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

.btn-submit {
  background: #3498db;
  color: white;
}

.btn-submit:hover:not(:disabled) {
  background: #2980b9;
}

.btn-submit:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}
</style>
