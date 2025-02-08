<script setup lang="ts">
import { PropType, computed } from "vue";

// Define props
const props = defineProps({
  warnings: {
    type: Array as PropType<{ Title: string; Location: string; Severity: string; Summary: string }[]>,
    required: true,
  },
});

// Map severity levels to colors
const severityColors: Record<string, string> = {
  doomed: "#FF0000",
  danger: "#FF4500",
  warning: "#FFA500",
  notification: "#4682B4",
};
</script>

<template>
  <div class="warnings-container">
    <h2>⚠️ Warning System</h2>

    <div v-if="props.warnings.length === 0" class="no-warnings">
      ✅ No active warnings.
    </div>

    <ul v-else>
      <li v-for="(warning, index) in props.warnings" :key="index" class="warning-card" :style="{ borderColor: severityColors[warning.Severity] }">
        <h3 :style="{ backgroundColor: severityColors[warning.Severity] }">
          {{ warning.Title }}
        </h3>
        <p><strong>Location:</strong> Room {{ warning.Location }}</p>
        <p><strong>Severity:</strong> {{ warning.Severity.toUpperCase() }}</p>
        <p class="summary"><strong>Summary:</strong> {{ warning.Summary }}</p>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.warnings-container {
  padding: 20px;
  background-color: #f8f8ff;
  border-top: 1px solid #ccc;
  color: black;
}

.loading, .error, .no-warnings {
  font-size: 16px;
  text-align: center;
  margin: 10px 0;
}

.warning-card {
  border-left: 6px solid;
  padding: 15px;
  margin-bottom: 15px;
  background: white;
  border-radius: 5px;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
}

.warning-card h3 {
  margin: 0;
  padding: 10px;
  color: white;
  font-size: 18px;
  border-radius: 5px 5px 0 0;
}

.summary {
  margin-top: 5px;
  font-size: 14px;
  color: #333;
}
</style>
