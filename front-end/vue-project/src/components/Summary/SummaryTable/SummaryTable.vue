<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { getTextColour } from '../../../utils/helper/colorUtils';
import { usePresetStore } from '../../../utils/useFetchPresets';
import { sensors, sensorMapping } from '../../../stores/sensorTypeStore';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import PersonMarker from '../../ObjectMarker/PersonMarker.vue';
import LuggageMarker from '../../ObjectMarker/LuggageMarker.vue';
import EnvironmentDataGraph from '../EnvironmentDataGraph.vue';
import SummaryTableFilterBar from "./SummaryTableFilterBar.vue";
import { faUser, faClipboardCheck, faShieldAlt, faSuitcase, faQuestion, faChevronLeft, faChevronRight, faChevronUp, faChevronDown, faL } from '@fortawesome/free-solid-svg-icons';


const props = defineProps({
  data: {
    type: Object,
    required: true,
  },
});
const presetStore = usePresetStore();
const presetData = computed(() =>
  Object.values(presetStore.boxes_and_data).map(area => ({
    ...area,
    tracker: area.tracker || {},
  }))
);

// Multi-selection state (stores selected areas)
const selectedAreas = ref([]);
const activeGraphArea = ref(null);
const showModal = ref(false);
const showFilterBar = ref(true);

const toggleFilterVisibility = () => {
  showFilterBar.value = !showFilterBar.value;
};

// Toggle modal for environment graph
const openGraph = async(areaLabel) => {
  activeGraphArea.value = areaLabel;
  showModal.value = true;
};

const closeGraph = () => {
  showModal.value = false;
};

// Computed property for filtered areas
const filteredAreas = computed(() => presetData.value.filter(area => selectedAreas.value.includes(area.label)));

watch(presetData, (newVal, oldVal) => {
  // If newVal contains rooms not in selectedAreas, add them
  newVal.forEach(area => {
    if (!selectedAreas.value.includes(area.label)) {
      selectedAreas.value.push(area.label);
    }
  });
});

onMounted(() => {
  selectedAreas.value = presetData.value.map(area => area.label);
});

// Computed: Object Trackers (Users, Luggage, etc.)
const getObjectTrackers = (area) => {
  return Object.entries(sensorMapping.value)
    .filter(([_, sensor]) => sensor.type === 2) // Filter only type 2 (object trackers)
    .map(([key, sensor]) => ({
      key,
      name: sensor.name,
      icon: sensor.icon,
      count: area.tracker?.[key]?.count ?? 0, // Use count if available, default to 0
    }));
};

// Computed: Environment Sensors (Temperature, Sound, etc.)
const getEnvironmentSensors = (area) => {
  return Object.entries(sensorMapping.value)
    .filter(([_, sensor]) => sensor.type === 1) // Only Environment Sensors
    .map(([key, sensor]) => ({
      key,
      name: sensor.name,
      icon: sensor.icon,
      value: area.tracker?.environment?.[key] ?? '--' // Default to "N/A" if missing
    }));
}

const formatSensorName = (name: string): string => {
  return name.replace(/\s*Sensor\s*/i, '').trim();
};

// Add helper function to return icon mapping based on type using imported icons
const getIcon = (type: string) => {
  switch (type.toLowerCase()) {
    case 'guard':
      return faShieldAlt;
    case 'luggage':
      return faSuitcase;
    case 'users':
      return faUser;
    case 'staff':
      return faClipboardCheck;
    default:
      return faQuestion;
  }
};

// New helper to return color per role
const getRoleColor = (type: string) => {
  switch (type.toLowerCase()) {
    case 'guard':
      return 'blue';
    case 'luggage':
      return 'grey';
    case 'users':
      return 'darkblue';
    case 'staff':
      return 'green';
    default:
      return 'black';
  }
};

const getEmoji = (key: string) => {
  const emojiMapping: Record<string, string> = {
    temperature: '🌡️',
    IAQ: '🌬️',
    sound: '🔊',
    pressure: '🌡️',
    light: '💡',
    humidity: '💧',
  };
  return emojiMapping[key] || null;
};

const getUnitSymbol = (key: string) => {
  const unitMapping: Record<string, string> = {
    temperature: '°C',
    IAQ: '%',
    sound: 'dB',
    pressure: 'hPa',
    light: 'lux',
    humidity: '%',
  };
  return unitMapping[key] || '?';
};
</script>

