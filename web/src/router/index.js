import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import Home from '../App.vue'
import KnowledgeBase from '../views/KnowledgeBase.vue'
import History from '../views/History.vue'

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'Home',
        component: Home,
        meta: {
          title: '报告生成',
          icon: '📝'
        }
      },
      {
        path: 'history',
        name: 'History',
        component: History,
        meta: {
          title: '历史报告',
          icon: '📚'
        }
      },
      {
        path: 'knowledge',
        name: 'KnowledgeBase',
        component: KnowledgeBase,
        meta: {
          title: '知识库管理',
          icon: '🗄️'
        }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
