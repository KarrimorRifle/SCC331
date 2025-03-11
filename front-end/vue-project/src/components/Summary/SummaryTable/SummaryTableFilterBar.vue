<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps({
  presetData: {
    type: Array,
    required: true,
  },
});

const emit = defineEmits(["update:selectedAreas"]);

// Multi-selection state (stores selected areas) - Select all by default
const selectedAreas = ref(props.presetData.map(area => area.label));

// Watch for changes and emit updates
watch(selectedAreas, (newValue) => {
  emit("update:selectedAreas", newValue);
});

// Handle Select All functionality
const toggleAllAreas = () => {
  if (selectedAreas.value.length === props.presetData.length) {
    selectedAreas.value = []; // Deselect all
  } else {
    selectedAreas.value = props.presetData.map(area => area.label); // Select all
  }
};
</script>

<template>
  <div class="filter-bar">
    <h2>Filter by Area</h2>

    <!-- Select All Checkbox -->
    <div class="checkbox-group">
      <input type="checkbox" id="select-all" @change="toggleAllAreas" :checked="selectedAreas.length === presetData.length" />
      <label for="select-all">Select All</label>
    </div>

    <div class="divider"></div>

    <!-- Individual Checkboxes -->
    <div class="area-list">
      <div v-for="area in presetData" :key="area.label" class="checkbox-group">
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
  background: var(--primary-light-bg);
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Title */
.filter-bar h2 {
  font-size: 18px;
  color: var(--primary-dark-text);
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

/* Checkbox Inputs */
.checkbox-group input {
  margin-right: 10px;
  accent-color: var(--active); /* Match color theme */
}

/* Checkbox Labels */
.checkbox-group label {
  font-size: 14px;
  color: var(--primary-dark-text);
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
