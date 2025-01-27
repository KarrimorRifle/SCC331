<script setup lang="ts">
import LuggageMarker from './ObjectMarker/LuggageMarker.vue';
import PersonMarker from './ObjectMarker/PersonMarker.vue';

const props = defineProps({
  overlayAreas: {
    type: Array,
    required: true,
  },
});

const getTextColor = (color: string): string => {
  const hex = color.replace('#', '');
  const r = parseInt(hex.slice(0, 2), 16);
  const g = parseInt(hex.slice(2, 4), 16);
  const b = parseInt(hex.slice(4, 6), 16);
  const brightness = (r * 299 + g * 587 + b * 114) / 1000;
  return brightness < 128 ? 'white' : 'black';
};
</script>

<template>
  <div class="dashboard">
    <h2>Dashboard</h2>
    <div 
      v-for="(area, index) in props.overlayAreas" 
      :key="index" 
      class="dashboard-area"
      :style="{ backgroundColor: area.color, color: getTextColor(area.color) }"
    >
      <h3>{{ area.label }}</h3>
      
      <div class="count-container">
        <div class="marker-container">
          <LuggageMarker :color="'#f44336'" :position="{ top: 5, left: 0 }" />
        </div>
        <p>Luggage Count: {{ area.luggage?.length || 0 }}</p>
      </div>
      
      <div class="count-container">
        <div class="marker-container">
          <PersonMarker :color="'#4caf50'" :position="{ top: 5, left: 0 }" />
        </div>
        <p>People Count: {{ area.people?.length || 0 }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  width: 300px;
  padding: 20px;
  background-color: #f8f8ff;
  border-left: 1px solid #ccc;
  overflow-y: auto;
  box-shadow: -4px 0 8px rgba(0, 0, 0, 0.1);
  color: black;
  font-weight: bold;
}

.dashboard-area {
  margin-bottom: 20px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.dashboard-area h3 {
  margin: 0;
  font-size: 18px;
  font-weight: bold;
  text-decoration: underline;
}

.count-container {
  display: flex;
  align-items: center;
  margin: 5px 0;
}

.marker-container {
  position: relative; /* Keeps the marker absolutely positioned within the container */
  width: 20px; /* Matches marker size */
  height: 20px;
  margin-right: 8px;
}

.dashboard-area p {
  margin: 0;
  font-size: 14px;
}
</style>
