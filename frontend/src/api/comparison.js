import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1/pdf-comparison',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const message = error.response?.data?.message || error.message || '请求失败'
    return Promise.reject(new Error(message))
  }
)

// API方法
export const comparisonApi = {
  // 文件比对
  async compareFiles(fileA, fileB, options = {}) {
    const formData = new FormData()
    formData.append('file_a', fileA)
    formData.append('file_b', fileB)
    
    // 添加比对选项
    Object.keys(options).forEach(key => {
      if (options[key] !== undefined && options[key] !== null) {
        formData.append(key, options[key])
      }
    })

    return await api.post('/compare', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 获取比对结果
  async getComparison(comparisonId) {
    return await api.get(`/compare/${comparisonId}`)
  },

  // 列出比对结果
  async listComparisons(page = 1, pageSize = 20) {
    return await api.get('/compare', {
      params: { page, page_size: pageSize }
    })
  },

  // 删除比对结果
  async deleteComparison(comparisonId) {
    return await api.delete('/compare', {
      data: { comparison_ids: [comparisonId] }
    })
  },

  // 生成高亮PDF
  async generateHighlight(comparisonId, options = {}) {
    return await api.post('/highlight', {
      comparison_id: comparisonId,
      ...options
    })
  },

  // 生成差异图像
  async generateRender(comparisonId, options = {}) {
    return await api.post('/render', {
      comparison_id: comparisonId,
      ...options
    })
  },

  // 生成报告
  async generateReport(comparisonId, options = {}) {
    return await api.post('/report', {
      comparison_id: comparisonId,
      ...options
    })
  },

  // 健康检查
  async getHealth() {
    return await api.get('/health')
  },

  // 获取统计信息
  async getStatistics() {
    return await api.get('/statistics')
  },

  // 文件上传
  async uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    return await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 下载文件
  downloadFile(filePath) {
    const url = `/api/v1/pdf-comparison/files/${filePath}`
    window.open(url, '_blank')
  }
}

// 导出默认API实例
export default api
