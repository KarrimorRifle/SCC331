<script setup lang="ts">
import Navbar from '@/components/Navbar.vue';
import { useFetchData } from '@/utils/useFetchData';

const picoIds = [1, 2, 3, 4, 5, 6, 9, 10, 14, 59];

const { overlayAreasConstant, overlayAreasData, updates, environmentHistory } = useFetchData(picoIds);
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
