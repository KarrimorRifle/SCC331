<script setup lang="ts">
import SummaryHeader from '../components/Summary/SummaryHeader.vue';
import SummaryTable from '../components/Summary/SummaryTable.vue';
import LiveUpdates from '../components/Summary/LiveUpdates.vue';
import { PropType } from 'vue';

const props = defineProps({
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

</script>

<template>
  <div class="summary-view">
    <SummaryHeader title="Live Summary of People and Luggage" />
    <SummaryTable 
      :data="overlayAreasData" 
      :overlayAreasConstant="overlayAreasConstant"
      :environmentHistory="environmentHistory"
    />
    <LiveUpdates :updates="updates"/>
  </div>
</template>

<style scoped>
.summary-view {
  display: flex;
  flex-direction: column;
  height: 90vh;
  overflow-y: auto;
  background-color: #f8f8ff;
}
</style>
