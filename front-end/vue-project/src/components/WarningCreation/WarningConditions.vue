<script setup lang="ts">
import { defineProps, defineEmits, ref, watch } from "vue";
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faTrash } from '@fortawesome/free-solid-svg-icons';

const props = defineProps({
  selectedWarning: Object, 
  selectedRooms: Array as () => { label: string; roomID: string }[],
  conditions: Object, 
  createWarning: Function, 
});

const emit = defineEmits(["updateConditions"]);

// List of possible condition types
const conditionTypes = ["Temperature", "Person", "Luggage", "Light Level"];
const authorities = ["admin", "security", "staff", "users", "everyone"];
const severities = ["doomed", "danger", "warning", "notification"];

const selectedAuthority = ref<{ [key: string]: string }>({});
const selectedSeverity = ref<{ [key: string]: string }>({});
const selectedConditionType = ref<{ [key: string]: string }>({});
const pendingConditions = ref<Record<string, {
  conditions: { variable: string | null; lower_bound: number | null; upper_bound: number | null }[];
  messages: { Authority: string | null; Location: string | null; Severity: string | null; Summary: string | null; Title: string | null }[];
  roomID: string;
}>>({});


const updatePendingCondition = (roomID: string, conditionType: string, key: "min" | "max", value: number) => {
  if (!pendingConditions.value[roomID]) return;

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


const updatePendingMessage = (roomID: string, key: "Authority" | "Severity", value: string) => {
  if (!pendingConditions.value[roomID]) {
    return;
  }
  if (!pendingConditions.value[roomID].messages || pendingConditions.value[roomID].messages.length === 0) {
    pendingConditions.value[roomID].messages = [{
      Authority: null,
      Location: roomID,
      Severity: null,
      Summary: null,
      Title: null,
    }];
  }else {
    pendingConditions.value[roomID].messages[0].Location = roomID;
  }
  pendingConditions.value[roomID].messages[0][key] = value;
  pendingConditions.value = { ...pendingConditions.value };

  console.log(`Updated ${key} for room ${roomID}:`, pendingConditions.value[roomID].messages);
};

const setCondition = (roomID: string) => {
  const conditionType = selectedConditionType.value[roomID];
  if (!conditionType) return;

  console.log(pendingConditions);

  emit("updateConditions", { ...pendingConditions.value });

  delete pendingConditions.value[roomID][conditionType];

  console.log(props.conditions);
};

const removeCondition = (roomID: string, conditionIndex: number) => {
  if (props.conditions[roomID]) {
    props.conditions[roomID].conditions.splice(conditionIndex, 1);

    if (props.conditions[roomID].conditions.length === 0) {
      delete props.conditions[roomID];
    }

    emit("updateConditions", { ...props.conditions });
  }
};

watch(
  () => props.selectedRooms,
  (newRooms) => {
    newRooms.forEach((room) => {
      if (!pendingConditions.value[room.roomID]) {
        pendingConditions.value[room.roomID] = {
          conditions: [
            { variable: null, lower_bound: null, upper_bound: null }
          ],
          messages: [
            { Authority: null, Location: null, Severity: null, Summary: null, Title: null }
          ],
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
  <div class="conditions-container">
    <h3>Set Warning Conditions</h3>
    <div v-for="room in props.selectedRooms" :key="room.roomID" class="room-conditions">
      <h4>{{ room.label }}</h4>

      <div v-if="props.conditions[room.roomID]?.conditions.length">
        <h5>Existing Conditions:</h5>
        <ul>
          <li v-for="(condition, index) in props.conditions[room.roomID].conditions"
              :key="index" class="condition-item">
            <font-awesome-icon 
              :icon="faTrash" 
              class="delete-icon" 
              @click="removeCondition(room.roomID, index)"
            />
            <strong>{{ condition.variable }}:</strong> {{ condition.lower_bound }} to {{ condition.upper_bound }}
          </li>
        </ul>
      </div>

      <!-- Select Condition Type -->
      <label>
        Condition Type:
        <select v-model="selectedConditionType[room.roomID]">
          <option v-for="type in conditionTypes" :key="type" :value="type">{{ type }}</option>
        </select>
      </label>

      <!-- Dynamic Condition Input Fields -->
      <div v-if="selectedConditionType[room.roomID]">
        <label>
          {{ selectedConditionType[room.roomID] }} Range:
          <input type="number" 
                 @input="updatePendingCondition(room.roomID, selectedConditionType[room.roomID], 'min', $event.target.valueAsNumber)" />
          to
          <input type="number" 
                 @input="updatePendingCondition(room.roomID, selectedConditionType[room.roomID], 'max', $event.target.valueAsNumber)" />
        </label>
        
        <label>
          Authority:
          <select @change="updatePendingMessage(room.roomID, 'Authority', $event.target.value)">
            <option v-for="auth in authorities" :key="auth" :value="auth">{{ auth }}</option>
          </select>
        </label>

        <label>
          Severity:
          <select @change="updatePendingMessage(room.roomID, 'Severity', $event.target.value)">
            <option v-for="sev in severities" :key="sev" :value="sev">{{ sev }}</option>
          </select>
        </label>

        <p v-if="pendingConditions[room.roomID]?.[selectedConditionType[room.roomID]]?.max < 
                  pendingConditions[room.roomID]?.[selectedConditionType[room.roomID]]?.min" 
          class="error-message">
          ⚠️ Max value cannot be less than Min value.
        </p>
      </div>

      <button @click="setCondition(room.roomID)">Set Condition</button>
    </div>
  </div>
</template>
