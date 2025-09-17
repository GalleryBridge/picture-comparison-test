import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Comparison from '@/views/Comparison.vue'
import Report from '@/views/Report.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: 'PDF图纸比对'
    }
  },
  {
    path: '/comparison/:id',
    name: 'Comparison',
    component: Comparison,
    meta: {
      title: '比对结果'
    }
  },
  {
    path: '/report/:id',
    name: 'Report',
    component: Report,
    meta: {
      title: '分析报告'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - PDF图纸比对系统`
  }
  next()
})

export default router
