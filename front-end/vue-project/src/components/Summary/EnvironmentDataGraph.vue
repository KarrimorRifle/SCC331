<script setup lang="ts">
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faXmark } from '@fortawesome/free-solid-svg-icons';
import { defineProps, ref, watch, onMounted, onBeforeUnmount, computed } from 'vue';
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

// New: reactive object to control visible datasets
const visibleDatasets = ref({
  temperature: true,
  sound: true,
  light: true,
  IAQ: true,
  pressure: true,
  humidity: true,
});

// New: computed property to check if all datasets are selected
const allSelected = computed(() =>
  visibleDatasets.value.temperature &&
  visibleDatasets.value.sound &&
  visibleDatasets.value.light &&
  visibleDatasets.value.IAQ &&
  visibleDatasets.value.pressure &&
  visibleDatasets.value.humidity
);

// New: single toggle function for all datasets
const toggleAll = () => {
  const newValue = !allSelected.value;
  visibleDatasets.value.temperature = newValue;
  visibleDatasets.value.sound = newValue;
  visibleDatasets.value.light = newValue;
  visibleDatasets.value.IAQ = newValue;
  visibleDatasets.value.pressure = newValue;
  visibleDatasets.value.humidity = newValue;
};

const selectedTimeRange = ref('1min');

const renderChart = () => {
  if (chartInstance) {
    chartInstance.destroy(); // Clear previous chart
  }

  if (chartCanvas.value) {
    // Build datasets array based on toggles
    const datasets = [];
    if (visibleDatasets.value.temperature) {
      datasets.push({
        label: '🌡️ Temperature (°C)',
        data: props.environmentData.map(item => item.temperature),
        borderColor: 'red',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        borderWidth: 2,
        fill: false,
        tension: 0.4, // Smooth curve
      });
    }
    if (visibleDatasets.value.sound) {
      datasets.push({
        label: '🔊 Sound (dB)',
        data: props.environmentData.map(item => item.sound),
        borderColor: 'blue',
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderWidth: 2,
        fill: false,
        tension: 0.4,
      });
    }
    if (visibleDatasets.value.light) {
      datasets.push({
        label: '💡 Light (lux)',
        data: props.environmentData.map(item => item.light),
        borderColor: 'yellow',
        backgroundColor: 'rgba(255, 206, 86, 0.2)',
        borderWidth: 2,
        fill: false,
        tension: 0.4,
      });
    }
    if (visibleDatasets.value.IAQ) {
      datasets.push({
        label: '📊 IAQ',
        data: props.environmentData.map(item => item.IAQ),
        borderColor: 'green',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderWidth: 2,
        fill: false,
        tension: 0.4,
      });
    }
    if (visibleDatasets.value.pressure) {
      datasets.push({
        label: '⏱️ Pressure',
        data: props.environmentData.map(item => item.pressure),
        borderColor: 'purple',
        backgroundColor: 'rgba(153, 102, 255, 0.2)',
        borderWidth: 2,
        fill: false,
        tension: 0.4,
      });
    }
    if (visibleDatasets.value.humidity) {
      datasets.push({
        label: '💧 Humidity (%)',
        data: props.environmentData.map(item => item.humidity),
        borderColor: 'cyan',
        backgroundColor: 'rgba(0, 255, 255, 0.2)',
        borderWidth: 2,
        fill: false,
        tension: 0.4,
      });
    }

    chartInstance = new Chart(chartCanvas.value, {
      type: 'line', // Change to line chart
      data: {
        labels: props.environmentData.map(item => item.timestamp),
        datasets: datasets,
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
        plugins: {
          legend: {
            display: false
          }
        }
      },
    });
  }
};

// Watch for changes and update chart
watch(() => props.environmentData, renderChart, { deep: true });
watch(visibleDatasets, renderChart, { deep: true });
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
      <div style="height: 410px; background-color: white; border-radius: 1rem;">
        <div class="modal-content">
          <div class="modal-graph-header">
              <h3>Environment for: {{ areaLabel }}</h3>
              <button class="close-btn" @click="emit('close')">
                  <font-awesome-icon :icon="faXmark" />
              </button>
          </div>
          <div class="modal-body">
            <div class="dataset-toggles">
              <!-- New: single toggle button -->
              <div class="toggle-actions">
                <button type="button" @click="toggleAll" class="btn btn-sm" :class="{'btn-secondary': allSelected, 'btn-outline-secondary': !allSelected}">
                  {{ allSelected ? 'Deselect All' : 'Select All' }}
                </button>
              </div>
              <label class="px-2" style="border-radius: 4px; background-color: rgba(255,99,132,0.2)"><input type="checkbox" v-model="visibleDatasets.temperature" /> Temperature</label>
              <label class="px-2" style="border-radius: 4px; background-color: rgba(54,162,235,0.2)"><input type="checkbox" v-model="visibleDatasets.sound" /> Sound</label>
              <label class="px-2" style="border-radius: 4px; background-color: rgba(255,206,86,0.2)"><input type="checkbox" v-model="visibleDatasets.light" /> Light</label>
              <label class="px-2" style="border-radius: 4px; background-color: rgba(75,192,192,0.2)"><input type="checkbox" v-model="visibleDatasets.IAQ" /> IAQ</label>
              <label class="px-2" style="border-radius: 4px; background-color: rgba(153,102,255,0.2)"><input type="checkbox" v-model="visibleDatasets.pressure" /> Pressure</label>
              <label class="px-2" style="border-radius: 4px; background-color: rgba(0,255,255,0.2)"><input type="checkbox" v-model="visibleDatasets.humidity" /> Humidity</label>
            </div>
            <div class="chart-container">
              <canvas ref="chartCanvas"></canvas>
            </div>
          </div>
          <div class="button-container d-flex justify-content-center">
            <button class="btn btn-secondary btn-sm">
              <
            </button>
            <select v-model="selectedTimeRange" class="form-select form-select-sm" style="width: auto; margin: 0 0.5rem;" limit="3">
              <option value="1min">1min</option>
              <option value="5min">5min</option>
              <option value="15min">15min</option>
              <option value="30min">30min</option>
              <option value="1hr">1hr</option>
              <option value="3hrs">3hrs</option>
              <option value="6hrs">6hrs</option>
              <option value="12hrs">12hrs</option>
              <option value="1day">1day</option>
              <option value="2days">2days</option>
              <option value="5days">5days</option>
              <option value="7days">7days</option>
            </select>
            <button class="btn btn-secondary btn-sm">
              >
            </button>
          </div>
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
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.modal-graph-header{
    display: flex;
    flex-direction: row;
    justify-content: space-between;
}

.modal-body {
  display: flex;
  gap: 1rem;
  height: calc(100% - 60px); /* adjust as needed */
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

.dataset-toggles {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 120px;
  align-items: flex-start;
  font-size: 14px;
}
.dataset-toggles label {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.3rem;
}

.chart-container {
  flex: 1;
  position: relative;
}

.toggle-actions {
  display: flex;
  gap: 0.5rem;
}
</style>
