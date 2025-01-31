<script setup lang="ts">
import { PropType, defineEmits, ref, watch } from 'vue';

// Props
const props = defineProps({
  userIds: {
    type: Array as PropType<number[]>,
    required: true,
  },
});

// Emits event to parent when users are selected/deselected
const emit = defineEmits(["update:selectedUsers"]);

// Local state for handling selections
const selectedUsers = ref<number[]>([...props.userIds]);
const selectAll = ref(true);

// Watch for changes in selectedUsers and update "Select All" status
watch(selectedUsers, (newValue) => {
  selectAll.value = newValue.length === props.userIds.length;
  emit("update:selectedUsers", newValue);
});

// Handle "Select All" checkbox
const toggleAllUsers = () => {
  if (selectAll.value) {
    selectedUsers.value = []; // Deselect all
  } else {
    selectedUsers.value = [...props.userIds]; // Select all
  }
};
</script>

<template>
  <div class="user-filter">
    <h2>User Selection</h2>

    <!-- Select All Checkbox -->
    <div class="checkbox-group">
      <input type="checkbox" id="select-all" @change="toggleAllUsers" :checked="selectAll" />
      <label for="select-all">Select All</label>
    </div>

    <div class="divider"></div>

    <!-- Individual User Checkboxes -->
    <div class="user-list">
      <div v-for="userId in userIds" :key="userId" class="checkbox-group">
        <input type="checkbox" :id="'user-' + userId" v-model="selectedUsers" :value="userId" />
        <label :for="'user-' + userId">User {{ userId }}</label>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Container Styling */
.user-filter {
  padding: 20px;
  margin: 20px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Title */
.user-filter h2 {
  font-size: 18px;
  color: #305F72;
  margin-bottom: 10px;
}

/* Divider */
.divider {
  height: 1px;
  background-color: #ddd;
  margin: 10px 0;
}

/* Checkbox Groups */
.checkbox-group {
  display: flex;
  align-items: center;
  padding: 8px;
  border-radius: 6px;
  transition: background 0.3s ease-in-out;
}

.checkbox-group:hover {
  background: #f1f1f1;
}

/* Checkbox Inputs */
.checkbox-group input {
  margin-right: 10px;
  accent-color: #F18C8E; /* Match color theme */
}

/* Checkbox Labels */
.checkbox-group label {
  font-size: 14px;
  color: #444;
  cursor: pointer;
  font-weight: bold;
}

/* User List */
.user-list {
  max-height: 200px;
  overflow-y: auto;
  padding-right: 5px;
}

</style>
