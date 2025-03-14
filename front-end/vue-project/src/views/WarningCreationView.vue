<script setup lang="ts">
import axios from "axios";
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faTrash, faChevronRight, faChevronDown} from '@fortawesome/free-solid-svg-icons';
import { ref, onMounted, computed, warn } from "vue";
import { usePresetStore } from "../utils/useFetchPresets";
import RoomSelection from "@/components/WarningCreation/RoomSelection.vue";
import WarningConditions from "@/components/WarningCreation/WarningConditions.vue";
// import CustomWarningMessage from "@/components/WarningCreation/CustomWarningMessage.vue";

const presetStore = usePresetStore();
const selectedRooms = ref<string[]>([]);
// wait for the presets data to populate
const presetData = computed(() => presetStore.presetData);
const isPresetDataAvailable = computed(() => presetData.value && Object.keys(presetData.value).length > 0);

const isWarningListCollapsed = ref(false);
const selectedWarningName = computed(() => {
  if (!Array.isArray(warningsList.value)) return null; // Ensure it's an array
  const selected = warningsList.value.find(warning => warning.id === selectedWarningId.value);
  return selected ? selected.name : null;
});
import { 
  warningsList, 
  selectedWarningId, 
  selectedWarning, 
  newWarningName, 
  warningConditions, 
  warningMessages,
  isRoomSelectionVisible,
  activeSection,
  fetchWarnings, 
  fetchWarningById, 
  createWarning, 
  updateWarning, 
  deleteWarning, 
  resetWarningSelection 
} from '../stores/warningStore';

const warningSectionRef = ref<HTMLElement| null>(null);
const roomSelectionRef = ref<HTMLElement| null>(null);
const conditionsRef = ref<HTMLElement| null>(null);

const searchQuery = ref("");

