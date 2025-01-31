<script setup lang="ts">
import SummaryHeader from '../components/Summary/SummaryHeader.vue';
import SummaryTable from '../components/Summary/SummaryTable/SummaryTable.vue';
import LiveUpdates from '../components/Summary/LiveUpdates/LiveUpdates.vue';
import { ref, PropType } from 'vue';

const props = defineProps({
  picoIds: {
    type: Array, 
    required: true,
  }, 
  overlayAreasConstant: {
    type: Array,
    required: true,
  },
  overlayAreasData: {
    type: Array,
    required: true,
  },
  updates: {
    type: Array as PropType<string[]>,
    required: true,
  },
  environmentHistory: {
    type: Object,
    required: true,
  },
});

// Active section: "all", "summary", or "updates"
const activeSection = ref("all");

</script>

<template>
  <div class="summary-container">
    <!-- Sidebar Navigation -->
    <nav class="sidebar">
      <button @click="activeSection = 'all'" :class="{ active: activeSection === 'all' }">📌 Show All</button>
      <button @click="activeSection = 'summary'" :class="{ active: activeSection === 'summary' }">📊 Summary Table</button>
      <button @click="activeSection = 'updates'" :class="{ active: activeSection === 'updates' }">🔄 Live Updates</button>
    </nav>

    <!-- Main Content -->
    <div class="summary-content">
      <SummaryHeader title="Live Summary of People and Luggage" />
      
      <SummaryTable 
        v-if="activeSection === 'summary' || activeSection === 'all'"
        :data="overlayAreasData" 
        :overlayAreasConstant="overlayAreasConstant"
        :environmentHistory="environmentHistory"
      />
      <LiveUpdates 
        v-if="activeSection === 'updates' || activeSection === 'all'"
        :userIds="picoIds" 
        :updates="updates"
      />
    </div>
  </div>
</template>

<style scoped>
/* Layout */
.summary-container {
  display: flex;
  height: 90vh;
  background-color: #f8f8ff;
}

/* Sidebar */
.sidebar {
  width: 200px;
  padding: 20px;
  background-color: #305F72;
  color: white;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sidebar button {
  background: none;
  border: none;
  color: white;
  font-size: 16px;
  cursor: pointer;
  padding: 10px;
  text-align: left;
  transition: background 0.3s;
  border-radius: 5px;
}

.sidebar button:hover,
.sidebar button.active {
  background: #568EA6;
}

/* Main Content */
.summary-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
</style>
