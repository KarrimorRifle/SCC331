<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps({
  overlayAreasConstant: {
    type: Array,
    required: true,
  },
});

const emit = defineEmits(["update:selectedAreas"]);

// Multi-selection state (stores selected areas) - Select all by default
const selectedAreas = ref(props.overlayAreasConstant.map(area => area.label));

// Watch for changes and emit updates
watch(selectedAreas, (newValue) => {
  emit("update:selectedAreas", newValue);
});

// Handle Select All functionality
const toggleAllAreas = () => {
  if (selectedAreas.value.length === props.overlayAreasConstant.length) {
    selectedAreas.value = []; // Deselect all
  } else {
    selectedAreas.value = props.overlayAreasConstant.map(area => area.label); // Select all
  }
};
</script>

<template>
  <div class="filter-bar">
    <h2>Filter by Area</h2>

    <!-- Select All Checkbox -->
    <div class="checkbox-group">
      <input type="checkbox" id="select-all" @change="toggleAllAreas" :checked="selectedAreas.length === overlayAreasConstant.length" />
      <label for="select-all">Select All</label>
    </div>

    <div class="divider"></div>

    <!-- Individual Checkboxes -->
    <div class="area-list">
      <div v-for="area in overlayAreasConstant" :key="area.label" class="checkbox-group">
        <input type="checkbox" :id="area.label" v-model="selectedAreas" :value="area.label" />
        <label :for="area.label">{{ area.label }}</label>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Container Styling */
.filter-bar {
  padding: 20px;
  margin: 20px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Title */
.filter-bar h2 {
  font-size: 18px;
  color: #305F72;
  margin-bottom: 10px;
}

/* Divider */
.divider {
  height: 1px;
  background-color: #ddd;
  margin: 10px 0;
}

/* Checkbox Groups */
.checkbox-group {
  display: flex;
  align-items: center;
  padding: 8px;
  border-radius: 6px;
  transition: background 0.3s ease-in-out;
}

.checkbox-group:hover {
  background: #f1f1f1;
}

/* Checkbox Inputs */
.checkbox-group input {
  margin-right: 10px;
  accent-color: #F18C8E; /* Match color theme */
}

/* Checkbox Labels */
.checkbox-group label {
  font-size: 14px;
  color: #444;
  cursor: pointer;
  font-weight: bold;
}

/* Area List */
.area-list {
  max-height: 200px;
  overflow-y: auto;
  padding-right: 5px;
}
</style>
