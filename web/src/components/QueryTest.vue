<template>
  <div class="query-test-container">
    <div class="query-header">
      <h3>知识库查询测试</h3>
      <p class="query-hint" v-if="!selectedDatabaseId">请先选择一个知识库</p>
    </div>
    
    <div class="query-input-section">
      <textarea
        v-model="queryText"
        placeholder="输入您的问题..."
        rows="3"
        :disabled="!selectedDatabaseId || isQuerying"
        @keydown.ctrl.enter="handleQuery"
      ></textarea>
      <button 
        class="btn-query"
        @click="handleQuery"
        :disabled="!selectedDatabaseId || !queryText.trim() || isQuerying"
      >
        {{ isQuerying ? '查询中...' : '查询' }}
      </button>
    </div>
    
    <div class="query-results" v-if="queryResults.length > 0 || queryError">
      <div v-if="queryError" class="error-message">
        <span class="error-icon">⚠️</span>
        {{ queryError }}
      </div>
      
      <div v-else class="results-list">
        <div 
          v-for="(result, index) in queryResults" 
          :key="index"
          class="result-item"
        >
          <div class="result-header">
            <span class="result-index">#{{ index + 1 }}</span>
            <span class="result-score">相似度: {{ formatScore(result.score) }}</span>
          </div>
          <div class="result-content">
            {{ result.content }}
          </div>
          <div class="result-meta" v-if="result.metadata">
            <div 
              v-for="(value, key) in result.metadata" 
              :key="key"
              class="meta-item"
            >
              <span class="meta-label">{{ key }}:</span>
              <span class="meta-value">{{ value }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="empty-state" v-else-if="hasQueried && !isQuerying">
      <div class="empty-icon">🔍</div>
      <p>暂无查询结果</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { knowledgeApi } from '../api/knowledge'

const props = defineProps({
  selectedDatabaseId: {
    type: String,
    default: ''
  }
})

const queryText = ref('')
const isQuerying = ref(false)
const queryResults = ref([])
const queryError = ref('')
const hasQueried = ref(false)

const handleQuery = async () => {
  if (!props.selectedDatabaseId || !queryText.value.trim()) {
    return
  }
  
  isQuerying.value = true
  queryError.value = ''
  queryResults.value = []
  
  try {
    const response = await knowledgeApi.queryDatabase(
      props.selectedDatabaseId,
      queryText.value,
      {}
    )
    
    if (response.data.status === 'success') {
      queryResults.value = response.data.result || []
    } else {
      queryError.value = response.data.message || '查询失败'
    }
  } catch (error) {
    console.error('查询失败:', error)
    queryError.value = error.response?.data?.detail || error.message || '查询失败，请稍后重试'
  } finally {
    isQuerying.value = false
    hasQueried.value = true
  }
}

const formatScore = (score) => {
  if (typeof score === 'number') {
    return (score * 100).toFixed(2) + '%'
  }
  return score
}

defineExpose({
  clearResults: () => {
    queryResults.value = []
    queryError.value = ''
    hasQueried.value = false
  }
})
</script>

<style scoped>
.query-test-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.query-header {
  margin-bottom: 20px;
}

.query-header h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.query-hint {
  margin: 0;
  font-size: 14px;
  color: #e74c3c;
}

.query-input-section {
  margin-bottom: 20px;
}

.query-input-section textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ced4da;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  margin-bottom: 12px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.query-input-section textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.query-input-section textarea:disabled {
  background: #f8f9fa;
  cursor: not-allowed;
}

.btn-query {
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

.btn-query:hover:not(:disabled) {
  background: #2980b9;
}

.btn-query:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.query-results {
  max-height: 400px;
  overflow-y: auto;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f8d7da;
  color: #dc3545;
  border-radius: 6px;
  font-size: 14px;
}

.error-icon {
  font-size: 18px;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-item {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  background: #f8f9fa;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e9ecef;
}

.result-index {
  font-size: 14px;
  font-weight: 600;
  color: #3498db;
}

.result-score {
  font-size: 13px;
  color: #6c757d;
}

.result-content {
  font-size: 14px;
  line-height: 1.6;
  color: #2c3e50;
  margin-bottom: 12px;
  white-space: pre-wrap;
}

.result-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid #e9ecef;
}

.meta-item {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.meta-label {
  color: #6c757d;
}

.meta-value {
  color: #495057;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #6c757d;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

.query-results::-webkit-scrollbar {
  width: 6px;
}

.query-results::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.query-results::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 10px;
}

.query-results::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
