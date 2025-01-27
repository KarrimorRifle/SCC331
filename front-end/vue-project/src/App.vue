<script setup lang="ts">
import Navbar from '@/components/Navbar.vue';
import { reactive } from 'vue';

const overlayAreas = reactive([
  { 
    label: 'Area 1', 
    color: '#F18C8E', 
    position: { top: 50, left: 50, width: 150, height: 150 },
    people: [{ position: { top: 20, left: 30 }, color: '#4caf50' }],
    luggage: [{ position: { top: 70, left: 100 }, color: '#f44336' }],
  },
  { label: 'Area 2', color: '#F0B7A4', position: { top: 200, left: 100, width: 150, height: 150 }, people: [], luggage: [] },
  { label: 'Area 3', color: '#F1D1B5', position: { top: 400, left: 50, width: 150, height: 150 }, people: [], luggage: [] },
  { label: 'Area 4', color: '#568EA6', position: { top: 300, left: 300, width: 150, height: 150 }, people: [], luggage: [] },
]);
</script>

<template>
  <div class="app">
    <!-- Navbar -->
    <Navbar />
    
    <!-- Dynamic Routing -->
    <router-view :overlayAreas="overlayAreas" />
  </div>
</template>

<style>
html, body, *{
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
