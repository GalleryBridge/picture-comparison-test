import { createRouter, createWebHistory } from 'vue-router'
import Upload from '@/views/Upload.vue'

const routes = [
  {
    path: '/',
    redirect: '/upload'
  },
  {
    path: '/upload',
    name: 'Upload',
    component: Upload,
    meta: { title: 'PDF图纸尺寸分析系统' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - PDF图纸尺寸分析系统`
  }
  next()
})

export default router
