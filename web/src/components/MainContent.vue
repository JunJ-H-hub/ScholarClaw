<template>
  <div 
    class="main-content" 
    :class="{ 'sidebar-collapsed': collapsed }"
  >
    <div class="content-header" v-if="isMobile">
      <button 
        class="mobile-menu-btn"
        @click="$emit('toggle-sidebar')"
      >
        ☰
      </button>
      <h1 class="page-title">{{ pageTitle }}</h1>
    </div>

    <div class="content-wrapper">
      <div class="loading-overlay" v-if="isLoading">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>

      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <keep-alive>
            <component :is="Component" @loading="handleLoading" />
          </keep-alive>
        </transition>
      </router-view>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  collapsed: {
    type: Boolean,
    default: false
  },
  isMobile: {
    type: Boolean,
    default: false
  }
})

defineEmits(['toggle-sidebar'])

const route = useRoute()
const isLoading = ref(false)

const pageTitle = computed(() => {
  const titles = {
    '/': '报告生成',
    '/history': '历史报告',
    '/knowledge': '知识库管理'
  }
  return titles[route.path] || 'Paper Agent'
})

const handleLoading = (loading) => {
  isLoading.value = loading
}

watch(() => route.path, () => {
  isLoading.value = false
})
</script>

<style scoped>
.main-content {
  flex: 1;
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  transition: all 0.3s ease;
}

.content-header {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  background: white;
  border-bottom: 1px solid #e1e8ed;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.mobile-menu-btn {
  background: #f8f9fa;
  border: 1px solid #e1e8ed;
  border-radius: 6px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 18px;
  color: #2c3e50;
  transition: all 0.2s ease;
  margin-right: 12px;
}

.mobile-menu-btn:hover {
  background: #e9ecef;
  transform: scale(1.05);
}

.mobile-menu-btn:active {
  transform: scale(0.95);
}

.page-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.content-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  position: relative;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.loading-spinner {
  width: 48px;
  height: 48px;
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

.loading-overlay p {
  margin: 0;
  color: #6c757d;
  font-size: 14px;
}

.page-fade-enter-active,
.page-fade-leave-active {
  transition: all 0.3s ease;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.content-wrapper::-webkit-scrollbar {
  width: 8px;
}

.content-wrapper::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.content-wrapper::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 10px;
}

.content-wrapper::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

@media (min-width: 769px) {
  .content-header {
    display: none;
  }
}

@media (max-width: 768px) {
  .content-wrapper {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .content-wrapper {
    padding: 12px;
  }

  .page-title {
    font-size: 16px;
  }
}
</style>
