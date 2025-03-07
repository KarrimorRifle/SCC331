<template>
  <div class="filter-bar-container p-3">
    <div class="d-flex flex-column flex-md-row justify-content-between">
      <!-- Sensor Filters -->
      <div class="sensor-filters flex-grow-1 me-4 mx-4">
        <h5>Filter</h5>
        <div class="filter-grid">
          <div v-for="sensor in sensors" :key="sensor.name" class="filter-item">
            <FontAwesomeIcon :icon="sensor.icon" class="sensor-icon me-2" /> 
            <span class="displayName me-2">{{ sensor.displayName }}</span>
            <label class="switch">
              <input type="checkbox" v-model="sensor.checked" @change="updateFilters" />
              <span class="slider round"></span>
            </label>
          </div>
        </div>
      </div>

      <!-- State Filters -->
      <div class="state-filters flex-grow-1 me-4 mx-4">
        <h5>State Filter</h5>
        <div class="filter-grid state-grid">
          <div v-for="state in states" :key="state.name" class="filter-item">
            <span :style="{ backgroundColor: state.color }" class="state-indicator me-2"></span>
            <span class="me-2">{{ state.name }}</span>
            <label class="switch">
              <input type="checkbox" v-model="state.checked" @change="updateFilters" />
              <span class="slider round"></span>
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineEmits, watch, computed } from 'vue';
import { sensors } from "../stores/sensorTypeStore";
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

const props = defineProps({
  isMobile: Boolean
})
// Define emitted event for filter updates
const emit = defineEmits(['updateFilters']);

// Define filter states: "All" (default checked) and "Disconnected"
const states = ref([
  { name: 'All', color: 'blue', checked: true }, 
  { name: 'Disconnected', color: 'red', checked: false }
]);

// Watcher: Toggle "Disconnected" state when "All" is checked/unchecked
watch(
  () => states.value.find(s => s.name === "All").checked,
  (newVal) => {
    const disconnectedState = states.value.find(s => s.name === "Disconnected");
    if (disconnectedState.checked === newVal) {
      disconnectedState.checked = !newVal; // Prevent both being the same
    }
  }
);

// Watcher: Toggle "All" state when "Disconnected" is checked/unchecked
watch(
  () => states.value.find(s => s.name === "Disconnected").checked,
  (newVal) => {
    const allState = states.value.find(s => s.name === "All");
    if (allState.checked === newVal) {
      allState.checked = !newVal; // Prevent both being the same
    }
  }
);

// Function to emit updated filter selections
const updateFilters = () => {
  const showAll = states.value.find(state => state.name === "All")?.checked;
  const showDisconnected = states.value.find(state => state.name === "Disconnected")?.checked;

  const selectedSensors = sensors.value
    .filter(s => s.checked) 
    .map(s => s.name);

  console.log("Emitting Filters: ", { sensors: selectedSensors, showDisconnected, showAll });

  emit('updateFilters', {
    sensors: selectedSensors,
    showDisconnected,
    showAll
  });
};


</script>

<style scoped>
.filter-bar-container {
  background-color: var(--primary-light-bg);
  color: var(--primary-dark-text);
  padding: 15px;
  max-height: 30vh;
  overflow-y: auto;
  border-top: 1px solid #ccc;
}

.sensor-filters {
  border-right: 1px solid #ccc;
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr); 
  grid-auto-flow: row; /* Ensure items go in rows, not columns */
  grid-template-rows: auto;
  gap: 12px;
  margin: 0 10px;
}

.state-grid {
  grid-template-rows: auto;
  grid-auto-flow: row;
}

.filter-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px;
  background: var(--primary-light-bg);
  border-radius: 8px;
}

.displayName {
  font-weight: bold;
  white-space: nowrap;
}

.sensor-icon {
  font-size: 18px;
  color: var(--primary-dark-text);
}

.state-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

/* Toggle Switch Styling */
.switch {
  position: relative;
  display: inline-block;
  width: 34px;
  height: 20px;
}
.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}
.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.4s;
  border-radius: 20px;
}
.slider:before {
  position: absolute;
  content: "";
  height: 14px;
  width: 14px;
  left: 3px;
  bottom: 3px;
  background-color: var(--primary-light-bg);
  transition: 0.4s;
  border-radius: 50%;
}
input:checked + .slider {
  background-color: var(--active);
}
input:checked + .slider:before {
  transform: translateX(14px);
}

@media (max-width: 768px) {
  .filter-bar-container{
    margin-bottom: 77px ;
  }
  .sensor-filters{
    border: none;
  }
  .filter-grid{
    grid-template-columns: 1fr; 
  }
}


</style>
