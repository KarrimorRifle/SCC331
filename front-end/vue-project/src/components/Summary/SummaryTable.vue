<script setup lang="ts">
import { ref, computed } from 'vue';
import PersonMarker from '../ObjectMarker/PersonMarker.vue';
import LuggageMarker from '../ObjectMarker/LuggageMarker.vue';
import EnvironmentDataGraph from './EnvironmentDataGraph.vue';

const props = defineProps({
  data: {
    type: Array,
    required: true,
  },
  overlayAreasConstant: {
    type: Array,
    required: true,
  },
  environmentHistory: {
    type: Object,
    required: true,
  },
});
console.log(props.environmentHistory);
// Track active graph area and modal state
const activeGraphArea = ref(null);
const showModal = ref(false);

// Toggle modal for environment graph
const openGraph = (areaLabel) => {
  activeGraphArea.value = areaLabel;
  showModal.value = true;
};

const closeGraph = () => {
  showModal.value = false;
};

const getAreaKey = (label: string): string | null => {
  const match = label.match(/\d+/);
  return match ? match[0] : null;
};

</script>

<template>
  <div class="summary-table">
    <table>
      <thead>
        <tr>
          <th>Area</th>
          <th>
            <div class="header-container">
              <div class="marker-wrapper">
                <PersonMarker :color="'#4caf50'" :position="{ top: 5, left: 0 }" />
              </div>
              People Count
            </div>
          </th>
          <th>
            <div class="header-container">
              <div class="marker-wrapper">
                <LuggageMarker :color="'#f44336'" :position="{ top: 5, left: 0 }" />
              </div>
              Luggage Count
            </div>
          </th>
          <th>🌡️ Temp (°C)</th>
          <th>🔊 Sound (dB)</th>
          <th>💡 Light (lux)</th>
          <th>📊 Graph</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(area, index) in props.overlayAreasConstant" :key="index">
          <td>{{ area.label }}</td>
          <td>{{ props.data[getAreaKey(area.label)]?.users?.count || 0 }}</td>
          <td>{{ props.data[getAreaKey(area.label)]?.luggage?.count || 0 }}</td>
          <td>{{ props.data[getAreaKey(area.label)]?.environment?.temperature  ?? 'N/A' }}</td>
          <td>{{ props.data[getAreaKey(area.label)]?.environment?.sound ?? 'N/A' }}</td>
          <td>{{ props.data[getAreaKey(area.label)]?.environment?.light ?? 'N/A' }}</td>
          <td>
            <button @click="openGraph(getAreaKey(area.label))">📊 View Graph</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Environment Data Modal -->
    <EnvironmentDataGraph
      v-if="showModal"
      :areaLabel="activeGraphArea"
      :environmentData="environmentHistory[activeGraphArea] || []"
      :showModal="showModal"
      @close="closeGraph"
    />
  </div>
</template>

<style scoped>
.summary-table {
  padding: 20px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

th, td {
  padding: 10px;
  border: 1px solid #ccc;
  text-align: center;
}

th {
  background-color: #568ea6;
  color: white;
}

td {
  background-color: #f8f8ff;
  color: #333;
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative; /* Ensure markers stay positioned relative to this container */
}

.marker-wrapper {
  position: relative; /* Contains the absolutely positioned markers */
  width: 20px;
  height: 20px;
}

button {
  padding: 5px 10px;
  border: none;
  background-color: #568ea6;
  color: white;
  cursor: pointer;
  border-radius: 5px;
}

button:hover {
  background-color: #305f72;
}
</style>
