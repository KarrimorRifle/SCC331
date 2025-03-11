<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { getTextColour } from '../../../utils/helper/colorUtils';
import { usePresetStore } from '../../../utils/useFetchPresets';
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
const filteredAreas = computed(() => presetData.value.filter(area => selectedAreas.value.includes(area.label)));

watch(presetData, (newVal, oldVal) => {
  // If newVal contains rooms not in selectedAreas, add them
  newVal.forEach(area => {
    if (!selectedAreas.value.includes(area.label)) {
      selectedAreas.value.push(area.label);
    }
  });
});

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
          <!-- People Count -->
          <div class="count-container">
            <div class="marker-wrapper">
              <PersonMarker :color="'#4caf50'" :position="{ top: 0, left: 0 }" />
            </div>
            <p>People Count: {{ area.tracker?.users?.count || 0 }}</p>
          </div>

          <!-- Luggage Count -->
          <div class="count-container">
            <div class="marker-wrapper">
              <LuggageMarker :color="'#f44336'" :position="{ top: 0, left: 0 }" />
            </div>
            <p>Luggage Count: {{ area.tracker?.luggage?.count || 0 }}</p>
          </div>

          <!-- Environment Data -->
          <div class="environment-data">
            <p><span class="emoji">🌡️</span> Temperature: {{ area.tracker?.environment?.temperature ?? 'N/A' }}°C</p>
            <p><span class="emoji">🔊</span> Sound Level: {{ area.tracker?.environment?.sound ?? 'N/A' }} dB</p>
            <p><span class="emoji">💡</span> Light Level: {{ area.tracker?.environment?.light ?? 'N/A' }} lux</p>
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

/* Counters */
.count-container {
  display: flex;
  align-items: center;
  font-size: 14px;
  gap: 10px;
}

.marker-wrapper {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

/* Environment Data */
.environment-data {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.environment-data p {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 14px;
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
