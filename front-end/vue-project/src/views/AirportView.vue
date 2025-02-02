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
  }
});

// Dashboard toggle
const isDashboardOpen = ref(true);
const toggleDashboard = () => {
  isDashboardOpen.value = !isDashboardOpen.value;
};
</script>

<template>
  <div class="airport-view-container">
    <!-- Airport Map Section -->
    <div class="airport-map">
      <AirportMap 
        :overlayAreasConstant="overlayAreasConstant" 
        :overlayAreasData="overlayAreasData" 
      />
    </div>

    <!-- Mobile Dashboard Toggle Button -->
    <button class="dashboard-toggle" @click="toggleDashboard" v-if="isMobile">
      {{ isDashboardOpen ? "Hide Dashboard ⬆️" : "Show Dashboard ⬇️" }}
    </button>

    <!-- Dashboard Section -->
    <div class="dashboard" :class="{ hidden: isMobile && !isDashboardOpen }">
      <DashBoard 
        :overlayAreasConstant="overlayAreasConstant" 
        :overlayAreasData="overlayAreasData" 
      />
    </div>
  </div>
</template>

<style scoped>
/* Layout */
.airport-view-container {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
  gap: 20px;
}

/* Airport Map */
.airport-map {
  flex: 1;
  min-width: 300px;
}

/* Dashboard */
.dashboard {
  min-width: 300px;
  background: #f8f8ff;
  padding: 15px;
  border-radius: 10px;
  transition: 0.3s ease-in-out;
}

/* Hidden Dashboard on Mobile */
.dashboard.hidden {
  display: none;
}

/* Toggle Button for Mobile */
.dashboard-toggle {
  display: none;
  width: 100%;
  padding: 10px;
  font-size: 16px;
  background-color: #305F72;
  color: white;
  border: none;
  cursor: pointer;
  margin-bottom: 10px;
  border-radius: 5px;
}

.dashboard-toggle:hover {
  background-color: #568EA6;
}

/* Responsive Design */
@media (max-width: 768px) {
  .airport-view-container {
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
</style>
