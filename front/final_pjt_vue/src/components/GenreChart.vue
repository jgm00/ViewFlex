<template>
  <div class="chart-header">
    <h2>장르 통계</h2>
    <span class="genre-count">(총 {{ props.genreStats.length }}개의 장르)</span>
  </div>
  <div class="chart-container">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  genreStats: {
    type: Array,
    required: true
  }
})

let chartInstance = null
const chartCanvas = ref(null)

const renderChart = () => {
  const ctx = chartCanvas.value.getContext('2d')

  if (chartInstance) {
    chartInstance.destroy()
  }

  // 모던한 색상 팔레트
  const colors = [
    '#4A90E2',  // 파랑
    '#50E3C2',  // 민트
    '#F5A623',  // 주황
    '#7ED321',  // 초록
    '#B8E986',  // 연두
    '#BD10E0',  // 보라
    '#9013FE',  // 자주
    '#417505',  // 진초록
    '#4A4A4A',  // 진회색
    '#D0021B',  // 빨강
  ].map(color => `${color}CC`)  // 투명도 80% 적용

  const hoverColors = colors.map(color => color.replace('CC', 'FF'))

  chartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: props.genreStats.map(item => item.genre),
      datasets: [{
        data: props.genreStats.map(item => item.count),
        backgroundColor: colors,
        hoverBackgroundColor: hoverColors,
        borderWidth: 2,
        borderColor: '#ffffff',
        spacing: 5,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      devicePixelRatio: window.devicePixelRatio || 1,
      layout: {
        padding: {
          top: 20,
          bottom: 20,
          left: 20,
          right: 20
        }
      },
      plugins: {
        tooltip: {
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          titleColor: '#1a1a1a',
          bodyColor: '#4a4a4a',
          titleFont: {
            size: 14,
            weight: '600',
            family: "'Pretendard', sans-serif"
          },
          bodyFont: {
            size: 13,
            weight: '500',
            family: "'Pretendard', sans-serif"
          },
          callbacks: {
            label: function(context) {
              const label = context.label || '';
              const value = context.raw || 0;
              const total = context.dataset.data.reduce((acc, curr) => acc + curr, 0);
              const percentage = ((value / total) * 100).toFixed(1);
              return `${label}: ${value}개 (${percentage}%)`;
            }
          }
        },
        legend: {
          position: 'top',
          align: 'center',
          labels: {
            padding: 15,
            usePointStyle: true,
            pointStyle: 'circle',
            boxWidth: 8,
            boxHeight: 8,
            font: {
              size: 12,
              weight: '500',
              family: "'Pretendard', sans-serif"
            },
            generateLabels: function(chart) {
              const data = chart.data;
              if (data.labels.length && data.datasets.length) {
                return data.labels.map((label, i) => {
                  const meta = chart.getDatasetMeta(0);
                  const style = meta.controller.getStyle(i);

                  return {
                    text: label,
                    fillStyle: style.backgroundColor,
                    strokeStyle: style.borderColor,
                    lineWidth: style.borderWidth,
                    hidden: meta.data[i].hidden,
                    index: i
                  };
                });
              }
              return [];
            }
          },
          onClick: function(e, legendItem, legend) {
            const index = legendItem.index;
            const chart = legend.chart;
            const meta = chart.getDatasetMeta(0);
            meta.data[index].hidden = !meta.data[index].hidden;
            chart.update();
          }
        }
      },
      cutout: '65%',
      radius: '90%',
      hover: {
        mode: 'nearest',
        intersect: true,
        animationDuration: 200
      },
      animation: {
        animateScale: true,
        animateRotate: true
      }
    }
  })
}

onMounted(() => {
  renderChart()
})

watch(() => props.genreStats, () => {
  renderChart()
}, { deep: true })
</script>

<style scoped>
.chart-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 1rem;
  padding-left: 1rem;
}

.chart-header h2 {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 600;
}

.genre-count {
  color: #666;
  font-size: 1rem;
}

.chart-container {
  position: relative;
  height: 400px;
  width: 100%;
  max-width: 500px;
  margin: 3rem auto;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.95);
  border: 2px solid #00000000;
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

canvas {
  max-width: 100%;
  max-height: 100%;
  cursor: pointer;
}

.chart-container:hover {
  /* transform과 box-shadow 효과 제거 */
}

.chart-container::before {
  /* 전체 제거 */
}

@keyframes borderGlow {
  /* 전체 제거 */
}

@media (max-width: 768px) {
  .chart-container {
    height: 350px;
    padding: 1rem;
  }
  
  .chart-header h2 {
    font-size: 1.5rem;
  }
  
  .genre-count {
    font-size: 0.9rem;
  }
}
</style>