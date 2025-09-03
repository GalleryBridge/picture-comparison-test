<template>
  <div class="home-container">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-content">
        <h1 class="title">
          <el-icon class="title-icon"><Document /></el-icon>
          PDF图纸尺寸分析系统
        </h1>
        <p class="subtitle">基于 Qwen2.5-VL 多模态大模型的智能图纸尺寸识别与分析</p>
        
        <div class="action-buttons">
          <el-button 
            type="primary" 
            size="large" 
            @click="$router.push('/upload')"
            :icon="Upload"
          >
            开始分析
          </el-button>
          <el-button 
            size="large" 
            @click="$router.push('/results')"
            :icon="FolderOpened"
          >
            查看历史
          </el-button>
        </div>
      </div>
    </div>

    <!-- 功能特性 -->
    <div class="features-section">
      <div class="section-title">
        <h2>核心功能</h2>
        <p>强大的PDF图纸分析能力，助力工程设计效率提升</p>
      </div>
      
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">
            <el-icon><Upload /></el-icon>
          </div>
          <h3>PDF上传</h3>
          <p>支持多页PDF文档上传，自动解析页面内容</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">
            <el-icon><View /></el-icon>
          </div>
          <h3>智能识别</h3>
          <p>基于AI模型自动识别图纸中的尺寸标注信息</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <h3>结果分析</h3>
          <p>结构化展示识别结果，支持页面级别查看</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <h3>历史记录</h3>
          <p>保存分析历史，支持搜索和管理功能</p>
        </div>
      </div>
    </div>

    <!-- 使用统计 -->
    <div class="stats-section" v-if="stats">
      <div class="section-title">
        <h2>使用统计</h2>
      </div>
      
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-number">{{ stats.totalFiles }}</div>
          <div class="stat-label">已处理文件</div>
        </div>
        
        <div class="stat-card">
          <div class="stat-number">{{ stats.totalPages }}</div>
          <div class="stat-label">分析页面数</div>
        </div>
        
        <div class="stat-card">
          <div class="stat-number">{{ stats.totalDimensions }}</div>
          <div class="stat-label">识别尺寸数</div>
        </div>
        
        <div class="stat-card">
          <div class="stat-number">{{ stats.avgAccuracy }}%</div>
          <div class="stat-label">平均准确率</div>
        </div>
      </div>
    </div>

    <!-- 快速开始 -->
    <div class="quick-start-section">
      <div class="section-title">
        <h2>快速开始</h2>
        <p>三步完成PDF图纸尺寸分析</p>
      </div>
      
      <div class="steps">
        <div class="step">
          <div class="step-number">1</div>
          <div class="step-content">
            <h4>上传PDF</h4>
            <p>选择需要分析的PDF图纸文件</p>
          </div>
        </div>
        
        <div class="step-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
        
        <div class="step">
          <div class="step-number">2</div>
          <div class="step-content">
            <h4>AI分析</h4>
            <p>系统自动识别图纸中的尺寸信息</p>
          </div>
        </div>
        
        <div class="step-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
        
        <div class="step">
          <div class="step-number">3</div>
          <div class="step-content">
            <h4>查看结果</h4>
            <p>获取结构化的尺寸分析结果</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { 
  Document, 
  Upload, 
  FolderOpened, 
  View, 
  DataAnalysis, 
  Clock, 
  ArrowRight 
} from '@element-plus/icons-vue'

// 统计数据
const stats = ref({
  totalFiles: 0,
  totalPages: 0,
  totalDimensions: 0,
  avgAccuracy: 0
})

// 模拟获取统计数据
const fetchStats = async () => {
  // TODO: 实际从API获取统计数据
  stats.value = {
    totalFiles: 156,
    totalPages: 423,
    totalDimensions: 1247,
    avgAccuracy: 94
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 欢迎区域 */
.welcome-section {
  text-align: center;
  padding: 60px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  margin-bottom: 60px;
  color: white;
}

.title {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.title-icon {
  font-size: 52px;
}

.subtitle {
  font-size: 20px;
  margin-bottom: 40px;
  opacity: 0.9;
}

.action-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
}

/* 功能特性 */
.features-section {
  margin-bottom: 60px;
}

.section-title {
  text-align: center;
  margin-bottom: 40px;
}

.section-title h2 {
  font-size: 32px;
  margin-bottom: 10px;
  color: #333;
}

.section-title p {
  font-size: 16px;
  color: #666;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.feature-card {
  text-align: center;
  padding: 30px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.feature-icon {
  width: 60px;
  height: 60px;
  margin: 0 auto 20px;
  background: #409EFF;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.feature-card h3 {
  font-size: 20px;
  margin-bottom: 10px;
  color: #333;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
}

/* 统计数据 */
.stats-section {
  margin-bottom: 60px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  text-align: center;
  padding: 30px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-number {
  font-size: 36px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

/* 快速开始 */
.quick-start-section {
  margin-bottom: 60px;
}

.steps {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 40px;
  flex-wrap: wrap;
}

.step {
  display: flex;
  align-items: center;
  gap: 20px;
  max-width: 250px;
}

.step-number {
  width: 50px;
  height: 50px;
  background: #409EFF;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  flex-shrink: 0;
}

.step-content h4 {
  font-size: 18px;
  margin-bottom: 5px;
  color: #333;
}

.step-content p {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.step-arrow {
  color: #409EFF;
  font-size: 24px;
}

@media (max-width: 768px) {
  .title {
    font-size: 32px;
  }
  
  .subtitle {
    font-size: 16px;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .steps {
    flex-direction: column;
  }
  
  .step-arrow {
    transform: rotate(90deg);
  }
}
</style>
