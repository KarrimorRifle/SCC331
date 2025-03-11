<script setup lang="ts">
import { ref, defineEmits, onMounted } from "vue";

// Define emit event
const emit = defineEmits(["update:filter"]);

// Filter options
const severityLevels = ["All", "Doomed", "Danger", "Warning", "Notification"];

// Selected filter state (Default to "All")
const selectedSeverity = ref("all");

// Emit filter update when changed
const updateFilter = () => {
  emit("update:filter", selectedSeverity.value);
};

// Emit default value on mount to ensure "All" is selected initially
onMounted(() => {
  updateFilter();
});
</script>

<template>
  <div class="filter-bar">
    <label for="severity-filter">Filter by Severity:</label>
    <select id="severity-filter" v-model="selectedSeverity" @change="updateFilter">
      <option v-for="level in severityLevels" :key="level" :value="level.toLowerCase()">
        {{ level }}
      </option>
    </select>
  </div>
</template>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
  padding: 8px 12px;
  background: var(--primary-light-bg);
  border-radius: 10px;
  border: 2px solid #568EA6;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease-in-out;
  max-width: 420px;
}

/* Label Styling */
label {
  font-size: 16px;
  font-weight: bold;
  color: var(--primary-dark-text);
  white-space: nowrap;
}

/* Dropdown Styling */
select {
  flex: 1;
  padding: 10px;
  font-size: 14px;
  border: 2px solid #ccc;
  border-radius: 8px;
  outline: none;
  background: var(--primary-light-bg);
  cursor: pointer;
  transition: all 0.3s ease-in-out;
  color: var(--primary-dark-text);
  font-weight: bold;
}

</style>
