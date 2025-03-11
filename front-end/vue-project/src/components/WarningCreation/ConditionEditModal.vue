<script setup lang="ts">
import { defineProps, defineEmits, ref } from "vue";

const props = defineProps({
  roomID: String,
  condition: Object,
  index: Number,
  conditionTypes: Array, 
});

const emit = defineEmits(["update-condition", "close"]);

const editedCondition = ref({ ...props.condition });

const saveChanges = () => {
  emit("update-condition", { 
    roomID: props.roomID, 
    index: props.index, 
    updatedCondition: editedCondition.value 
  });
};

</script>

<template>
  <div class="modal-overlay">
    <div class="modal-content">
      <h3>Edit Condition</h3>
      
      <label>
        Condition Type:
        <select v-model="editedCondition.variable">
          <option v-for="type in conditionTypes" :key="type" :value="type">{{ type }}</option>
        </select>
      </label>

      <label>
        Min Value:
        <input type="number" v-model.number="editedCondition.lower_bound" />
      </label>

      <label>
        Max Value:
        <input type="number" v-model.number="editedCondition.upper_bound" />
      </label>

      <div class="modal-buttons">
        <button @click="saveChanges">Update Condition</button>
        <button @click="$emit('close')">Cancel</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: var(--primary-light-bg);
  padding: 20px;
  border-radius: 8px;
  width: 400px;
  text-align: center;
}

.modal-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
}

button {
  background: var(--primary-bg);
  color: var(--primary-light-text);
  border: none;
  padding: 8px 12px;
  font-weight: bold;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s ease-in-out;
}

button:hover {
  background: var(--primary-bg-hover);
}

</style>