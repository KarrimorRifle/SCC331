<template>
  <div class="filter-bar-container p-3">
    <div class="d-flex justify-content-between">
      <!-- Sensor Filters -->
      <div class="sensor-filters flex-grow-1 me-4 mx-4">
        <h5>Filter</h5>
        <div class="filter-grid">
          <div v-for="sensor in sensors" :key="sensor.name" class="filter-item">
            <font-awesome-icon :icon="sensor.icon" class="sensor-icon me-2" />
            <span class="me-2">{{ sensor.name }}</span>
            <label class="switch">
              <input type="checkbox" v-model="sensor.checked" @change="updateFilters" />
              <span class="slider round"></span>
            </label>
          </div>
        </div>
      </div>

      <!-- State Filters -->
      <div class="state-filters flex-grow-1">
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
import { ref, defineEmits } from 'vue';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faTemperatureLow, faSnowflake, faDoorOpen, faEye, faFire, faThermometerHalf, faTrash, faTint, faUsers, faRecycle } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

library.add(faTemperatureLow, faSnowflake, faDoorOpen, faEye, faFire, faThermometerHalf, faTrash, faTint, faUsers, faRecycle);

const emit = defineEmits(['updateFilters']);

const sensors = ref([
  { name: 'Smart Shelf', icon: 'temperature-low', checked: true },
  { name: 'Freezer', icon: 'snowflake', checked: true },
  { name: 'Door Sensor', icon: 'door-open', checked: true },
  { name: 'Motion Sensor', icon: 'eye', checked: true },
  { name: 'Smoke Sensor', icon: 'fire', checked: true },
  { name: 'Chiller', icon: 'thermometer-half', checked: true },
  { name: 'Smart Bin', icon: 'recycle', checked: true },
  { name: 'Liquid Level Sensor', icon: 'tint', checked: true },
  { name: 'Occupancy Sensor', icon: 'users', checked: true }
]);

const states = ref([
  { name: 'Normal', color: 'green', checked: true },
  { name: 'Major', color: 'yellow', checked: true },
  { name: 'Critical', color: 'red', checked: true },
  { name: 'Disconnected', color: 'gray', checked: true }
]);

const updateFilters = () => {
  emit('updateFilters', { sensors: sensors.value, states: states.value });
};
</script>

<style scoped>
.filter-bar-container {
  background-color: #fff;
  color: black;
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
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  grid-auto-flow: column;
  grid-template-rows: repeat(5, auto);
  gap: 12px;
  margin: 0 10px;
}

.state-grid {
  grid-template-rows: repeat(5, auto);
}

.filter-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px;
  background: #f9f9f9;
  border-radius: 8px;
}

.sensor-icon {
  font-size: 18px;
  color: #333;
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
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}
input:checked + .slider {
  background-color: #ffa726;
}
input:checked + .slider:before {
  transform: translateX(14px);
}
</style>
