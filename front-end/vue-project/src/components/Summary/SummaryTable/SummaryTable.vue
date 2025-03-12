<script setup lang="ts">
import { ref, computed } from 'vue';
import { getTextColour } from '../../../utils/helper/colorUtils';
import { usePresetStore } from '../../../utils/useFetchPresets';
import { sensors, sensorMapping } from '../../../stores/sensorTypeStore';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import PersonMarker from '../../ObjectMarker/PersonMarker.vue';
import LuggageMarker from '../../ObjectMarker/LuggageMarker.vue';
import EnvironmentDataGraph from '../EnvironmentDataGraph.vue';
import SummaryTableFilterBar from "./SummaryTableFilterBar.vue";

const props = defineProps({
  data: {
    type: Object,
    required: true,
  },
  environmentHistory: {
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
const selectedEnvironmentData = ref({});

const toggleFilterVisibility = () => {
  showFilterBar.value = !showFilterBar.value;
};

// Toggle modal for environment graph
const openGraph = (areaLabel) => {
  const selectedArea = presetData.value?.find(area => area.label === areaLabel);

  if (selectedArea) {
    selectedEnvironmentData.value = selectedArea.tracker.environment;
  } else {
    selectedEnvironmentData.value = {}; 
  }
  activeGraphArea.value = areaLabel;
  showModal.value = true;
};

const closeGraph = () => {
  showModal.value = false;
};

// Computed property for filtered areas
const filteredAreas = computed(() => {
  if (selectedAreas.value.length === 0) return presetData.value;
  return presetData.value.filter(area => selectedAreas.value.includes(area.label));
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
      :presetData="presetData" 
      @update:selectedAreas="selectedAreas = $event"
    />

    <!-- Cards Layout -->
    <div class="summary-grid">
      <div v-for="(area, index) in filteredAreas" :key="index" class="summary-card">
        <div class="card-header" :style="{ backgroundColor: area.box?.colour, color: getTextColour(area.box?.colour) }">
          <h3>{{ area.label }}</h3>
        </div>
        <div class="card-body">

          <div class="pico-data">
            <div v-for="tracker in getObjectTrackers(area)" :key="tracker.key">
              <p>
                <span class="emoji">
                  <FontAwesomeIcon :icon="tracker.icon" />
                </span> 
                <span class="pico-data-value">
                  {{ tracker.name }} Count: {{ tracker.count }}
                </span>
              </p>
            </div>
          </div>
          
          <div class="pico-data">
            <div v-for="sensor in getEnvironmentSensors(area)" :key="sensor.key">
              <p>
                <span class="emoji">
                  <FontAwesomeIcon :icon="sensor.icon" />
                </span> 
                <span class="pico-data-value">
                  {{ sensor.name }}: {{ sensor.value }}
                </span>
              </p>
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
      :environmentData="selectedEnvironmentData"
      :showModal="showModal"
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
  justify-content: space-between;
  font-size: 14px;
}

.pico-data-value{
  width: 80%;
  text-align: left;
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
}
</style>
