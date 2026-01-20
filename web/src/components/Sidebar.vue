<template>
  <div 
    class="sidebar" 
    :class="{ 'collapsed': collapsed, 'mobile': isMobile }"
  >
    <div class="sidebar-header">
      <div class="logo" v-if="!collapsed">
        <span class="logo-icon">📊</span>
        <span class="logo-text">Paper Agent</span>
      </div>
      <button 
        class="toggle-btn"
        @click="$emit('toggle')"
        :title="collapsed ? '展开侧边栏' : '折叠侧边栏'"
      >
        {{ collapsed ? '→' : '←' }}
      </button>
    </div>

    <nav class="sidebar-nav">
      <div 
        v-for="item in menuItems" 
        :key="item.path"
        class="nav-item"
        :class="{ 'active': isActive(item.path), 'has-children': item.children }"
      >
        <div 
          class="nav-item-header"
          @click="item.children ? toggleChildren(item) : navigate(item.path)"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-text" v-if="!collapsed">{{ item.title }}</span>
          <span 
            class="expand-icon" 
            v-if="item.children && !collapsed"
            :class="{ 'expanded': item.expanded }"
          >
            ▼
          </span>
        </div>

        <div 
          class="nav-children" 
          v-if="item.children && item.expanded && !collapsed"
        >
          <div 
            v-for="child in item.children" 
            :key="child.path"
            class="nav-child-item"
            :class="{ 'active': isActive(child.path) }"
            @click="navigate(child.path)"
          >
            <span class="nav-icon">{{ child.icon }}</span>
            <span class="nav-text">{{ child.title }}</span>
          </div>
        </div>
      </div>
    </nav>

    <div class="sidebar-footer" v-if="!collapsed">
      <div class="user-info">
        <span class="user-avatar">👤</span>
        <span class="user-name">用户</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
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

const emit = defineEmits(['toggle', 'navigate'])

const route = useRoute()

const menuItems = ref([
  {
    title: '报告生成',
    path: '/',
    icon: '📝',
    children: [
      {
        title: '新建报告',
        path: '/',
        icon: '➕'
      },
      {
        title: '历史报告',
        path: '/history',
        icon: '📚'
      }
    ],
    expanded: true
  },
  {
    title: '知识库管理',
    path: '/knowledge',
    icon: '🗄️',
    expanded: false
  }
])

const isActive = (path) => {
  return route.path === path || route.path.startsWith(path + '/')
}

const toggleChildren = (item) => {
  item.expanded = !item.expanded
}

const navigate = (path) => {
  emit('navigate', path)
}
</script>

<style scoped>
.sidebar {
  width: 12%;
  min-width: 200px;
  max-width: 280px;
  height: 100%;
  background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 1000;
}

.sidebar.collapsed {
  width: 70px;
  min-width: 70px;
  max-width: 70px;
}

.sidebar.mobile {
  position: fixed;
  left: 0;
  top: 0;
  z-index: 2000;
}

.sidebar.mobile.collapsed {
  transform: translateX(-100%);
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 70px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  transition: opacity 0.3s ease;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  color: white;
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
}

.toggle-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  font-size: 16px;
}

.toggle-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

.toggle-btn:active {
  transform: scale(0.95);
}

.sidebar.collapsed .toggle-btn {
  margin: 0 auto;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
}

.nav-item {
  margin: 4px 10px;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s ease;
}

.nav-item-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.8);
  transition: all 0.2s ease;
  border-radius: 8px;
  position: relative;
}

.nav-item-header:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item-header:active {
  transform: scale(0.98);
}

.nav-item.active > .nav-item-header {
  background: rgba(52, 152, 219, 0.3);
  color: white;
  font-weight: 500;
}

.nav-item.active > .nav-item-header::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 60%;
  background: #3498db;
  border-radius: 0 4px 4px 0;
}

.nav-icon {
  font-size: 18px;
  min-width: 24px;
  text-align: center;
}

.nav-text {
  flex: 1;
  margin-left: 12px;
  white-space: nowrap;
  transition: opacity 0.2s ease;
}

.sidebar.collapsed .nav-text {
  display: none;
}

.expand-icon {
  font-size: 10px;
  transition: transform 0.3s ease;
  color: rgba(255, 255, 255, 0.6);
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.nav-children {
  margin-top: 4px;
  padding-left: 12px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 0 0 8px 8px;
}

.nav-child-item {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.7);
  transition: all 0.2s ease;
  border-radius: 6px;
  margin: 2px 0;
}

.nav-child-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-child-item.active {
  background: rgba(52, 152, 219, 0.4);
  color: white;
  font-weight: 500;
}

.nav-child-item .nav-icon {
  font-size: 14px;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  color: rgba(255, 255, 255, 0.8);
}

.user-avatar {
  font-size: 24px;
}

.user-name {
  font-size: 14px;
}

.sidebar.collapsed .sidebar-footer {
  display: none;
}

.sidebar-nav::-webkit-scrollbar {
  width: 6px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.sidebar-nav::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

@media (max-width: 768px) {
  .sidebar {
    width: 280px;
    min-width: 280px;
    max-width: 280px;
  }

  .sidebar.collapsed {
    transform: translateX(-100%);
  }
}
</style>
