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

// Handle individual checkbox change (emits automatically via watch)
</script>

<template>
  <div class="filter-bar">
    <label>Filter by Area:</label>
    <div class="checkbox-group">
      <label>
        <input type="checkbox" @change="toggleAllAreas" :checked="selectedAreas.length === overlayAreasConstant.length">
        All
      </label>
      <label v-for="area in overlayAreasConstant" :key="area.label">
        <input type="checkbox" v-model="selectedAreas" :value="area.label">
        {{ area.label }}
      </label>
    </div>
  </div>
</template>

<style scoped>
/* Filter Bar */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 15px;
  justify-content: flex-start;
  background: white;
  padding: 20px;
  margin: 20px 0px;
  border-radius: 8px;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
  color: black;
  overflow: hidden;
}

/* Checkbox group */
.checkbox-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  cursor: pointer;
  font-weight: bold;
}

/* Checkbox Styling */
input[type="checkbox"] {
  cursor: pointer;
  width: 16px;
  height: 16px;
  margin-right: 10px;
  accent-color: #F18C8E;
}
</style>
