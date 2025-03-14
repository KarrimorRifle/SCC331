<script setup lang="ts">
import { defineProps, defineEmits, ref, watch, computed } from "vue";
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faTrash } from '@fortawesome/free-solid-svg-icons';
import ConditionEditModal from "./ConditionEditModal.vue";

const props = defineProps({
  selectedWarning: Object, 
  selectedRooms: Array as () => { label: string; roomID: string }[],
  conditions: Object, 
  createWarning: Function, 
});
const emit = defineEmits(["updateConditions"]);

// List of possible condition types, authorities, and severities
const conditionTypes = ["Temperature", "Person", "Luggage", "Light Level"];
const authorities = ["admin", "security", "staff", "users", "everyone"];
const severities = ["danger", "warning", "notification"];

const isEditModalOpen = ref(false);
const editRoomID = ref<string | null>(null);
const editCondition = ref<any>(null);
const editConditionIndex = ref<number | null>(null);

const selectedAuthority = ref<{ [key: string]: string }>({});
const selectedSeverity = ref<{ [key: string]: string }>({});
const selectedConditionType = ref<{ [key: string]: string }>({});

// Initialize pendingConditions with a default object if needed
const pendingConditions = ref<Record<string, {
  conditions: { variable: string | null; lower_bound: number | null; upper_bound: number | null }[];
  messages: { Authority: string | null; Location: string | null; Severity: string | null; Summary: string | null; Title: string | null }[];
  roomID: string;
}>>({});

const filteredConditions = computed(() => {
  const roomConditions: Record<string, any[]> = {};
  if (!props.conditions) return roomConditions;
  Object.keys(props.conditions).forEach((roomID) => {
    // Ensure conditions array exists and is an array
    const conditionsArray = Array.isArray(props.conditions[roomID].conditions)
      ? props.conditions[roomID].conditions
      : [];
    roomConditions[roomID] = conditionsArray.filter(
      (condition) => condition.variable !== null
    );
  });
  return roomConditions;
});

const isConditionValid = (roomID: string) => {
  const conditionType = selectedConditionType.value[roomID];
  if (!conditionType) return false;
  const roomPending = pendingConditions.value[roomID];
  if (!roomPending || !Array.isArray(roomPending.conditions)) return false;
  const conditionEntry = roomPending.conditions.find(c => c.variable === conditionType);
  if (!conditionEntry || conditionEntry.lower_bound === null || conditionEntry.upper_bound === null) return false;
  const messageEntry = roomPending.messages && roomPending.messages[0];
  if (!messageEntry || !messageEntry.Authority || !messageEntry.Severity || !messageEntry.Title || !messageEntry.Summary)
    return false;
  return true;
};

const updatePendingCondition = (roomID: string, conditionType: string, key: "min" | "max", value: number) => {
  if (!pendingConditions.value[roomID]) return;
  // Ensure conditions array exists
  if (!Array.isArray(pendingConditions.value[roomID].conditions)) {
    pendingConditions.value[roomID].conditions = [];
  }
  let conditionEntry = pendingConditions.value[roomID].conditions.find(c => c.variable === conditionType);
  if (!conditionEntry) {
    conditionEntry = { variable: conditionType, lower_bound: null, upper_bound: null };
    pendingConditions.value[roomID].conditions.push(conditionEntry);
  }
  if (key === "min") {
    conditionEntry.lower_bound = value;
  } else if (key === "max") {
    conditionEntry.upper_bound = value;
  }
  pendingConditions.value = { ...pendingConditions.value };
};

const updatePendingMessage = (roomID: string, key: "Authority" | "Severity" | "Title" | "Summary", value: string) => {
  if (!pendingConditions.value[roomID]) return;
  // Ensure messages array exists
  if (!Array.isArray(pendingConditions.value[roomID].messages)) {
    pendingConditions.value[roomID].messages = [];
  }
  if (pendingConditions.value[roomID].messages.length === 0) {
    pendingConditions.value[roomID].messages = [{
      Authority: authorities[0],
      Location: roomID,
      Severity: severities[0],
      Summary: null,
      Title: null,
    }];
  } else {
    pendingConditions.value[roomID].messages[0].Location = roomID;
  }
  pendingConditions.value[roomID].messages[0][key] =
    key === "Authority" ? value || authorities[0] :
    key === "Severity" ? value || severities[0] :
    value;
  pendingConditions.value = { ...pendingConditions.value };
};

