<script setup lang="ts">
import AirportMap from "@/components/AirportMap.vue";
import DashBoard from "@/components/Dashboard.vue";
import FilterBar from "../components/FilterBar.vue";
import BottomTabNavigator from "@/components/BottomTabNavigator.vue";
import {onMounted, onUnmounted, ref, watch, computed, PropType, defineEmits,}from "vue"
import axios from "axios";
import OverlayArea from '@/components/OverlayArea.vue';
/*
import type { Timeout } from "node:timers";
import type {preset, presetListType, boxAndData, boxType, summaryType, environmentData, dataObject} from "../utils/mapTypes";
import { addNotification } from '@/stores/notificationStore';
*/
import { usePresetStore } from "../utils/useFetchPresets";
import { usePresetLocalCache } from '../stores/presetLocalCache';
import {sensors, updateSensorMappings, } from "../stores/sensorTypeStore";
// Receive isMobile from App.vue
const props = defineProps({
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
  },
  warnings: {
    type: Array as PropType<{ Title: string; Location: string; Severity: string; Summary: string }[]>,
    required: true,
  },
});
const emit = defineEmits(["updateOverlayAreaColor", "updateOverlayAreas"]);
const presetStore = usePresetStore();
const presetCache = usePresetLocalCache();

const enabledSensors = ref([]);
const showAll = ref(true);
const showDisconnected = ref(false);

const updateEnabledSensors = (filters) => {
  enabledSensors.value = filters.sensors;
  showDisconnected.value = filters.showDisconnected;
  showAll.value = filters.showAll;
};

const isDashboardOpen = ref(true);
const toggleDashboard = () => {
  isDashboardOpen.value = !isDashboardOpen.value;
};

onMounted(async () => {
  await updateSensorMappings();
  enabledSensors.value = sensors.value.map(sensor => sensor.name);
  await presetStore.fetchPresets();
  if (presetStore?.presetList?.presets?.length > 0) {
    await presetStore.fetchPreset();
  }
  console.log(sensors.value)
});

</script>

<template>
  <BottomTabNavigator v-if="isMobile">
    <!-- Slot for Map -->
    <template #map>
      <div class="d-flex flex-column flex-grow-1 h-100">
        <AirportMap
          class="flex-grow-1"
          :isLoading="presetStore.isLoading"
          :warnings="warnings"
          v-model="presetStore.boxes_and_data"
          :presetList="presetStore.presetList"
          :canCreate="presetStore.canCreate"
          :settable="presetStore.settable"
          :defaultPresetId="presetStore.defaultPresetId"
          :currentPreset="presetStore.currentPreset"
          :backgroundImage="presetStore.presetImage"
          :canDelete="presetStore.canDelete"
          :canEdit="presetStore.canEdit"
          :presetData="presetStore.presetData"
          :editMode="presetStore.editMode"
          :showDisconnected="showDisconnected"
          :showAll="showAll"
          :enabledSensors="enabledSensors"
          @selectPreset="presetStore.handleSelectPreset"
          @setDefault="presetStore.setDefaultPreset"
          @newPreset="presetStore.reloadPresets"
          @newImage="presetStore.reloadPresets"
          @delete="presetStore.deletePreset"
          @edit="presetStore.editMode = true"
          @save="presetStore.uploadBoxes"
          @cancel="presetStore.cancelBoxEdit"
        />
        <!--
        <FilterBar 
          class="filter-bar flex-grow-1"
          @updateFilters="updateEnabledSensors" 
        />
        -->
      </div>
    </template>

    <!-- Slot for Dashboard -->
    <template #dashboard>
      <DashBoard
        v-model="presetStore.boxes_and_data"
        :isLoading="presetStore.isLoading"
        :editMode="presetStore.editMode"
        @newBox="presetStore.createNewBox"
        @colourChange="presetStore.handleColourChange"
        @removeBox="presetStore.removeBox"
        :userIds="picoIds"
        :updates="updates"
        :warnings="warnings"
      />
    </template>
  </BottomTabNavigator>

  <div v-else class="airport-view-container d-flex flex-row">
    <div class="d-flex flex-column flex-grow-1" style="display: flex; width: 10%;">
    <AirportMap
      class="flex-grow-1"
      :isLoading="presetStore.isLoading"
      :warnings="warnings"
      v-model="presetStore.boxes_and_data"
      :presetList="presetStore.presetList"
      :canCreate="presetStore.canCreate"
      :settable="presetStore.settable"
      :defaultPresetId="presetStore.defaultPresetId"
      :currentPreset="presetStore.currentPreset"
      :backgroundImage="presetStore.presetImage"
      :canDelete="presetStore.canDelete"
      :canEdit="presetStore.canEdit"
      :presetData="presetStore.presetData"
      :editMode="presetStore.editMode"
      :showDisconnected="showDisconnected"
      :showAll="showAll"
      :enabledSensors="enabledSensors"
      @selectPreset="presetStore.handleSelectPreset"
      @setDefault="presetStore.setDefaultPreset"
      @newPreset="presetStore.reloadPresets"
      @newImage="presetStore.reloadPresets"
      @delete="presetStore.deletePreset"
      @edit="presetStore.editMode = true"
      @save="presetStore.uploadBoxes"
      @cancel="presetStore.cancelBoxEdit"
    />
    <!--<FilterBar @updateFilters="updateEnabledSensors" />-->
    </div>

    <DashBoard
      v-model="presetStore.boxes_and_data"
      :isLoading="presetStore.isLoading"
      :editMode="presetStore.editMode"
      @newBox="presetStore.createNewBox"
      @colourChange="presetStore.handleColourChange"
      @removeBox="presetStore.removeBox"
      :userIds="picoIds"
      :updates="updates"
      :warnings="warnings"
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