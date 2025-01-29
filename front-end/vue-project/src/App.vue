<script setup lang="ts">
import Navbar from '@/components/Navbar.vue';
import { ref, reactive, onMounted, onUnmounted } from 'vue';

const overlayAreasConstant = reactive([
  { label: "Area 1", color: "#F18C8E", position: { top: 50, left: 50, width: 150, height: 150 } },
  { label: "Area 2", color: "#F0B7A4", position: { top: 200, left: 100, width: 150, height: 150 } },
  { label: "Area 3", color: "#F1D1B5", position: { top: 400, left: 50, width: 150, height: 150 } },
  { label: "Area 4", color: "#568EA6", position: { top: 300, left: 300, width: 150, height: 150 } }
]);

const overlayAreasData = ref([]);
const updates = ref([]);
const environmentHistory = ref({}); 
let pollingInterval: number;

const trackEnvironmentData = (data) => {
  data.forEach((area) => {
    if (!area.environment) return;

    const timestamp = Date.now();
    if (!environmentHistory.value[area.label]) {
      environmentHistory.value[area.label] = [];
    }

    environmentHistory.value[area.label].push({
      timestamp,
      temperature: area.environment.temperature,
      sound: area.environment.sound,
      light: area.environment.light,
    });

    // Keep only last 20 data points
    if (environmentHistory.value[area.label].length > 20) {
      environmentHistory.value[area.label].shift();
    }
  });
};

const fetchData = async () => {
  try {
    const response = await fetch('../data.json');
    const data = await response.json();

    trackEnvironmentData(data.overlayAreasData);

    // Compare overlayAreas for changes
    if (JSON.stringify(data.overlayAreasData) !== JSON.stringify(overlayAreasData.value)) {
      console.log('Overlay areas updated:', data.overlayAreasData);
      overlayAreasData.value = data.overlayAreasData; // Update the overlay areas
    }

    // Compare updates for changes
    if (JSON.stringify(data.updates) !== JSON.stringify(updates.value)) {
      console.log('Updates updated:', data.updates);
      updates.value = data.updates; // Replace updates entirely to handle reductions or reordering
    }
  } catch (error) {
    console.error('Error fetching data:', error);
  }
};

onMounted(() => {
  fetchData(); // Initial fetch
  pollingInterval = setInterval(fetchData, 5000); // Poll every 5 seconds
});

onUnmounted(() => {
  clearInterval(pollingInterval); // Clean up polling on component unmount
});
</script>

<template>
  <div class="app">
    <!-- Navbar -->
    <Navbar />

    <!-- Dynamic Routing -->
    <router-view 
      :overlayAreasConstant="overlayAreasConstant"
      :overlayAreasData="overlayAreasData" 
      :updates="updates"
      :environmentHistory="environmentHistory"
    />
  </div>
</template>

<style>
html, body, * {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  overflow-x: hidden;
}

#app {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}

.router-view {
  width: 100%;
  height: 100%;
}
</style>
