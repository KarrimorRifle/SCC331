<script setup lang="ts">
import { PropType, computed, ref } from "vue";
import { getCardBackgroundColor } from "@/utils/helper/warningUtils";
import WarningSystemFilterBar from "./WarningSystemFilterBar.vue"; // Import filter bar

// Define props
const props = defineProps({
  warnings: {
    type: Array as PropType<{ Title: string; Location: string; Severity: string; Summary: string }[]>,
    required: true,
  },
  overlayAreasConstant: {
    type: Array as PropType<{ label: string; color: string; position: object }[]>,
    required: true,
  },
});

// **Reactive filter state**
const selectedSeverity = ref("all");

// **Filter warnings based on selected severity**
const filteredWarnings = computed(() => {
  if (selectedSeverity.value === "all") {
    return props.warnings;
  }
  return props.warnings.filter((warning) => warning.Severity.toLowerCase() === selectedSeverity.value);
});

// **Ensure all areas are displayed, even if they have no warnings**
const groupedWarnings = computed(() => {
  const grouped: Record<string, typeof props.warnings> = {};

  // Initialize all areas with empty arrays
  props.overlayAreasConstant.forEach((area) => {
    grouped[area.label] = [];
  });

  // Populate warnings where applicable
  filteredWarnings.value.forEach((warning) => {
    if (!grouped[warning.Location]) {
      grouped[warning.Location] = [];
    }
    grouped[warning.Location].push(warning);
  });

  return grouped;
});

// **Get Area Color Based on overlayAreasConstant**
const getAreaColor = (location: string): string => {
  const area = props.overlayAreasConstant.find(area => area.label === location);
  return area ? area.color : "#ccc"; // Default gray if not found
};

// **Handle Filter Update**
const updateFilter = (severity: string) => {
  selectedSeverity.value = severity;
};
</script>

<template>
  <div class="warnings-container">
    <!-- Header & Filter Bar in Flexbox -->
    <div class="header-container">
      <h2>⚠️ Warning System</h2>
      <WarningSystemFilterBar @update:filter="updateFilter" />
    </div>

    <div v-if="props.overlayAreasConstant.length === 0" class="no-warnings">
      ✅ No active areas available.
    </div>

    <div class="grid-container">
      <!-- Loop through all areas, ensuring they appear even if no warnings -->
      <div v-for="(warnings, area) in groupedWarnings" :key="area" class="area-group">
        <h3 class="area-title" :style="{ backgroundColor: getAreaColor(area), color: 'white' }">
          {{ area }}
        </h3>

        <!-- Grid Layout for Warnings -->
        <div class="warning-grid">
          <div 
            v-for="(warning, index) in warnings" 
            :key="index" 
            class="warning-card" 
            :style="{ backgroundColor: getCardBackgroundColor(warning.Severity), borderColor: getAreaColor(warning.Location) }"
          >
            <h3 :style="{ backgroundColor: getCardBackgroundColor(warning.Severity) }">
              {{ warning.Title }}
            </h3>
            <p><strong>Severity:</strong> {{ warning.Severity.toUpperCase() }}</p>
            <p class="summary"><strong>Summary:</strong> {{ warning.Summary }}</p>
          </div>

          <!-- Show "No Warnings" message if no warnings in this area -->
          <div v-if="warnings.length === 0" class="no-warnings-card">
            ✅ No active warnings in this area.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.warnings-container {
  padding: 20px;
  background-color: #f8f8ff;
  border-top: 1px solid #ccc;
  color: black;
}

/* Header & Filter Bar Flexbox */
.header-container {
  display: flex;
  justify-content: space-between;
  width: 100%;
  align-items: center;
  flex-wrap: wrap; 
  gap: 15px;
  padding-bottom: 10px;
}

/* No warnings message */
.loading, .error, .no-warnings {
  font-size: 16px;
  text-align: center;
  margin: 10px 0;
}

/* Grid Layout for 3 Areas per Row */
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); /* Responsive grid */
  gap: 20px;
}

/* Area Group Styling */
.area-group {
  padding: 15px;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  border: 2px solid #568EA6;
}

/* Area Title */
.area-title {
  color: white;
  margin-bottom: 10px;
  padding: 10px;
  border-radius: 5px;
  text-align: center;
}

/* Grid for Warnings */
.warning-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); /* Responsive */
  gap: 15px;
}

/* Individual Warning Cards */
.warning-card {
  padding: 15px;
  background: white;
  border-radius: 5px;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  color: white; /* Text contrast for colored backgrounds */
}

/* Warning Title */
.warning-card h3 {
  margin: 0;
  color: white;
  font-size: 18px;
  font-weight: bold;
  border-radius: 5px 5px 0 0;
}

/* "No Warnings in this Area" Placeholder */
.no-warnings-card {
  padding: 10px;
  text-align: center;
  font-size: 14px;
  color: #666;
  background: #e8e8e8;
  border-radius: 5px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .grid-container {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); /* Adjust for mobile */
  }

  .header-container {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
