import { createRouter, createWebHistory } from 'vue-router'
import App from '../App.vue'
import KnowledgeBase from '../views/KnowledgeBase.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: App
  },
  {
    path: '/knowledge',
    name: 'KnowledgeBase',
    component: KnowledgeBase
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
