<script setup lang="ts">
import { defineProps, defineEmits, ref, watch } from "vue";
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faTrash } from '@fortawesome/free-solid-svg-icons';

const props = defineProps({
  selectedRooms: Array as () => { label: string; roomID: string }[],
  conditions: Object, // Receive conditions from the parent
});

const emit = defineEmits(["updateConditions"]);

// List of possible condition types
const conditionTypes = ["Temperature", "Person", "Luggage", "Light Level"];
const selectedConditionType = ref<{ [key: string]: string }>({});
const pendingConditions = ref<Object>({});


const updatePendingCondition = (roomID: string, conditionType: string, key: "min" | "max", value: number) => {
  if (!pendingConditions.value[roomID]) {
    pendingConditions.value[roomID] = {};
  }

  if (!pendingConditions.value[roomID][conditionType]) {
    pendingConditions.value[roomID][conditionType] = { min: null, max: null };
  }

  pendingConditions.value[roomID][conditionType][key] = value;
};

const setCondition = (roomID: string) => {
  const conditionType = selectedConditionType.value[roomID];

  if (!conditionType || !pendingConditions.value[roomID]?.[conditionType]) return;

  const { min, max } = pendingConditions.value[roomID][conditionType];

  if (min === null || max === null) {
    alert("Please enter both min and max values.");
    return;
  }

  if (max <= min) {
    alert("Max value cannot be less than Min value.");
    return;
  }

  if (!props.conditions[roomID]) {
    props.conditions[roomID] = { conditions: [], messages: [] };
  }

  // Check if the condition type already exists
  const existingCondition = props.conditions[roomID].conditions.find(c => c.variable === conditionType);
  if (existingCondition) {
    existingCondition.lower_bound = min;
    existingCondition.upper_bound = max;
  } else {
    props.conditions[roomID].conditions.push({
      variable: conditionType,
      lower_bound: min,
      upper_bound: max,
    });
  }

  // **Only add a message if it doesn't exist yet**
  if (!props.conditions[roomID].messages.find(m => m.Title.includes(conditionType))) {
    props.conditions[roomID].messages.push({
      Authority: "everyone",
      Title: `Warning for ${roomID} - ${conditionType}`,
      Location: roomID,
      Severity: "warning",
      Summary: `${conditionType} should be between ${min} and ${max}.`,
    });
  }

  emit("updateConditions", { ...props.conditions });

  // Clear pending input
  delete pendingConditions.value[roomID][conditionType];

  console.log(props.conditions);
};

const removeCondition = (roomID: string, conditionType: string) => {
  if (props.conditions[roomID] && props.conditions[roomID][conditionType]) {
    delete props.conditions[roomID][conditionType];

    if (Object.keys(props.conditions[roomID]).length === 0) {
      delete props.conditions[roomID];
    }

    emit("updateConditions", { ...props.conditions });
  }
};

watch(() => props.selectedRooms, (newRooms) => {
  newRooms.forEach((room) => {
    if (!pendingConditions.value[room.roomID]) {
      pendingConditions.value[room.roomID] = {};
    }
  });

  Object.keys(pendingConditions.value).forEach((roomID) => {
    if (!newRooms.some(room => room.roomID === roomID)) {
      delete pendingConditions.value[roomID];
    }
  });
}, { deep: true, immediate: true });

</script>

<template>
  <div class="conditions-container">
    <h3>Set Warning Conditions</h3>

    <div v-for="room in props.selectedRooms" :key="room.roomID" class="room-conditions">
      <h4>{{ room.label }}</h4>

      <!-- Display Set Conditions -->
      <div v-if="props.conditions[room.roomID] && Object.keys(props.conditions[room.roomID]).length > 0">
        <h5>Set Conditions:</h5>
        <ul>
          <li v-for="(values, conditionType) in props.conditions[room.roomID]" 
              :key="conditionType" class="condition-item">
            <font-awesome-icon 
              :icon="faTrash" 
              class="delete-icon" 
              @click="removeCondition(room.roomID, conditionType)"
            />
            <strong>{{ conditionType }}:</strong> {{ values.min }} to {{ values.max }}
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
                 :value="pendingConditions[room.roomID]?.[selectedConditionType[room.roomID]]?.min || ''" 
                 @input="updatePendingCondition(room.roomID, selectedConditionType[room.roomID], 'min', $event.target.valueAsNumber)" />
          to
          <input type="number" 
                 :value="pendingConditions[room.roomID]?.[selectedConditionType[room.roomID]]?.max || ''" 
                 @input="updatePendingCondition(room.roomID, selectedConditionType[room.roomID], 'max', $event.target.valueAsNumber)" />
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
