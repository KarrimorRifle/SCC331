<script setup lang="ts">
import Navbar from '@/components/Navbar.vue';
import { ref, onMounted, onUnmounted } from 'vue';

const overlayAreas = ref([]);
const updates = ref([]);
let pollingInterval: number;

const fetchData = async () => {
  try {
    const response = await fetch('../data.json');
    const data = await response.json();

    // Compare overlayAreas for changes
    if (JSON.stringify(data.overlayAreas) !== JSON.stringify(overlayAreas.value)) {
      console.log('Overlay areas updated:', data.overlayAreas);
      overlayAreas.value = data.overlayAreas; // Update the overlay areas
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
      :overlayAreas="overlayAreas" 
      :updates="updates"
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
