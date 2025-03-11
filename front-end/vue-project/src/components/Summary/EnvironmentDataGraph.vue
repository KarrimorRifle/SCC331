<script setup lang="ts">
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faXmark } from '@fortawesome/free-solid-svg-icons';
import { defineProps, ref, watch, onMounted, onBeforeUnmount } from 'vue';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

const props = defineProps({
  areaLabel: {
    type: String,
    required: true,
  },
  environmentData: {
    type: Array, // Changed from Object to Array
    required: true, // Array of { temperature, sound, light, timestamp, pressure, humidity, IAQ }
  },
  showModal: {
    type: Boolean,
    required: true,
  },
});

console.log(props.environmentData);
const emit = defineEmits(['close']); // Emits close event

const chartCanvas = ref(null);
let chartInstance = null;

const renderChart = () => {
  if (chartInstance) {
    chartInstance.destroy(); // Clear previous chart
  }

  if (chartCanvas.value) {
    chartInstance = new Chart(chartCanvas.value, {
      type: 'line', // Change to line chart
      data: {
        labels: props.environmentData.map(item => item.timestamp),
        datasets: [
          {
            label: '🌡️ Temperature (°C)',
            data: props.environmentData.map(item => item.temperature),
            borderColor: 'red',
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderWidth: 2,
            fill: false,
            tension: 0.4, // Smooth curve
          },
          {
            label: '🔊 Sound (dB)',
            data: props.environmentData.map(item => item.sound),
            borderColor: 'blue',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderWidth: 2,
            fill: false,
            tension: 0.4,
          },
          {
            label: '💡 Light (lux)',
            data: props.environmentData.map(item => item.light),
            borderColor: 'yellow',
            backgroundColor: 'rgba(255, 206, 86, 0.2)',
            borderWidth: 2,
            fill: false,
            tension: 0.4,
          },
          {
            label: '📊 IAQ',
            data: props.environmentData.map(item => item.IAQ),
            borderColor: 'green',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderWidth: 2,
            fill: false,
            tension: 0.4,
          },
          {
            label: '⏱️ Pressure',
            data: props.environmentData.map(item => item.pressure),
            borderColor: 'purple',
            backgroundColor: 'rgba(153, 102, 255, 0.2)',
            borderWidth: 2,
            fill: false,
            tension: 0.4,
          },
          {
            label: '💧 Humidity (%)',
            data: props.environmentData.map(item => item.humidity),
            borderColor: 'cyan',
            backgroundColor: 'rgba(0, 255, 255, 0.2)',
            borderWidth: 2,
            fill: false,
            tension: 0.4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            display: true,
          },
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 5, // Adjust step size for better readability
            },
          },
        },
        elements: {
          point: {
            radius: 5, // Increase point size
          },
        },
      },
    });
  }
};

// Watch for changes and update chart
watch(() => props.environmentData, renderChart, { deep: true });
onMounted(renderChart);
onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy();
  }
});
</script>

<template>
  <transition name="fade">
    <div v-if="showModal" class="modal-overlay">
      <div style="height: 430px; background-color: white; border-radius: 1rem;">
        <div class="modal-content">
          <div class="modal-graph-header">
              <h3>Environment Data - Area {{ areaLabel }}</h3>
              <button class="close-btn" @click="emit('close')">
                  <font-awesome-icon :icon="faXmark" />
              </button>
          </div>

          <canvas ref="chartCanvas"></canvas>
        </div>
        </div>
    </div>
  </transition>
</template>

<style scoped>
/* Modal Overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

/* Modal Content */
.modal-content {
  background: var(--primary-light-bg);
  padding: 20px;
  width: 600px;
  height: 400px;
  border-radius: 8px;
  position: relative;
  color: var(--primary-dark-text);
}

.modal-graph-header{
    display: flex;
    flex-direction: row;
    justify-content: space-between;
}
/* Close Button */
.close-btn {
  border: none;
  outline: none;
  font-size: 20px;
  cursor: pointer;
  background: none;
  transition: transform 0.3s ease-in-out 0.1s;
}
.close-btn:hover{
  transform: scale(1.2);
}
.close-btn i {
  font-size: 24px;
}
/* Fade Animation */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>