const filteredWarnings = computed(() => {
  if (!searchQuery.value) return warningsList.value;
  return warningsList.value.filter(warning =>
    warning.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

const toggleWarningList = () => {
  isWarningListCollapsed.value = !isWarningListCollapsed.value;
};

const toggleRoomSelection = (room: Object) => {
   if (!Array.isArray(selectedRooms.value)) {
    console.error("selectedRooms is not an array:", selectedRooms.value);
    selectedRooms.value = []; // Ensure it is an array
  }
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

    if (!Array.isArray(warningConditions.value[roomID].conditions)) {
      console.error(`warningConditions[${roomID}].conditions is not an array:`, warningConditions.value[roomID].conditions);
      warningConditions.value[roomID].conditions = []; // Ensure it's an array
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

    if (!Array.isArray(warningConditions.value[roomID].messages)) {
      console.error(`warningConditions[${roomID}].messages is not an array:`, warningConditions.value[roomID].messages);
      warningConditions.value[roomID].messages = []; // Ensure it's an array
    }

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
    if (existingMessageIndex !== -1) {
      // Update existing message
      warningConditions.value[roomID].messages[existingMessageIndex].Summary = msg.Summary;
    } else {
      // Add only if it does NOT exist
      warningConditions.value[roomID].messages.push(msg);
    }
  });
};

const setActiveSection = (section: string) => {
  activeSection.value = section;
  if (section === "warnings" && warningSectionRef.value) {
    warningSectionRef.value.scrollIntoView({ behavior: "smooth", block: "start" });
  } else if (section === "rooms" && roomSelectionRef.value?.$el) {
    roomSelectionRef.value.$el.scrollIntoView({ behavior: "smooth", block: "start" });
  } else if (section === "conditions" && conditionsRef.value?.$el) {
    conditionsRef.value.$el.scrollIntoView({ behavior: "smooth", block: "start" });
  }
};

const getSidebarClass = (section: string) => {
  return { active: activeSection.value === section };
};

onMounted(fetchWarnings);
</script>

<template>
  <div class="app-container">
    <!-- Sidebar Navigation -->
    <nav class="sidebar">
      <button @click="setActiveSection('warnings')" :class="{ active: activeSection === 'warnings' }">⚠️ Warnings</button>
      <button @click="setActiveSection('rooms')" :class="{ active: activeSection === 'rooms' }">📌 Room Selection</button>
      <button @click="setActiveSection('conditions')" :class="{ active: activeSection === 'conditions' }">🔧 Conditions</button>
    </nav>

    <!-- Main Content -->
    <div class="warning-creation-content">
      <!-- Existing Warnings List -->
      <div 
        ref="warningSectionRef"
        :class="['section', { dimmed: activeSection !== 'warnings' }]"
        @click="setActiveSection('warnings')"
      >
        <div class="existing-warning-header">
          <h3>
            Existing Warnings
            <FontAwesomeIcon 
              :icon="isWarningListCollapsed ? faChevronRight : faChevronDown" 
              class="toggle-icon"
              @click.stop="toggleWarningList"
            />
          </h3>

          <div class="search-input-container">
            <input 
              v-model="searchQuery"
              placeholder="Search warnings..."
              class="search-input"
            />
          </div>

          <div class="add-warning-container">
            <input v-model="newWarningName" placeholder="Enter warning name" />
            <button @click="createWarning(newWarningName)">Create</button>
          </div>
        </div>
        <div v-if="selectedWarningName" class="selected-warning">
          <strong>Selected Warning:</strong> {{ selectedWarningName }}
        </div>
        <ul v-show="!isWarningListCollapsed" class="existing-warning-list">
          <li v-for="warning in filteredWarnings" 
              :key="warning.id" 
              :class="['warning-item', { selected: selectedWarningId === warning.id }]"
              @click="fetchWarningById(warning.id)"
               >
            <div class="warning-content">
              <div class="warning-details">
                <h5>Name</h5>
                <p>{{ warning.name }}</p>
              </div>
              <button @click.stop="deleteWarning(warning.id)" class="delete-button">
                <FontAwesomeIcon :icon="faTrash" />
              </button>
            </div>
          </li>
        </ul>
      </div>

      <!-- Room Selection -->
      <RoomSelection 
        ref="roomSelectionRef"
        v-if="isPresetDataAvailable" 
        :isRoomSelectionVisible="isRoomSelectionVisible"
        :presetData="presetData"
        :class="['section', { dimmed: activeSection !== 'rooms' }]"
        @updateRooms="toggleRoomSelection"
        @click="setActiveSection('rooms')"
      />

      <!-- Warning Conditions -->
      <WarningConditions 
        ref="conditionsRef"
        v-if="selectedWarning" 
        :selectedWarning="selectedWarning"
        :selectedRooms="selectedRooms" 
        :conditions="warningConditions"
        :class="['section', { dimmed: activeSection !== 'conditions' }]"
        @updateConditions="updateWarningConditions" 
        @click="setActiveSection('conditions')"
      />

      <!-- Custom Warning Messages 
      <CustomWarningMessage 
        :conditions="warningConditions" 
        :class="['section', { dimmed: activeSection !== 'messages' }]"
        @updateMessages="updateWarningMessages" 
      />
      

      <button @click="resetWarningSelection">Clear Selection</button>
      -->
    </div>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  background: var(--primary-light-bg);
}

.sidebar h3 {
  font-size: 20px;
  margin-bottom: 15px;
}

.sidebar {
  width: 200px;
  padding: 20px;
  background-color: var(--primary-dark-bg);
  color: var(--primary-light-text);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sidebar button {
  background: none;
  border: none;
  color: var(--primary-light-text);
  font-size: 16px;
  cursor: pointer;
  padding: 10px;
  text-align: left;
  transition: background 0.3s;
  border-radius: 5px;
}

.sidebar button:hover,
.sidebar button.active {
  background: var(--primary-dark-bg-hover);
}

.warning-creation-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.section {
  padding: 20px;
  border-radius: 8px;
  background: var(--primary-light-bg);
  color: var(--primary-dark-text);
  transition: opacity 0.3s;
  border: 2px solid #568EA6;
}

.dimmed {
  opacity: 0.4;
}

.existing-warning-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}
.toggle-icon {
  margin-left: 10px;  
  font-size: 18px;    
  transition: transform 0.2s ease-in-out, color 0.2s ease-in-out;
  cursor: pointer;   
  color: var(--primary-bg);   
}
.is-collapsed .toggle-icon {
  transform: rotate(90deg);
}
.existing-warning-list {
  padding: 0;
}

.warning-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: var(--primary-dark-text);
  padding: 5px;
  margin: 10px 0;
  border-radius: 8px;
  font-size: 18px;
  cursor: pointer;
  transition: background 0.3s, transform 0.2s;
}

.warning-item:hover {
  background: var(--not-active-bg);
  transform: scale(1.01);
}

.warning-item.selected {
  background: var(--active-bg);
  transform: scale(1.01);
}

.warning-content {
  display: flex;
  justify-content: space-between;
  width: 100%;
}

.warning-details {
  text-align: left;
}

.delete-button {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--warning-text);
  font-size: 18px;
  transition: color 0.3s ease-in-out;
}

.delete-button:hover {
  color: var(--warning-text-hover) !important;
  z-index: 999;
}

.search-input-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  background: var(--primary-light-bg);
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #568EA6;
}
.search-input {
  padding: 10px;
  border: 1px solid #CBD5E1;
  border-radius: 6px;
  font-size: 16px;
  outline: none;
  transition: border 0.2s ease-in-out;
}

.add-warning-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  background: var(--primary-light-bg);
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #568EA6;
}

.add-warning-container input {
  padding: 10px;
  border: 1px solid #CBD5E1;
  border-radius: 6px;
  font-size: 16px;
  outline: none;
  transition: border 0.2s ease-in-out;
}
.add-warning-container button {
  background: var(--primary-bg);
  color: var(--primary-light-text);
  border: none;
  padding: 10px;
  font-weight: bold;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s ease-in-out;
}

.add-warning-container button:hover {
  background: var(--primary-bg-hover);
}

@media (max-width: 768px) {
  .app-container {
    flex-direction: column;
  }

  .sidebar {
    flex-direction: row;
    width: 100%;
  }
  .existing-warning-header{
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>