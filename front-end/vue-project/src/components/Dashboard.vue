<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faExpand, faCompress } from '@fortawesome/free-solid-svg-icons';
import { updateTabHeight } from '@/utils/helper/domUtils';
import LuggageMarker from './ObjectMarker/LuggageMarker.vue';
import PersonMarker from './ObjectMarker/PersonMarker.vue';
import LiveUpdates from './Summary/LiveUpdates/LiveUpdates.vue';

const props = defineProps({
  overlayAreasConstant: {
    type: Array,
    required: true,
  },
  overlayAreasData: {
    type: Object,
    required: true,
  },
  userIds: {
    type: Array,
    required: true,
  },
  updates: {
    type: Object,
    required: true,
  }
});

// Dashboard state
const isExpanded = ref(false);
const bottomTabHeight = ref(0);

const toggleDashboard = () => {
  isExpanded.value = !isExpanded.value;
};

// Helper functions remain unchanged
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

const getUpdatesForArea = (area) => {
  const areaKey = getAreaKey(area.label);
  if (!areaKey) return {};

  // Filter updates to only include users in this specific area
  const filteredUpdates: Record<number, { logged_at: string; roomID: number }[]> = {};

  Object.entries(props.updates).forEach(([userId, userUpdates]) => {
    const relevantUpdates = userUpdates.filter(update => update.roomID.toString() === areaKey);
    if (relevantUpdates.length) {
      filteredUpdates[Number(userId)] = relevantUpdates;
    }
  });

  return filteredUpdates;
};

onMounted(() => {
  updateTabHeight('.tab-bar', bottomTabHeight);
  window.addEventListener('resize', updateTabHeight);
});

// Cleanup event listener
onUnmounted(() => {
  window.removeEventListener('resize', () => updateTabHeight('.tab-bar', bottomTabHeight));
});
</script>

<template>
  <div 
    class="dashboard" 
    :class="{ expanded: isExpanded }"
    :style="{ 
      maxHeight: `calc(100vh - ${bottomTabHeight + 65}px)`,
      minHeight: `calc(100vh - ${bottomTabHeight + 65}px)`
    }"
  >
    <!-- Dashboard Header -->
    <div class="dashboard-header">
      <h2 v-if="!isExpanded">Dashboard</h2>
      <h2 v-else>Detailed Dashboard</h2>

      <button class="expand-btn" @click="toggleDashboard">
        <font-awesome-icon :icon="isExpanded ? faCompress : faExpand" />
      </button>
    </div>

    <!-- Dashboard Areas -->
    <div class="dashboard-areas">
      <div 
        v-for="(area, index) in overlayAreasConstant" 
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
          <p>Luggage Count: {{ overlayAreasData[getAreaKey(area.label)]?.luggage?.count || 0 }}</p>
        </div>

        <!-- People Count -->
        <div class="count-container">
          <div class="marker-container">
            <PersonMarker :color="'#4caf50'" :position="{ top: 0, left: 0 }" />
          </div>
          <p>People Count: {{ overlayAreasData[getAreaKey(area.label)]?.users?.count || 0 }}</p>
        </div>

        <!-- Environment Data (Expanded View Only) -->
        <div v-if="isExpanded" class="environment-container">
          <h4>Environment Data:</h4>
          <table style="width: 100%;">
            <tbody>
            <tr>
              <th class="emoji-column">🌡️</th>
              <th class="data-column">{{ overlayAreasData[getAreaKey(area.label)]?.environment?.temperature || '--' }} °C</th>
              <th class="emoji-column">🌬️</th>
              <th class="data-column">{{ overlayAreasData[getAreaKey(area.label)]?.environment?.IAQ || '--' }} %</th>
            </tr>
            <tr>
              <th class="emoji-column">🔊</th>
              <th class="data-column">{{ overlayAreasData[getAreaKey(area.label)]?.environment?.sound || '--' }} dB</th>
              <th class="emoji-column">🌡️</th>
              <th class="data-column">{{ overlayAreasData[getAreaKey(area.label)]?.environment?.pressure || '--' }} hPa</th>
            </tr>
            <tr>
              <th class="emoji-column">💡</th>
              <th class="data-column">{{ overlayAreasData[getAreaKey(area.label)]?.environment?.light || '--' }} lux</th>
              <th class="emoji-column">💧</th>
              <th class="data-column">{{ overlayAreasData[getAreaKey(area.label)]?.environment?.humidity || '--' }} %</th>
            </tr>
            </tbody>
          </table>
        </div>

        <!-- Live Updates for Each Area (Expanded View Only) -->
        <div v-if="isExpanded" class="live-updates-section">
          <LiveUpdates 
            :userIds="userIds" 
            :updates="getUpdatesForArea(area)" 
            :fullUpdates="updates"
            :overlayAreasConstant="overlayAreasConstant"
            :areaShown="[area]" 
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Default Dashboard */
.dashboard {
  display: flex;
  flex-direction: column;
  padding: 20px;
  background-color: #f8f8ff;
  border-left: 1px solid #ccc;
  overflow-y: auto;
  transition: all 0.8s ease-in-out;
  position: relative;
  flex: 0.2;
}

.dashboard-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  margin: 20px 0;
}

.expand-btn {
  background-color: #305f72;
  color: white;
  border: none;
  padding: 8px 12px;
  font-size: 18px;
  cursor: pointer;
  border-radius: 5px;
}

.expand-btn:hover {
  background-color: #568ea6;
}

.dashboard h2 {
  color: black;
}

/* Expanded Dashboard */
.dashboard.expanded {
  flex: 5;
  background-color: white;
  z-index: 888;
  padding: 20px;
}

/* Compact Dashboard Layout */
.dashboard-areas {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* Expanded Layout - Two Areas Per Row */
.dashboard.expanded .dashboard-areas {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

@media (max-width: 600px) {
  .dashboard.expanded .dashboard-areas {
    grid-template-columns: repeat(1, 1fr);
  }
}

/* Dashboard Area Box */
.dashboard-area {
  margin-bottom: 20px;
  padding: 10px;
  border-radius: 8px;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
}

.dashboard-area h3 {
  margin: 0;
  font-size: 18px;
  font-weight: bold;
  text-decoration: underline;
}

/* Counters for Luggage & People */
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

/* Live Updates inside Each Area */
.live-updates-section {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #ccc;
}
</style>
