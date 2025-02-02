<script setup lang="ts">
import { computed } from 'vue';
import LuggageMarker from './ObjectMarker/LuggageMarker.vue';
import PersonMarker from './ObjectMarker/PersonMarker.vue';

const props = defineProps({
  overlayAreasConstant: {
    type: Array,
    required: true,
  },
  overlayAreasData: {
    type: Object,
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

const getAreaKey = (label: string): string | null => {
  const match = label.match(/\d+/);
  return match ? match[0] : null;
};

</script>

<template>
  <div class="dashboard">
    <h2>Dashboard</h2>
    <div 
      v-for="(area, index) in props.overlayAreasConstant" 
      :key="index" 
      class="dashboard-area"
      :style="{ backgroundColor: area.color, color: getTextColor(area.color) }"
    >
      <h3>{{ area.label }}</h3>

      <!-- Luggage Count -->
      <div class="count-container">
        <div class="marker-container">
          <LuggageMarker :color="'#f44336'" :position="{ top: 0, left: 0 }" />
        </div>
        <p>Luggage Count: {{ props.overlayAreasData[getAreaKey(area.label)]?.luggage?.count || 0 }}</p>
      </div>
      
      <!-- People Count -->
      <div class="count-container">
        <div class="marker-container">
          <PersonMarker :color="'#4caf50'" :position="{ top: 0, left: 0 }" />
        </div>
        <p>People Count: {{ props.overlayAreasData[getAreaKey(area.label)]?.users?.count || 0 }}</p>
      </div>

      <!-- Environment Data -->
      <div class="environment-container">
        <h4>Environment Data:</h4>
        <p>🌡️ Temperature: {{ props.overlayAreasData[getAreaKey(area.label)]?.environment?.temperature || 'N/A' }}°C</p>
        <p>🔊 Sound Level: {{ props.overlayAreasData[getAreaKey(area.label)]?.environment?.sound || 'N/A' }} dB</p>
        <p>💡 Light Level: {{ props.overlayAreasData[getAreaKey(area.label)]?.environment?.light || 'N/A' }} lux</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  width: 300px;
  padding: 20px;
  background-color: #f8f8ff;
  max-height: 90vh;
  overflow-y: auto;
  color: black;
  font-weight: bold;
}

.dashboard-area {
  margin-bottom: 20px;
  padding: 10px;
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
  position: relative;
  width: 20px;
  height: 20px;
  margin-right: 8px;
}

.environment-container {
  margin-top: 10px;
  padding: 8px;
  border-radius: 5px;
  background-color: rgba(255, 255, 255, 0.2);
}

.environment-container h4 {
  margin-bottom: 5px;
  font-size: 14px;
  text-decoration: underline;
}

.environment-container p {
  margin: 3px 0;
  font-size: 12px;
}
</style>
