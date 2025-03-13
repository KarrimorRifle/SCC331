<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import axios from 'axios';
import { getTextColour } from '../../../utils/helper/colorUtils';
import SummaryTableFilterBar from "./SummaryTableFilterBar.vue";
import { usePresetStore } from '../../../utils/useFetchPresets';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import EnvironmentDataGraph from '../EnvironmentDataGraph.vue';
import { 
  faUser, faClipboardCheck, faShieldAlt, faSuitcase, 
  faVolumeUp, faArrowDown, faLightbulb, faTint, faQuestion 
} from '@fortawesome/free-solid-svg-icons';


// ----------------------------
// Preset Data & Filtering
// ----------------------------
// Retain room IDs as keys
const presetStore = usePresetStore();
const presetData = computed(() =>
  Object.entries(presetStore.boxes_and_data).reduce((acc, [roomID, area]) => {
    acc[roomID] = {
      ...area,
      tracker: area.tracker || {} // Ensure "tracker" key exists
    };
    return acc;
  }, {} as Record<string, any>)
);
console.log(presetStore.boxes_and_data)
// Multi-selection state (stores selected area labels)
const selectedAreas = ref<string[]>([]);

// ----------------------------
// Summary Fetching
// ----------------------------
const summary = ref<Record<string, any>>({});

// Fetch summary from the API.
const fetchSummary = async () => {
  try {
    const response = await axios.get('/api/reader/summary', { withCredentials: true });
    summary.value = response.data;
  } catch (error) {
    console.error("Failed to fetch summary", error);
  }
};

// ----------------------------
// Merge Preset Data & Summary
// ----------------------------
// For each roomID in presetData, merge in the summary data (which uses the same roomID keys).
// If no summary exists for a room, default to an empty object.
const mergedData = computed(() => {
  return Object.entries(presetData.value).map(([roomID, area]) => {
    return {
      roomID,
      ...area,
      summary: summary.value[roomID] || { environment: {} }
    };
  });
});

const filteredAreas = computed(() => {
  return mergedData.value.filter(area => selectedAreas.value.includes(area.roomID));
});

const getFilteredSensors = (tracker: Record<string, any>) => {
  return Object.entries(tracker).filter(([key]) => key !== "environment");
};

// ----------------------------
// Modal / Graph State (Optional)
// ----------------------------
const activeGraphArea = ref<string | null>(null);
const showModal = ref(false);
const showFilterBar = ref(true);
const toggleFilterVisibility = () => {
  showFilterBar.value = !showFilterBar.value;
};
const openGraph = async (areaLabel: string) => {
  activeGraphArea.value = areaLabel;
  showModal.value = true;
};
const closeGraph = () => {
  showModal.value = false;
};

// Add helper function to return icon mapping based on type using imported icons
const getIcon = (type: string) => {
  if (!type) return faQuestion; // Default icon if undefined

  const iconMapping: Record<string, any> = {
    guard: faShieldAlt,
    luggage: faSuitcase,
    users: faUser,
    staff: faClipboardCheck,
    temperature: faArrowDown,
    IAQ: faClipboardCheck,
    sound: faVolumeUp,
    pressure: faArrowDown,
    light: faLightbulb,
    humidity: faTint,
  };

  return iconMapping[type.toLowerCase()] || faQuestion; // Return valid icon or default
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

const formatSensorName = (name: string): string => {
  const formattedName = name.replace(/\s*Sensor\s*/i, '').trim();
  return formattedName.length > 4 ? formattedName.slice(0, 4) : formattedName;
};

// ----------------------------
// On Mounted
// ----------------------------
onMounted(async () => {
  // Fetch the summary data.
  await fetchSummary();
  // Preselect all area labels from presetData.
  selectedAreas.value = Object.values(presetData.value).map((area: any) => area.label);
  console.log("Fetched Summary:", summary.value);
  console.log("Merged Data:", mergedData.value);
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
    
    <!-- Filter Bar (optional) -->
    <!--
    <SummaryTableFilterBar
      v-if="showFilterBar"
      v-model:selectedAreas="selectedAreas"
      :presetData="presetData"
    />
    -->

    <!-- Show message if no rooms are available -->
    <div v-if="mergedData.length === 0" class="text-center mt-2">
      There are no rooms available to display!
    </div>

    <!-- Display Merged Summary Cards -->
    <div class="summary-grid pb-3 px-1">
      <div v-for="(area, index) in mergedData" :key="area.roomID" class="summary-card">
        <div class="card-header" :style="{ backgroundColor: area.box?.colour, color: getTextColour(area.box?.colour) }">
          <h3>{{ area.label }}</h3>
        </div>
        <div class="card-body">

          <!-- Display Other Sensors -->
          <div class="object-grid">
            <div v-for="([sensorKey, sensorData]) in getFilteredSensors(area.tracker)" :key="sensorKey" class="pico-data">
              <span class="pico-data-icon">
                <FontAwesomeIcon :icon="getIcon(sensorKey)" />
              </span> 
              <span class="pico-data-value">
                {{ sensorKey }}: {{ sensorData.count }}
              </span>
            </div>
          </div>


          <div class="environment-grid">
            <div v-for="(value, key) in area.tracker.environment" :key="key" class="pico-data">
              <span class="pico-data-icon">
                <FontAwesomeIcon :icon="getIcon(key)" />
              </span> 
              <span class="pico-data-value">
                {{ formatSensorName(key) }}: {{ value }}
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
      :area-labels="Object.values(presetData).map(item => item.label)"
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
  grid-template-columns: repeat(2, 1fr);
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
  flex-direction: row;
  justify-content: space-between;
  gap: 20px;
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
.object-grid {
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
