<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { usePresetStore } from "../utils/useFetchPresets";
import RoomSelection from "@/components/WarningCreation/RoomSelection.vue";
import WarningConditions from "@/components/WarningCreation/WarningConditions.vue";
// import WarningMessages from "./WarningMessages.vue";
import CustomWarningMessage from "@/components/WarningCreation/CustomWarningMessage.vue";

const presetStore = usePresetStore();
const selectedRooms = ref<string[]>([]);
const warningConditions = ref<Record<string, any>>({});
const warningMessages = ref<string[]>([]);

// wait for the presets data to populate
const presetData = computed(() => presetStore.presetData);
const isPresetDataAvailable = computed(() => presetData.value && Object.keys(presetData.value).length > 0);

const toggleRoomSelection = (room: Object) => {
  const existingIndex = selectedRooms.value.findIndex((r) => r.roomID === room.roomID);
  if (existingIndex !== -1) {
    selectedRooms.value.splice(existingIndex, 1); // Remove if already selected
  } else {
    selectedRooms.value.push(room); // Add new room
  }
};

const updateWarningConditions = (conditions: Record<string, any>) => {
  warningConditions.value = conditions;
};

const updateWarningMessages = (messages: string[]) => {
  warningMessages.value = messages;
};

</script>

<template>
  <div class="warning-creation-view">
    <h2>Create Warning Rules</h2>

    <RoomSelection 
      v-if="isPresetDataAvailable" 
      :presetData="presetData"
      @updateRooms="toggleRoomSelection"
    />  

    <WarningConditions 
      :selectedRooms="selectedRooms" 
      :conditions="warningConditions"
      @updateConditions="updateWarningConditions" 
    />

    <CustomWarningMessage 
      :conditions="warningConditions" 
      @updateMessages="updateWarningMessages" 
    />

  </div>
</template>

<style scoped>
.warning-creation-view {
  display: flex;
  flex-direction: column;
}
</style>
