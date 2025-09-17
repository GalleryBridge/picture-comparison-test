<template>
  <div id="app">
    <el-container class="app-container">
      <!-- 头部导航 -->
      <el-header class="app-header">
        <div class="header-content">
          <div class="logo">
            <el-icon class="logo-icon"><Document /></el-icon>
            <span class="logo-text">PDF图纸比对系统</span>
          </div>
          <div class="header-actions">
            <el-button 
              type="primary" 
              :icon="Upload" 
              @click="goToUpload"
            >
              开始比对
            </el-button>
          </div>
        </div>
      </el-header>

      <!-- 主要内容区域 -->
      <el-main class="app-main">
        <router-view />
      </el-main>

      <!-- 底部信息 -->
      <el-footer class="app-footer">
        <div class="footer-content">
          <span>© 2024 PDF图纸比对系统 - 基于传统算法的高精度比对</span>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { Document, Upload } from '@element-plus/icons-vue'

const router = useRouter()

const goToUpload = () => {
  router.push('/')
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.app-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0 20px;
  height: 60px;
  display: flex;
  align-items: center;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 24px;
  color: #409eff;
}

.logo-text {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.app-main {
  padding: 20px;
  min-height: calc(100vh - 120px);
}

.app-footer {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.footer-content {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-header {
    padding: 0 10px;
  }
  
  .logo-text {
    font-size: 16px;
  }
  
  .app-main {
    padding: 10px;
  }
}
</style>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  background: #f5f7fa;
}

#app {
  min-height: 100vh;
}

/* Element Plus 自定义样式 */
.el-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: none;
}

.el-button {
  border-radius: 8px;
}

.el-input__wrapper {
  border-radius: 8px;
}

.el-upload-dragger {
  border-radius: 12px;
}

/* 动画效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  transform: translateY(20px);
  opacity: 0;
}

.slide-up-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}
</style>
