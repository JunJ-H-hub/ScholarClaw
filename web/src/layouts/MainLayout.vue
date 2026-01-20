<template>
  <div class="main-layout">
    <Sidebar 
      :collapsed="sidebarCollapsed"
      :is-mobile="isMobile"
      @toggle="toggleSidebar"
      @navigate="handleNavigate"
    />
    <MainContent 
      :collapsed="sidebarCollapsed"
      :is-mobile="isMobile"
      @toggle-sidebar="toggleSidebar"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Sidebar from '../components/Sidebar.vue'
import MainContent from '../components/MainContent.vue'

const router = useRouter()
const route = useRoute()

const sidebarCollapsed = ref(false)
const isMobile = ref(false)

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
  if (isMobile.value) {
    sidebarCollapsed.value = true
  }
}

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const handleNavigate = (path) => {
  if (isMobile.value) {
    sidebarCollapsed.value = true
  }
  router.push(path)
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.main-layout {
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}
</style>
