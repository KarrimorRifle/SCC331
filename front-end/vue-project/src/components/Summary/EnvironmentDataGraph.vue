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
    type: Array,
    required: true, // Array of { temperature, sound, light, timestamp }
  },
  showModal: {
    type: Boolean,
    required: true,
  },
});

const emit = defineEmits(['close']); // Emits close event

const chartCanvas = ref(null);
let chartInstance = null;

const renderChart = () => {
  if (chartInstance) {
    chartInstance.destroy(); // Clear previous chart
  }

  if (chartCanvas.value) {
    chartInstance = new Chart(chartCanvas.value, {
      type: 'line',
      data: {
        labels: props.environmentData.map((d) => new Date(d.timestamp).toLocaleTimeString()), // X-axis timestamps
        datasets: [
          {
            label: '🌡️ Temperature (°C)',
            data: props.environmentData.map((d) => d.temperature),
            borderColor: 'red',
            fill: false,
          },
          {
            label: '🔊 Sound (dB)',
            data: props.environmentData.map((d) => d.sound),
            borderColor: 'blue',
            fill: false,
          },
          {
            label: '💡 Light (lux)',
            data: props.environmentData.map((d) => d.light),
            borderColor: 'yellow',
            fill: false,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
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
      <div class="modal-content">
        <div class="modal-graph-header">
            <h3>Environment Data - {{ areaLabel }}</h3>
            <button class="close-btn" @click="emit('close')">
                <font-awesome-icon :icon="faXmark" />
            </button>
        </div>

        <canvas ref="chartCanvas"></canvas>
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
  background: white;
  padding: 20px;
  width: 600px;
  height: 400px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  position: relative;
  color: black;
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