const setCondition = (roomID: string) => {
  const conditionType = selectedConditionType.value[roomID];
  if (!conditionType) return;
  if (!isConditionValid(roomID)) return;
  
  // Ensure conditions array exists
  if (!Array.isArray(pendingConditions.value[roomID].conditions)) {
    pendingConditions.value[roomID].conditions = [];
  }
  const existingConditionIndex = pendingConditions.value[roomID].conditions.findIndex(
    (c) => c.variable === conditionType
  );
  if (existingConditionIndex !== -1) {
    pendingConditions.value[roomID].conditions[existingConditionIndex] = {
      variable: conditionType,
      lower_bound: pendingConditions.value[roomID].conditions[existingConditionIndex].lower_bound || null,
      upper_bound: pendingConditions.value[roomID].conditions[existingConditionIndex].upper_bound || null,
    };
  } else {
    pendingConditions.value[roomID].conditions.push({
      variable: conditionType,
      lower_bound: null,
      upper_bound: null,
    });
  }
  // Ensure messages array exists
  if (!Array.isArray(pendingConditions.value[roomID].messages)) {
    pendingConditions.value[roomID].messages = [];
  }
  const existingMessageIndex = pendingConditions.value[roomID].messages.findIndex(
    (m) => m.Title === conditionType
  );
  if (existingMessageIndex !== -1) {
    pendingConditions.value[roomID].messages[existingMessageIndex] = {
      Authority: selectedAuthority.value[roomID] || "admin",
      Title: conditionType,
      Location: roomID,
      Severity: selectedSeverity.value[roomID] || "warning",
      Summary: pendingConditions.value[roomID].messages[existingMessageIndex].Summary,
    };
  } else {
    pendingConditions.value[roomID].messages.push({
      Authority: selectedAuthority.value[roomID] || "admin",
      Title: conditionType,
      Location: roomID,
      Severity: selectedSeverity.value[roomID] || "warning",
      Summary: "",
    });
  }
  emit("updateConditions", { ...pendingConditions.value });
  selectedConditionType.value[roomID] = "";
  selectedAuthority.value[roomID] = "";
  selectedSeverity.value[roomID] = "";
  pendingConditions.value[roomID].messages = [{
    Authority: null,
    Location: null,
    Severity: null,
    Summary: "",
    Title: ""
  }];
  pendingConditions.value = { ...pendingConditions.value };
};

const removeCondition = (roomID: string, conditionIndex: number) => {
  if (props.conditions[roomID]) {
    // Ensure conditions is an array
    if (Array.isArray(props.conditions[roomID].conditions)) {
      props.conditions[roomID].conditions.splice(conditionIndex, 1);
    }
    if (props.conditions[roomID].conditions.length === 0) {
      delete props.conditions[roomID];
    }
    emit("updateConditions", { ...props.conditions });
  }
};

const openEditModal = (roomID: string, condition: any, index: number) => {
  editRoomID.value = roomID;
  editCondition.value = { ...condition };
  editConditionIndex.value = index;
  isEditModalOpen.value = true;
};

const updateCondition = ({ roomID, index, updatedCondition }) => {
  if (!props.conditions[roomID]) return;
  props.conditions[roomID].conditions[index] = updatedCondition;
  emit("updateConditions", { ...props.conditions });
  isEditModalOpen.value = false;
};

watch(
  () => props.selectedRooms,
  (newRooms) => {
    newRooms.forEach((room) => {
      if (!pendingConditions.value[room.roomID]) {
        pendingConditions.value[room.roomID] = {
          conditions: [{ variable: null, lower_bound: null, upper_bound: null }],
          messages: [{ Authority: null, Location: null, Severity: null, Summary: null, Title: null }],
          roomID: room.roomID,
        };
      }
    });
    // Cleanup: Remove rooms no longer selected
    Object.keys(pendingConditions.value).forEach((roomID) => {
      if (!newRooms.some((room) => room.roomID === roomID)) {
        delete pendingConditions.value[roomID];
      }
    });
  },
  { deep: true, immediate: true }
);
</script>

