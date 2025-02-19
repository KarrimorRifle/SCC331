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

const updateWarningMessages = (updatedMessages: any[]) => {
  updatedMessages.forEach((msg) => {
    const roomID = msg.Location.trim(); // Ensure correct roomID format

    if (!warningConditions.value[roomID]) {
      warningConditions.value[roomID] = { conditions: [], messages: [] };
    }

    // Ensure messages array exists
    if (!Array.isArray(warningConditions.value[roomID].messages)) {
      warningConditions.value[roomID].messages = [];
    }

    // Find existing message index
    const existingMessageIndex = warningConditions.value[roomID].messages.findIndex(
      (m) => m.Title.trim() === msg.Title.trim()
    );

    console.log("Existing Message Index:", existingMessageIndex);

    if (existingMessageIndex !== -1) {
      // Update existing message
      warningConditions.value[roomID].messages[existingMessageIndex].Summary = msg.Summary;
    } else {
      // Add only if it does NOT exist
      warningConditions.value[roomID].messages.push(msg);
    }
  });

  console.log("Updated warningConditions:", JSON.parse(JSON.stringify(warningConditions.value)));
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
