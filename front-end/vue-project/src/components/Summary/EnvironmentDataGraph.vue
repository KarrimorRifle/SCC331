<script setup lang="ts">
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faXmark, faSpinner } from '@fortawesome/free-solid-svg-icons';
import { defineProps, ref, watch, onMounted, onBeforeUnmount, computed, type PropType } from 'vue';
import { Chart, registerables } from 'chart.js';
import axios from 'axios';
import { usePresetStore } from '@/utils/useFetchPresets';

const presetStore = usePresetStore();
Chart.register(...registerables);

const props = defineProps({
  areaLabel: {
    type: String,
    required: true,
  },
  areaLabels: {
    type: Array as PropType<string[]>,
    required: true
  },
  showModal: {
    type: Boolean,
    required: true,
  },
});

const emit = defineEmits(['close']); // Emits close event
const currentLabel = ref<number>(0);
const selectedTimeRange = ref('1min');
const sampleSize = ref<number>(15);
const currentUpperTime = ref<number>(0)

const totalTime = computed(() => {
  let rangeMs = 0;
  switch(selectedTimeRange.value) {
    case '7days': rangeMs = 7 * 24 * 3600 * 1000; break;
    case '5days': rangeMs = 5 * 24 * 3600 * 1000; break;
    case '2days': rangeMs = 2 * 24 * 3600 * 1000; break;
    case '1day':  rangeMs = 24 * 3600 * 1000; break;
    case '12hrs': rangeMs = 12 * 3600 * 1000; break;
    case '6hrs':  rangeMs = 6 * 3600 * 1000; break;
    case '3hrs':  rangeMs = 3 * 3600 * 1000; break;
    case '1hr':   rangeMs = 3600 * 1000; break;
    case '30min': rangeMs = 30 * 60 * 1000; break;
    case '15min': rangeMs = 15 * 60 * 1000; break;
    case '5min':  rangeMs = 5 * 60 * 1000; break;
    case '1min':  rangeMs = 60 * 1000; break;
    default:      rangeMs = 60 * 1000;
  }
  return rangeMs * (sampleSize.value || 1);
});

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

interface EnvironmentData {
  timestamp: string;
  light: number;
  IAQ: number;
  sound: number;
  temperature: number;
  pressure: number;
  humidity: number;
}

const environmentData = ref<EnvironmentData[]>([]);

const loading = ref<boolean>(false);

const renderChart = async() => {
  loading.value = true;
  const now = new Date(currentUpperTime.value);
  const oneHourAgo = new Date(currentUpperTime.value - totalTime.value);
  const request = await axios.get('/summary/average', {
    withCredentials: true,
    params: {
      start_time:oneHourAgo.toISOString(),
      end_time: now.toISOString(),
      time_periods: selectedTimeRange.value
    }
  });

  // Translate roomLabel to roomID:
  const entry = Object.entries(presetStore.boxes_and_data).find(([id, object]) =>
    object.label === props.areaLabels[currentLabel.value]
  );
  let id = entry ? entry[0] : 0;

  let env: any[] = [];

  if (request.data) {
    Object.entries(request.data).forEach(([time, rooms]) => {
      const roomData = (rooms as any)[id];
      if (roomData) {
        let object = {
          timestamp: time.slice(11,16),
          light: 0,
          IAQ: 0,
          sound: 0,
          temperature: 0,
          pressure: 0,
          humidity: 0
        };
        object.light = roomData.light?.average ?? 0;
        object.IAQ = roomData.IAQ?.average ?? 0;
        object.sound = roomData.sound?.average ?? 0;
        object.temperature = roomData.temperature?.average ?? 0;
        object.pressure = roomData.pressure?.average ?? 0;
        object.humidity = roomData.humidity?.average ?? 0;
        env.push(object);
      }
    });
  }

  environmentData.value = env;

  if (chartInstance) {
    chartInstance.destroy(); // Clear previous chart
  }

  if (chartCanvas.value) {
    // Build datasets array based on toggles
    const datasets = [];
    if (visibleDatasets.value.temperature) {
      datasets.push({
        label: '🌡️ Temperature (°C)',
        data: environmentData.value.map(item => item.temperature),
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
        data: environmentData.value.map(item => item.sound),
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
        data: environmentData.value.map(item => item.light),
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
        data: environmentData.value.map(item => item.IAQ),
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
        data: environmentData.value.map(item => item.pressure),
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
        data: environmentData.value.map(item => item.humidity),
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
        labels: environmentData.value.map(item => item.timestamp),
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
  loading.value = false;
};

// Replace watchers
let debounceTimer: number | null = null;
const debouncedRender = () => {
  if (debounceTimer) clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    renderChart();
    debounceTimer = null;
  }, 180);
};

watch(visibleDatasets, debouncedRender, { deep: true });
watch(currentLabel, debouncedRender);
watch(selectedTimeRange, debouncedRender);
watch(sampleSize, debouncedRender);
watch(currentUpperTime, debouncedRender);
onMounted(() => {
  let now = new Date();
  currentUpperTime.value = now.getTime()
  renderChart();
  currentLabel.value = props.areaLabels.findIndex(label => label === props.areaLabel);
});
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
              <div>
                <button class="btn btn-sm btn-outline-primary me-2" @click="currentLabel = currentLabel - 1 < 0 ? areaLabels.length - 1 : currentLabel - 1"><</button>
                <h3 class="d-inline-block align-top me-2 text-center" style="width: 15rem;">{{ areaLabels[currentLabel] }}</h3>
                <button class="btn btn-sm btn-outline-primary" @click="currentLabel = ++currentLabel % areaLabels.length">></button>
              </div>
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
            <div v-if="!loading && environmentData.length === 0">
              No data to display
            </div>
            <div v-show="!loading && environmentData.length !== 0" class="chart-container">
              <canvas ref="chartCanvas"></canvas>
            </div>
            <div v-if="loading" class="spinner-container">
              <font-awesome-icon :icon="faSpinner" spin size="2x" />
            </div>
          </div>
          <div class="button-container d-flex justify-content-center">
            <button class="btn btn-secondary btn-sm me-2" @click="currentUpperTime -= totalTime">
              <
            </button>
            <div class="d-inline-block me-2 align-bottom">
              {{ (new Date(currentUpperTime - totalTime)).toLocaleTimeString() }} - {{(new Date(currentUpperTime)).toLocaleTimeString() }}
            </div>
            <button class="btn btn-secondary btn-sm" @click="currentUpperTime = Math.min(currentUpperTime + totalTime, Date.now())">
              >
            </button>
            <select v-model="selectedTimeRange" class="form-select form-select-sm" style="width: auto; margin: 0 0.5rem;" limit="3">
              <option value="7days">7days</option>
              <option value="5days">5days</option>
              <option value="2days">2days</option>
              <option value="1day">1day</option>
              <option value="12hrs">12hrs</option>
              <option value="6hrs">6hrs</option>
              <option value="3hrs">3hrs</option>
              <option value="1hr">1hr</option>
              <option value="30min">30min</option>
              <option value="15min">15min</option>
              <option value="5min">5min</option>
              <option value="1min">1min</option>
            </select>
            <div class="input-group" style="max-width: fit-content;">
              <span class="input-group-text">Sample</span>
              <input v-model="sampleSize" style="width: 4rem;" class="form-control" type="number" value="20" name="sample" id="sample" min="15" max="99">
            </div>
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

.spinner-container {
  display: flex;
  width: 100%;
  justify-content: center;
  align-items: center;
  height: 100%;
}
</style>
