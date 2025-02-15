<script setup lang="ts">
import SummaryHeader from '../components/Summary/SummaryHeader.vue';
import SummaryTable from '../components/Summary/SummaryTable/SummaryTable.vue';
import LiveUpdates from '../components/Summary/LiveUpdates/LiveUpdates.vue';
import WarningSystem from '../components/Summary/WarningSystem/WarningSystem.vue'; // Import new warning system component
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
    type: Object,
    required: true,
  },
  updates: {
    type: Object,
    required: true,
  },
  environmentHistory: {
    type: Object,
    required: true,
  },
  warnings: {
    type: Array as PropType<{ Title: string; Location: string; Severity: string; Summary: string }[]>,
    required: true,
  },
});

// Active section: "all", "summary", or "updates"
const activeSection = ref("all");

</script>

<template>
  <div class="summary-container" id="summary">
    <!-- Sidebar Navigation -->
    <nav class="sidebar">
      <button @click="activeSection = 'all'" :class="{ active: activeSection === 'all' }">📌 Show All</button>
      <button @click="activeSection = 'summary'" :class="{ active: activeSection === 'summary' }">📊 Summary Table</button>
      <button @click="activeSection = 'updates'" :class="{ active: activeSection === 'updates' }">🔄 Live Updates</button>
      <button @click="activeSection = 'warnings'" :class="{ active: activeSection === 'warnings' }">⚠️ Warnings</button>
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
        :overlayAreasConstant="overlayAreasConstant"
      />
      <WarningSystem
        v-if="activeSection === 'warnings' || activeSection === 'all'"
        :warnings="warnings"
        :overlayAreasConstant="overlayAreasConstant"
      />
    </div>
  </div>
</template>

<style scoped>
/* Layout */
.summary-container {
  display: flex;
  background-color: #f8f8ff;
}

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

.summary-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

@media (max-width: 600px) {
  .summary-container{
    flex-direction: column;
  }
  .sidebar{
    flex-direction: row;
    width: 100%;
  }
}
</style>
