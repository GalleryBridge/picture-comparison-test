import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Upload from '@/views/Upload.vue'
import Results from '@/views/Results.vue'
import ResultDetail from '@/views/ResultDetail.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: '首页' }
  },
  {
    path: '/upload',
    name: 'Upload',
    component: Upload,
    meta: { title: '上传分析' }
  },
  {
    path: '/results',
    name: 'Results',
    component: Results,
    meta: { title: '历史记录' }
  },
  {
    path: '/results/:id',
    name: 'ResultDetail',
    component: ResultDetail,
    meta: { title: '分析详情' }
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
