<script setup lang="ts">
import axios from "axios";
import { ref, onMounted, computed } from "vue";
import { usePresetStore } from "../utils/useFetchPresets";
import RoomSelection from "@/components/WarningCreation/RoomSelection.vue";
import WarningConditions from "@/components/WarningCreation/WarningConditions.vue";
import CustomWarningMessage from "@/components/WarningCreation/CustomWarningMessage.vue";

const presetStore = usePresetStore();
const selectedRooms = ref<string[]>([]);
const warningConditions = ref<Record<string, any>>({});
const warningMessages = ref<string[]>([]);
const warningsList = ref<any[]>([]); 
const selectedWarningId = ref<number | null>(null);
const selectedWarning = ref<any>(null);
const newWarningName = ref<string>("");
const isRoomSelectionVisible = ref(false);

// wait for the presets data to populate
const presetData = computed(() => presetStore.presetData);
const isPresetDataAvailable = computed(() => presetData.value && Object.keys(presetData.value).length > 0);

const fetchWarnings = async () => {
  try {
    console.log("fetching");
    const response = await axios.get("http://localhost:5004/warnings", { withCredentials: true });
    warningsList.value = response.data;
    console.log(warningsList);

  } catch (error) {
    console.error("Error fetching warnings:", error);
  }
};

const fetchWarningById = async (warningId: number) => {
  try {
    const response = await axios.get(`http://localhost:5004/warnings/${warningId}`, { withCredentials: true });
    selectedWarningId.value = response.data.id;
     selectedWarning.value = response.data;

    warningConditions.value = response.data.conditions.reduce((acc, item) => {
      acc[item.roomID] = {
        conditions: [...item.conditions], // Pre-fill conditions
        messages: response.data.messages.filter(msg => msg.Location === item.roomID), // Pre-fill messages for room
      };
      return acc;
    }, {});

    isRoomSelectionVisible.value = true;
  } catch (error) {
    console.error("Error fetching warning details:", error);
  }
};

const createWarning = async () => {
  if (!newWarningName.value.trim()) {
    alert("Warning name is required.");
    return;
  }

  const payload = {
    name: newWarningName.value,
  };

  try {
    const response = await axios.post(`http://localhost:5004/warnings`, payload, { withCredentials: true });
    console.log("Warning created:", response.data);
    fetchWarnings(); // Refresh list
  } catch (error) {
    console.error("Error creating warning:", error);
  }
};

const updateWarning = async () => {
  if (!selectedWarningId.value) {
    console.error("No warning selected for update.");
    return;
  }

  const formattedConditions = Object.entries(warningConditions.value).reduce((acc, [roomID, data]) => {
    const validConditions = data.conditions.filter(
      cond => cond.variable !== null && cond.lower_bound !== null && cond.upper_bound !== null
    );

    if (validConditions.length > 0) {
      acc.push({
        roomID,
        conditions: validConditions.map(cond => ({
          variable: cond.variable,
          lower_bound: cond.lower_bound,
          upper_bound: cond.upper_bound,
        })),
      });
    }

    return acc;
  }, []);

  const formattedMessages = Object.entries(warningConditions.value).reduce((acc, [roomID, data]) => {
    console.log("Messages for Room:", roomID, data.messages);

    data.messages.forEach(msg => {
      acc.push({
        Authority: msg.Authority,
        Title: msg.Title || "No Title Provided", // ✅ Allow null, replace with fallback
        Location: msg.Location,
        Severity: msg.Severity,
        Summary: msg.Summary || "No Summary Provided", // ✅ Allow null, replace with fallback
      });
    });

    return acc;
  }, []);
  
  const payload = {
    name: selectedWarning.value.name || `Updated Warning ${selectedWarningId.value}`,
    id: selectedWarningId.value,
    conditions: formattedConditions,
    messages: formattedMessages,
  };

  try {
    await axios.patch(`http://localhost:5004/warnings/${selectedWarningId.value}`, payload, { withCredentials: true });
    await fetchWarnings(); 
  } catch (error) {
    console.error("Error updating warning:", error);
  }
};

const deleteWarning = async (warningId: number) => {
  try {
    await axios.delete(`http://localhost:5004/warnings/${warningId}`, { withCredentials: true });
    warningsList.value = warningsList.value.filter(w => w.id !== warningId);
  } catch (error) {
    console.error("Error deleting warning:", error);
  }
};

const resetWarningSelection = () => {
  selectedWarningId.value = null;
  selectedWarning.value = null;
  warningConditions.value = {};
  isRoomSelectionVisible.value = false; 
};

const toggleRoomSelection = (room: Object) => {
  const existingIndex = selectedRooms.value.findIndex((r) => r.roomID === room.roomID);
  if (existingIndex !== -1) {
    selectedRooms.value.splice(existingIndex, 1); // Remove if already selected
  } else {
    selectedRooms.value.push(room); // Add new room
  }
};

const updateWarningConditions = (updatedConditions: Record<string, any>) => {
  Object.entries(updatedConditions).forEach(([roomID, newData]) => {
    if (!warningConditions.value[roomID]) {
      warningConditions.value[roomID] = { conditions: [], messages: [] };
    }

    // Add new conditions while keeping the old ones
    newData.conditions.forEach(newCond => {
      const existingCondition = warningConditions.value[roomID].conditions.find(
        (c) => c.variable === newCond.variable
      );

      if (existingCondition) {
        existingCondition.lower_bound = newCond.lower_bound;
        existingCondition.upper_bound = newCond.upper_bound;
      } else {
        warningConditions.value[roomID].conditions.push(newCond);
      }
    });

    // Add new messages if they don't exist
    newData.messages.forEach(newMsg => {
      const existingMessage = warningConditions.value[roomID].messages.find(
        (m) => m.Title === newMsg.Title
      );

      if (!existingMessage) {
        warningConditions.value[roomID].messages.push(newMsg);
      }
    });
  });

  console.log("Merged warningConditions:", warningConditions.value);
  updateWarning();
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

onMounted(fetchWarnings);
</script>

<template>
  <div class="warning-creation-view">
    <div>
      <h3>Existing Warnings</h3>
      <ul>
        <li v-for="warning in warningsList" :key="warning.id">
          <span @click="fetchWarningById(warning.id)">{{ warning.name }}</span>
          <button @click="deleteWarning(warning.id)">Delete</button>
        </li>
      </ul>
    </div>

    <div>
      <input v-model="newWarningName" placeholder="Enter warning name" />
      <button @click="createWarning(newWarningName)">Create Warning</button>
    </div>

    <RoomSelection 
      v-if="isPresetDataAvailable && isRoomSelectionVisible" 
      :presetData="presetData"
      @updateRooms="toggleRoomSelection"
    />  

    <WarningConditions 
      v-if="selectedWarning" 
      :selectedWarning="selectedWarning"
      :selectedRooms="selectedRooms" 
      :conditions="warningConditions"
      :createWarning="createWarning"
      @updateConditions="updateWarningConditions" 
    />

    <CustomWarningMessage 
      :conditions="warningConditions" 
      @updateMessages="updateWarningMessages" 
    />

    <button @click="resetWarningSelection">Clear Selection</button>
  </div>
</template>

<style scoped>
.warning-creation-view {
  display: flex;
  flex-direction: column;
}
</style>