<template>  
  <h3 v-if="selectedRooms.length === 0" class="warning-message">
    Select an area first
  </h3>

  <div v-else class="conditions-container">
    <h3>Set Warning Conditions</h3>
    
    <div v-for="room in props.selectedRooms" :key="room.roomID" class="room-conditions">
      <h4>Area {{ room.label }}</h4>

      <div v-if="props.conditions[room.roomID]?.conditions.length" class="existing-conditions">
        <h5>Existing Conditions:</h5>
        <ul v-if="filteredConditions[room.roomID]?.length">
          <li 
            v-for="(condition, index) in filteredConditions[room.roomID]"
            :key="index" 
            class="condition-item"
            @click="openEditModal(room.roomID, condition, index)" 
          >
            <div>
            <strong>{{ condition.variable }} </strong> {{ condition.lower_bound }} to {{ condition.upper_bound }}
            </div>
            <font-awesome-icon 
              :icon="faTrash" 
              class="delete-icon" 
              @click.stop.prevent="removeCondition(room.roomID, index)" 
            />
          </li>
        </ul>
      </div>

      <!-- Condition Type & Range in One Row -->
      <div class="condition-row">
        <label>
          Condition Type:
          <select v-model="selectedConditionType[room.roomID]">
            <option v-for="type in conditionTypes" :key="type" :value="type">{{ type }}</option>
          </select>
        </label>

        <label v-if="selectedConditionType[room.roomID]">
          {{ selectedConditionType[room.roomID] }} Range:

          <div class="range-container">
          <input type="number" 
                 @input="updatePendingCondition(room.roomID, selectedConditionType[room.roomID], 'min', $event.target.valueAsNumber)" />
          to
          <input type="number" 
                 @input="updatePendingCondition(room.roomID, selectedConditionType[room.roomID], 'max', $event.target.valueAsNumber)" />
          </div>
        </label>
      </div>

      <!-- Authority & Severity in One Row -->
      <div class="condition-row">
        <label>
          Authority:
          <select v-model="selectedAuthority[room.roomID]" @change="updatePendingMessage(room.roomID, 'Authority', $event.target.value)">
            <option v-for="auth in authorities" :key="auth" :value="auth">{{ auth }}</option>
          </select>
        </label>

        <label>
          Severity:
          <select  v-model="selectedSeverity[room.roomID]" @change="updatePendingMessage(room.roomID, 'Severity', $event.target.value)">
            <option v-for="sev in severities" :key="sev" :value="sev">{{ sev }}</option>
          </select>
        </label>
      </div>

      <!-- Title & Summary in One Row -->
      <div class="condition-row">
        <label>
          Title (max 20 characters):
          <input 
            type="text"
            v-model.trim="pendingConditions[room.roomID].messages[0].Title"
            maxlength="20"
            @input="updatePendingMessage(room.roomID, 'Title', $event.target.value)" />
        </label>

        <label>
          Summary:
          <textarea 
            rows="1"
            v-model.trim="pendingConditions[room.roomID].messages[0].Summary"
            @input="updatePendingMessage(room.roomID, 'Summary', $event.target.value)">
          </textarea>
        </label>
      </div>

      <p v-if="pendingConditions[room.roomID]?.[selectedConditionType[room.roomID]]?.max < 
                pendingConditions[room.roomID]?.[selectedConditionType[room.roomID]]?.min" 
        class="error-message">
        ⚠️ Max value cannot be less than Min value.
      </p>

      <button @click="setCondition(room.roomID)" :disabled="!isConditionValid(room.roomID)">Set</button>
    </div>

    <ConditionEditModal 
      v-if="isEditModalOpen"
      :roomID="editRoomID"
      :condition="editCondition"
      :conditionTypes="conditionTypes"
      :index="editConditionIndex"
      @update-condition="updateCondition"
      @close="isEditModalOpen = false"
    />
  </div>
</template>

<style scoped>
.warning-message {
  background: var(--warning-bg) !important;
  color: var(--primary-light-text) !important;
  border: none;
  padding: 10px;
  text-align: center;
  border-radius: 8px;
  font-weight: bold;
}

.conditions-container {
  padding: 20px;
  border-radius: 10px;
  background: var(--primary-light-bg);
  border: 2px solid #568EA6;
}

.room-conditions {
  margin-bottom: 20px;
  padding: 15px;
  border-radius: 8px;
  background: var(--primary-light-bg); 
}

.existing-conditions {
  margin-top: 10px;
  padding: 10px;
  background: var(--primary-light-bg); 
  border-radius: 8px;
}

/* Style the heading */
.existing-conditions h5 {
  font-size: 16px;
  font-weight: bold;
  color: var(--primary-dark-text);
  margin-bottom: 8px;
}

/* Remove bullet points */
.existing-conditions ul {
  list-style: none; /* ✅ Removes default bullet points */
  padding: 0;
  margin: 0;
}

/* Style each condition item */
.condition-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px;
  background: var(--primary-light-bg);
  border-radius: 6px;
  border: 1px solid #CBD5E1;
  margin-bottom: 6px;
  transition: background 0.3s ease-in-out;
}

/* Add hover effect */
.condition-item:hover {
  background: var(--primary-light-bg-hover);
}

/* Trash icon styling */
.delete-icon {
  color: var(--warning-text);
  cursor: pointer;
  transition: color 0.3s ease-in-out;
}

.delete-icon:hover {
  color: var(--warning-text-hover);
}


label {
  font-weight: bold;
  font-size: 14px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}
li {
  text-decoration: none;
  padding: 0;
}
input, select, textarea {
  padding: 8px;
  border: 1px solid #CBD5E1;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: border 0.2s ease-in-out;
}

.condition-row {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.condition-row label {
  flex: 1;
}

.delete-icon {
  color: var(--warning-text);
  cursor: pointer;
  transition: color 0.3s ease-in-out;
}

.delete-icon:hover {
  color: var(--warning-text-hover);
}

button {
  background: var(--primary-bg);
  color: var(--primary-light-text);
  border: none;
  padding: 10px;
  font-weight: bold;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s ease-in-out;
  display: block;
  margin-top: 10px;
  width: 20%;
}

button:hover {
  background: var(--primary-bg-hover);
}
button:disabled{
  cursor: not-allowed;
}

.range-container{
  display: flex;
  flex-direction: row;
  gap: 10px;
}

@media (max-width: 768px) {
  .condition-row {
    flex-direction: column;
    gap: 10px;
  }
  .range-container {
    flex-direction: column;
  }
}

</style>
