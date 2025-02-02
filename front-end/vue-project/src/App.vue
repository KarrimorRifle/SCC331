<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import Navbar from '@/components/Navbar.vue';
import { useFetchData } from '@/utils/useFetchData';

const picoIds = [1, 2, 3, 4, 5, 6, 9, 10, 14, 59];

const { overlayAreasConstant, overlayAreasData, updates, environmentHistory } = useFetchData(picoIds);

// Responsive State (Moved from AirportView.vue)
const isMobile = ref(window.innerWidth <= 768);

// Function to update `isMobile` on window resize
const updateScreenSize = () => {
  isMobile.value = window.innerWidth <= 768;
};

// Attach event listeners
onMounted(() => {
  window.addEventListener("resize", updateScreenSize);
  updateScreenSize();
});

onUnmounted(() => {
  window.removeEventListener("resize", updateScreenSize);
});
</script>

<template>
  <div class="app">
    <Navbar />
    <router-view 
      :picoIds="picoIds"
      :overlayAreasConstant="overlayAreasConstant"
      :overlayAreasData="overlayAreasData" 
      :updates="updates"
      :environmentHistory="environmentHistory"
      :isMobile="isMobile"
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
  margin: 0;
  padding: 0;
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
