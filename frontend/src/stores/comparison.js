import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { comparisonApi } from '@/api/comparison'

export const useComparisonStore = defineStore('comparison', () => {
  // 状态
  const comparisons = ref([])
  const currentComparison = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // 计算属性
  const hasComparisons = computed(() => comparisons.value.length > 0)
  const currentComparisonId = computed(() => currentComparison.value?.comparison_id)

  // 操作
  const setLoading = (value) => {
    loading.value = value
  }

  const setError = (errorMessage) => {
    error.value = errorMessage
  }

  const clearError = () => {
    error.value = null
  }

  const addComparison = (comparison) => {
    comparisons.value.unshift(comparison)
  }

  const setCurrentComparison = (comparison) => {
    currentComparison.value = comparison
  }

  const updateComparison = (comparisonId, updates) => {
    const index = comparisons.value.findIndex(c => c.comparison_id === comparisonId)
    if (index !== -1) {
      comparisons.value[index] = { ...comparisons.value[index], ...updates }
    }
    
    if (currentComparison.value?.comparison_id === comparisonId) {
      currentComparison.value = { ...currentComparison.value, ...updates }
    }
  }

  const removeComparison = (comparisonId) => {
    comparisons.value = comparisons.value.filter(c => c.comparison_id !== comparisonId)
    if (currentComparison.value?.comparison_id === comparisonId) {
      currentComparison.value = null
    }
  }

  // API 操作
  const compareFiles = async (fileA, fileB, options = {}) => {
    setLoading(true)
    clearError()
    
    try {
      const result = await comparisonApi.compareFiles(fileA, fileB, options)
      addComparison(result)
      setCurrentComparison(result)
      return result
    } catch (err) {
      setError(err.message || '比对失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const getComparison = async (comparisonId) => {
    setLoading(true)
    clearError()
    
    try {
      const result = await comparisonApi.getComparison(comparisonId)
      setCurrentComparison(result)
      return result
    } catch (err) {
      setError(err.message || '获取比对结果失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const generateHighlight = async (comparisonId, options = {}) => {
    setLoading(true)
    clearError()
    
    try {
      const result = await comparisonApi.generateHighlight(comparisonId, options)
      updateComparison(comparisonId, { highlightResult: result })
      return result
    } catch (err) {
      setError(err.message || '生成高亮PDF失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const generateReport = async (comparisonId, options = {}) => {
    setLoading(true)
    clearError()
    
    try {
      const result = await comparisonApi.generateReport(comparisonId, options)
      updateComparison(comparisonId, { reportResult: result })
      return result
    } catch (err) {
      setError(err.message || '生成报告失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const generateRender = async (comparisonId, options = {}) => {
    setLoading(true)
    clearError()
    
    try {
      const result = await comparisonApi.generateRender(comparisonId, options)
      updateComparison(comparisonId, { renderResult: result })
      return result
    } catch (err) {
      setError(err.message || '生成差异图像失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const deleteComparison = async (comparisonId) => {
    setLoading(true)
    clearError()
    
    try {
      await comparisonApi.deleteComparison(comparisonId)
      removeComparison(comparisonId)
    } catch (err) {
      setError(err.message || '删除比对失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const listComparisons = async (page = 1, pageSize = 20) => {
    setLoading(true)
    clearError()
    
    try {
      const result = await comparisonApi.listComparisons(page, pageSize)
      comparisons.value = result.comparisons
      return result
    } catch (err) {
      setError(err.message || '获取比对列表失败')
      throw err
    } finally {
      setLoading(false)
    }
  }

  return {
    // 状态
    comparisons,
    currentComparison,
    loading,
    error,
    
    // 计算属性
    hasComparisons,
    currentComparisonId,
    
    // 操作
    setLoading,
    setError,
    clearError,
    addComparison,
    setCurrentComparison,
    updateComparison,
    removeComparison,
    
    // API 操作
    compareFiles,
    getComparison,
    generateHighlight,
    generateReport,
    generateRender,
    deleteComparison,
    listComparisons
  }
})