<template>
  <div class="summary-container">

    <div class="summary-container-header">
      <h1>Summary Table</h1>

      <!-- Toggle Filter Button -->
      <button @click="toggleFilterVisibility" class="toggle-button">
        {{ showFilterBar ? "Hide Filter" : "Show Filter" }}
      </button>
    </div>
    <!-- Import Filter Bar -->
    <SummaryTableFilterBar
      v-if="showFilterBar"
      v-model:selectedAreas="selectedAreas"
      :presetData="presetData"
    />

    <div class="text-center mt-2" v-if="presetData.length == 0">
      There are no rooms available to display!
    </div>
    <div v-else-if="filteredAreas.length == 0" class="text-center mt-2">
      You have nothing selected!
    </div>
    <!-- Cards Layout -->
    <div class="summary-grid pb-3 px-1">
      <div v-for="(area, index) in filteredAreas" :key="index" class="summary-card">
        <div class="card-header" :style="{ backgroundColor: area.box?.colour, color: getTextColour(area.box?.colour) }">
          <h3>{{ area.label }}</h3>
        </div>
        <div class="card-body">

        
          <div class="pico-data">
            <div v-for="tracker in getObjectTrackers(area)" :key="tracker.key">
              <p>
                <span class="pico-data-icon">
                  <FontAwesomeIcon :icon="tracker.icon" />
                </span> 
                <span class="pico-data-value">
                  {{ tracker.name }} Count: {{ tracker.count }}
                </span>
              </p>
            </div>
          </div>
          
          <div class="environment-grid">
            <div v-for="sensor in getEnvironmentSensors(area)" :key="sensor.key" class="pico-data">
              <span class="pico-data-icon">
                <FontAwesomeIcon :icon="sensor.icon" />
              </span> 
              <span class="pico-data-value">
                {{ formatSensorName(sensor.name) }}: {{ sensor.value }}
              </span>
            </div>
          </div>

          <!-- View Graph Button -->
          <button @click="openGraph(area.label)">📊 View Graph</button>
        </div>
      </div>
    </div>

    <!-- Environment Data Modal -->
    <EnvironmentDataGraph
      v-if="showModal"
      :areaLabel="activeGraphArea"
      :showModal="showModal"
      :area-labels="presetData.map(item => item.label)"
      @close="closeGraph"
    />
  </div>
</template>

<style scoped>
/* Summary Container Layout */
.summary-container {
  display: flex;
  flex-direction: column;
  padding: 20px;
  background-color: var(--primary-light-bg);
  border-top: 1px solid #ccc;
  color: var(--primary-dark-text);
}

/* Header Styling */
.summary-container-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.toggle-button {
  background-color: var(--primary-bg);
  color: var(--primary-light-text);
  border: none;
  padding: 8px 12px;
  border-radius: 5px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.toggle-button:hover {
  background-color: var(--primary-bg-hover);
}

/* Cards Layout */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  border-radius: 10px;
  overflow: hidden;
}

/* Individual Cards */
.summary-card {
  border-radius: 10px;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
  background: var(--primary-light-bg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: auto;
  padding: 15px;
}

.card-header {
  background-color: var(--primary-dark-bg);
  color: var(--primary-light-text);
  padding: 15px;
  font-size: 16px;
  font-weight: bold;
  text-align: center;
  border-radius: 8px 8px 0 0;
}

.card-body {
  display: flex;
  flex-direction: column;
  padding: 15px;
  gap: 10px;
}

.pico-data {
  display: flex;
  flex-direction: column;
}

.pico-data p {
  display: flex;
  align-items: center;
  font-size: 14px;
  gap: 5px;
}
.pico-data-icon{
  width: 10%;
}
.pico-data-value{
  width: 100%;
  text-align: left;
}
.environment-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  width: 100%;
}

/* Button */
button {
  width: fit-content;
  align-self: flex-start;
  padding: 8px 12px;
  border: none;
  background-color: var(--primary-bg);
  color: var(--primary-light-text);
  cursor: pointer;
  border-radius: 5px;
  transition: background 0.3s;
}

button:hover {
  background-color: var(--primary-bg-hover);
}

/* Responsive Grid */
@media (max-width: 600px) {
  .summary-grid {
    grid-template-columns: repeat(1, 1fr);
  }
  .environment-grid {
    grid-template-columns: repeat(1, 1fr);
  }
}
</style>
