<template>
  <div id="app">
    <el-container class="layout-container">
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-content">
          <div class="logo">
            <el-icon><Document /></el-icon>
            <span>PDF图纸尺寸分析系统</span>
          </div>
          <div class="nav-menu">
            <el-menu
              :default-active="$route.path"
              mode="horizontal"
              router
              background-color="transparent"
              text-color="#333"
              active-text-color="#409EFF"
            >
              <el-menu-item index="/">首页</el-menu-item>
              <el-menu-item index="/upload">上传分析</el-menu-item>
              <el-menu-item index="/results">历史记录</el-menu-item>
            </el-menu>
          </div>
        </div>
      </el-header>

      <!-- 主要内容区域 -->
      <el-main class="main-content">
        <router-view />
      </el-main>

      <!-- 底部信息 -->
      <el-footer class="footer">
        <div class="footer-content">
          <span>© 2024 PDF图纸尺寸分析系统 - 基于 Qwen2.5-VL 模型</span>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { Document } from '@element-plus/icons-vue'
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  padding: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.logo .el-icon {
  margin-right: 8px;
  font-size: 24px;
  color: #409EFF;
}

.nav-menu {
  flex: 1;
  display: flex;
  justify-content: flex-end;
}

.main-content {
  background: #f5f5f5;
  min-height: calc(100vh - 120px);
  padding: 20px;
}

.footer {
  background: #fff;
  border-top: 1px solid #e6e6e6;
  height: 60px;
  display: flex;
  align-items: center;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  color: #666;
  font-size: 14px;
}
</style>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

#app {
  width: 100%;
  height: 100%;
}
</style>
