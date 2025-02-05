<script setup lang="ts">
import { ref } from "vue";
import AirportMap from "@/components/AirportMap.vue";
import DashBoard from "@/components/Dashboard.vue";

// Receive isMobile from App.vue
const props = defineProps({
  overlayAreasConstant: {
    type: Array,
    required: true,
  },
  overlayAreasData: {
    type: Object,
    required: true,
  },
  isMobile: {
    type: Boolean,
    required: true,
  }, 
  picoIds: {
    type: Array,
    required: true,
  },
  updates: {
    type: Object,
    required: true,
  }
});

// Dashboard toggle
const isDashboardOpen = ref(true);
const toggleDashboard = () => {
  isDashboardOpen.value = !isDashboardOpen.value;
};
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
      :userIds="picoIds"
      :updates="updates"
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
    padding: 10px;
    gap: 10px;
  }

  .airport-map, .dashboard {
    width: 100%;
  }

  .dashboard-toggle {
    display: block;
  }
}
</style> -->