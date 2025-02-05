<script setup lang="ts">
import AirportMap from '@/components/AirportMap.vue';
import DashBoard from "@/components/Dashboard.vue";
import {onMounted, onUnmounted, ref, watch }from "vue"
import axios from "axios";
import OverlayArea from '@/components/OverlayArea.vue';
import type { Timeout } from "node:timers";

let pollingInterval: Timeout;
let OverlayAreasData = ref({});
let presetList = ref();
let currentPreset = ref();
let presetData = ref();

watch(currentPreset, () => {
  fetchPreset();
});

onMounted(() => {
  // Make sure data is always being updated
  pollingInterval = setInterval(fetchSummary, 5000);
  // Grab the list of presets
  fetchPresets();
  // Grab default preset and set it to the current one
  currentPreset.value = presetList.value.default;
  fetchPreset();
});

onUnmounted(() => {
  if (pollingInterval) clearInterval(pollingInterval);
});

const fetchSummary = async() => {
  let request = await axios.get("http://localhost:5003/summary",
    { withCredentials: true});
  OverlayAreasData.value = request.data;
  console.log(OverlayAreasData.value)
}

const fetchPresets = async() => {
  let request = await axios.get("http://localhost:5010/presets",
    {withCredentials: true});
  presetList.value = request.data;
}

const fetchPreset = async() => {
  let request = await axios.get(`http://localhost:5010/presets/${currentPreset.value}}`,
    {withCredentials: true});
  presetData.value = request.data;
}

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