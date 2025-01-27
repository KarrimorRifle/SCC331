<script setup lang="ts">
import AirportMap from '@/components/AirportMap.vue';
import DashBoard from "@/components/Dashboard.vue";

const props = defineProps({
  overlayAreas: {
    type: Array,
    required: true,
  },
});

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
    width: 100%;
    height: 90vh;
    box-sizing: border-box;
    gap: 10%;
  }
  @media (max-width: 600px) {
  .airport-view-container{
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    width: 100%;
    height: 90vh;
    box-sizing: border-box;
    gap: 0%;
  }
}
</style>