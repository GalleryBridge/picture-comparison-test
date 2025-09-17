<template>
  <div class="comparison-chart">
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Object,
    required: true
  },
  type: {
    type: String,
    default: 'pie' // pie, bar, gauge, line
  },
  title: {
    type: String,
    default: ''
  },
  height: {
    type: String,
    default: '300px'
  }
})

const chartRef = ref()
let chartInstance = null

const initChart = () => {
  if (!chartRef.value) return
  
  chartInstance = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  if (!chartInstance || !props.data) return

  let option = {}

  switch (props.type) {
    case 'pie':
      option = {
        title: {
          text: props.title,
          left: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        series: [{
          name: props.title,
          type: 'pie',
          radius: '70%',
          data: props.data,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      }
      break

    case 'bar':
      option = {
        title: {
          text: props.title,
          left: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        xAxis: {
          type: 'category',
          data: props.data.categories || []
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          name: props.title,
          type: 'bar',
          data: props.data.values || [],
          itemStyle: {
            color: '#409eff'
          }
        }]
      }
      break

    case 'gauge':
      option = {
        title: {
          text: props.title,
          left: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          formatter: '{a} <br/>{b}: {c}%'
        },
        series: [{
          name: props.title,
          type: 'gauge',
          radius: '80%',
          data: [{
            value: props.data.value || 0,
            name: props.data.name || '数值'
          }],
          axisLine: {
            lineStyle: {
              width: 10,
              color: [
                [0.3, '#FF6E76'],
                [0.7, '#FDDD60'],
                [1, '#58D9F9']
              ]
            }
          },
          pointer: {
            itemStyle: {
              color: 'auto'
            }
          },
          axisTick: {
            distance: -30,
            splitNumber: 5,
            lineStyle: {
              width: 2,
              color: '#999'
            }
          },
          splitLine: {
            distance: -30,
            length: 30,
            lineStyle: {
              width: 4,
              color: '#999'
            }
          },
          axisLabel: {
            color: 'auto',
            distance: 40,
            fontSize: 12
          },
          detail: {
            valueAnimation: true,
            formatter: '{value}%',
            color: 'auto',
            fontSize: 20
          }
        }]
      }
      break

    case 'line':
      option = {
        title: {
          text: props.title,
          left: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: props.data.categories || []
        },
        yAxis: {
          type: 'value'
        },
        series: [{
          name: props.title,
          type: 'line',
          data: props.data.values || [],
          smooth: true,
          itemStyle: {
            color: '#409eff'
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [{
                offset: 0, color: 'rgba(64, 158, 255, 0.3)'
              }, {
                offset: 1, color: 'rgba(64, 158, 255, 0.1)'
              }]
            }
          }
        }]
      }
      break

    default:
      option = {}
  }

  chartInstance.setOption(option)
}

const resizeChart = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// 监听数据变化
watch(() => props.data, () => {
  updateChart()
}, { deep: true })

// 监听类型变化
watch(() => props.type, () => {
  updateChart()
})

onMounted(async () => {
  await nextTick()
  initChart()
  window.addEventListener('resize', resizeChart)
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  window.removeEventListener('resize', resizeChart)
})
</script>

<style scoped>
.comparison-chart {
  width: 100%;
  height: 100%;
}

.chart-container {
  width: 100%;
  height: v-bind(height);
}
</style>
