<script setup lang="ts">
import AirportMap from '@/components/AirportMap.vue';
import DashBoard from "@/components/Dashboard.vue";

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

</script>

<template>
  <div class="airport-view-container d-flex flex-row">
    <AirportMap
      class="flex-grow-1"
      :overlayAreasConstant="overlayAreasConstant" 
      :overlayAreasData="overlayAreasData" 
    />
    <DashBoard
      :overlayAreasConstant="overlayAreasConstant" 
      :overlayAreasData="overlayAreasData" 
    />
  </div>
</template>

<!-- <style scoped>
  .airport-view-container{
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }
  @media (max-width: 600px) {
  .airport-view-container{
    flex-direction: column;
  }
}
</style> -->