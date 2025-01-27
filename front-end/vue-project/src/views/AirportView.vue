<script setup lang="ts">
import AirportMap from '@/components/AirportMap.vue';
import DashBoard from "@/components/Dashboard.vue";
import { reactive } from 'vue';

const overlayAreas = reactive([
  { 
    label: 'Area 1', 
    color: '#F18C8E', 
    position: { top: 50, left: 50, width: 150, height: 150 },
    people: [{ position: { top: 20, left: 30 }, color: '#4caf50' }],
    luggage: [{ position: { top: 70, left: 100 }, color: '#f44336' }],
  },
  { label: 'Area 2', color: '#F0B7A4', position: { top: 200, left: 100, width: 150, height: 150 } },
  { label: 'Area 3', color: '#F1D1B5', position: { top: 400, left: 50, width: 150, height: 150 } },
  { label: 'Area 4', color: '#568EA6', position: { top: 300, left: 300, width: 150, height: 150 } },
]);

</script>

<template>
  <div class="airport-view-container">
    <AirportMap :overlayAreas="overlayAreas" />
    <DashBoard :overlayAreas="overlayAreas" />
  </div>
</template>

<style scoped>
  .airport-view-container{
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    width: 90vw;
    box-sizing: border-box;
    gap: 10%;
  }
</style>