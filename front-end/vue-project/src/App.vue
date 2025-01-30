<script setup lang="ts">
import Navbar from '@/components/Navbar.vue';
import { ref, reactive, onMounted, onUnmounted, watch } from 'vue';

const LOCAL_STORAGE_KEY = 'overlayAreas'; // Storage Key for persistence

// Load from localStorage if available, otherwise use default values
const loadOverlayAreas = () => {
  const storedData = localStorage.getItem(LOCAL_STORAGE_KEY);
  return storedData ? JSON.parse(storedData) : [
    { label: "Area 1", color: "#F18C8E", position: { top: 50, left: 50, width: 150, height: 150 } },
    { label: "Area 2", color: "#F0B7A4", position: { top: 200, left: 100, width: 150, height: 150 } },
    { label: "Area 3", color: "#F1D1B5", position: { top: 400, left: 50, width: 150, height: 150 } },
    { label: "Area 4", color: "#568EA6", position: { top: 300, left: 300, width: 150, height: 150 } }
  ];
};

// Make overlayAreasConstant reactive
const overlayAreasConstant = reactive(loadOverlayAreas());

// Watch for changes and store in localStorage
watch(overlayAreasConstant, (newValue) => {
  localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(newValue));
}, { deep: true });

const overlayAreasData = ref([]);
const updates = ref([]);
const environmentHistory = ref({}); 
let pollingInterval;

// Load environment data
const trackEnvironmentData = (label, data) => {
  if (!data) return;
  const timestamp = Date.now();
  if (!environmentHistory.value[label]) {
    environmentHistory.value[label] = [];
  }
  environmentHistory.value[label].push({
    timestamp,
    temperature: data.temperature,
    sound: data.sound,
    light: data.light,
  });
  if (environmentHistory.value[label].length > 20) {
    environmentHistory.value[label].shift();
  }
};

// Fetch dynamic data
const fetchData = async () => {
  try {
    // const response = await fetch("/summary");
    const response = await fetch("/summary");

    const data = await response.json();

    Object.entries(data).forEach(([key, area]) => {
      if (area.environment && Object.keys(area.environment).length > 0) {
        trackEnvironmentData(key, area.environment);
      } else {
        console.warn(`Empty or missing environment data for Key: ${key}`);
      }
    });

    if (JSON.stringify(data) !== JSON.stringify(overlayAreasData.value)) {
      console.log('Overlay areas updated:', data);
      overlayAreasData.value = data;
    }
    if (JSON.stringify(data.updates) !== JSON.stringify(updates.value)) {
      console.log('Updates updated:', data.updates);
      updates.value = data.updates;
    }
  } catch (error) {
    console.error('Error fetching data:', error);
  }
};

onMounted(() => {
  fetchData();
  pollingInterval = setInterval(fetchData, 5000);
});

onUnmounted(() => {
  clearInterval(pollingInterval);
});
</script>

<template>
  <div class="app">
    <Navbar />
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
