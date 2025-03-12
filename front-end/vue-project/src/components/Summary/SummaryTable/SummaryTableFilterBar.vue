<script setup lang="ts">
import { watch } from 'vue';

const props = defineProps({
  presetData: {
    type: Array,
    required: true,
  },
  selectedAreas: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["update:selectedAreas"]);

// Watch for presetData changes and sync selectedAreas
watch(() => props.presetData, (newVal) => {
  // Sync selectedAreas with newly available data while preserving existing selections
  const newLabels = newVal.map(area => area.label);
  const filtered = props.selectedAreas.filter(label => newLabels.includes(label));
  emit("update:selectedAreas", filtered);
});

// Handle Select All functionality
const toggleAllAreas = () => {
  if (props.selectedAreas.length === props.presetData.length) {
    emit("update:selectedAreas", []); // Deselect all
  } else {
    emit("update:selectedAreas", props.presetData.map(area => area.label)); // Select all
  }
};

const toggleArea = (areaLabel: string) => {
  const updated = props.selectedAreas.includes(areaLabel)
    ? props.selectedAreas.filter(a => a !== areaLabel)
    : [...props.selectedAreas, areaLabel];
  emit("update:selectedAreas", updated);
};
</script>

<template>
  <div class="filter-bar">
    <h2>Filter by Area</h2>
    <!-- Individual Checkboxes -->
    <div class="area-list">
      <button type="button" class="btn" @click="toggleAllAreas" :class="{ 'btn-primary': selectedAreas.length === presetData.length, 'btn-outline-primary': selectedAreas.length != presetData.length }">
        All
      </button>
      <div v-for="area in presetData" :key="area.label" class="checkbox-group d-inline-block">
        <button type="button" class="btn" :class="{ 'btn-secondary': selectedAreas.includes(area.label), 'btn-outline-secondary': !selectedAreas.includes(area.label) }" @click="toggleArea(area.label)">
          {{ area.label }}
        </button>
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
