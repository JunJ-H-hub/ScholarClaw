<template>
  <div 
    class="database-card" 
    :class="{ 'selected': isSelected }"
    @click="$emit('select', database)"
  >
    <div class="card-header">
      <h3 class="database-name">{{ database.name }}</h3>
      <div class="card-actions">
        <button 
          class="btn-delete" 
          @click.stop="$emit('delete', database)"
          title="删除知识库"
        >
          ✕
        </button>
      </div>
    </div>
    
    <div class="card-body">
      <p class="database-description">{{ database.description || '暂无描述' }}</p>
      
      <div class="database-info">
        <div class="info-item">
          <span class="info-label">类型:</span>
          <span class="info-value">{{ database.kb_type || 'chroma' }}</span>
        </div>
        <div class="info-item" v-if="database.embedding_model">
          <span class="info-label">模型:</span>
          <span class="info-value">{{ database.embedding_model }}</span>
        </div>
        <div class="info-item" v-if="database.document_count !== undefined">
          <span class="info-label">文档数:</span>
          <span class="info-value">{{ database.document_count }}</span>
        </div>
      </div>
    </div>
    
    <div class="card-footer">
      <button 
        class="btn-select" 
        :class="{ 'active': isSelected }"
        @click.stop="$emit('select', database)"
      >
        {{ isSelected ? '已选中' : '选择' }}
      </button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  database: {
    type: Object,
    required: true
  },
  isSelected: {
    type: Boolean,
    default: false
  }
})

defineEmits(['select', 'delete'])

console.log('DatabaseCard渲染:', {
  database: props.database,
  databaseId: props.database.id,
  dbId: props.database.db_id,
  isSelected: props.isSelected
})
</script>

<style scoped>
.database-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  cursor: pointer;
  border: 2px solid transparent;
}

.database-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.database-card.selected {
  border-color: #3498db;
  background: #f0f8ff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.database-name {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.btn-delete {
  width: 28px;
  height: 28px;
  border: none;
  background: #e74c3c;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.btn-delete:hover {
  background: #c0392b;
}

.card-body {
  margin-bottom: 16px;
}

.database-description {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #7f8c8d;
  line-height: 1.5;
}

.database-info {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  font-size: 13px;
}

.info-label {
  color: #95a5a6;
  margin-right: 4px;
}

.info-value {
  color: #34495e;
  font-weight: 500;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
}

.btn-select {
  padding: 8px 20px;
  border: 2px solid #3498db;
  background: white;
  color: #3498db;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-select:hover {
  background: #3498db;
  color: white;
}

.btn-select.active {
  background: #3498db;
  color: white;
}
</style>
