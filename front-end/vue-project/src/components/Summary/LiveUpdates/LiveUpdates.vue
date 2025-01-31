<script setup lang="ts">
import { PropType, ref, computed } from 'vue';
import LiveUpdatesFilterBar from './LiveUpdatesFilterBar.vue'; // Import the new filter component

// Props for user IDs and updates
const props = defineProps({
  userIds: {
    type: Array as PropType<number[]>,
    required: true,
  },
  updates: {
    type: Object as PropType<Record<number, { logged_at: string; roomID: number }[]>>,
    required: true,
  },
});

// Reactive state for selected users
const selectedUsers = ref<number[]>([...props.userIds]);

// Reactive state for filter visibility
const showFilterBar = ref(true);

// Compute filtered updates based on selected users
const filteredUpdates = computed(() => {
  return Object.entries(props.updates)
    .filter(([userId]) => selectedUsers.value.includes(Number(userId))) // Filter by selected users
    .map(([userId, updates]) => ({
      userId,
      updates,
    }));
});

// Toggle filter bar visibility
const toggleFilterVisibility = () => {
  showFilterBar.value = !showFilterBar.value;
};
</script>

<template>
  <div class="live-updates">

    <div class="live-updates-header">
      <h1>Live Updates</h1>

      <!-- Toggle Filter Button -->
      <button @click="toggleFilterVisibility" class="toggle-button">
        {{ showFilterBar ? "Hide Filter" : "Show Filter" }}
      </button>
    </div>


    <!-- User Selection Filter (Togglable) -->
    <LiveUpdatesFilterBar v-if="showFilterBar" :userIds="userIds" v-model:selectedUsers="selectedUsers" />

    <!-- Display Updates -->
    <ul class="update-list">
      <li v-for="({ userId, updates }) in filteredUpdates" :key="userId">
        <h3>User {{ userId }}</h3>
        <ul class="user-updates">
          <li v-for="(update, index) in updates" :key="index" class="update-item">
            <span class="timestamp">{{ new Date(update.logged_at).toLocaleString() }}</span> -
            <span class="room">Room ID: {{ update.roomID }}</span>
          </li>
        </ul>
      </li>
    </ul>
  </div>
</template>

<style scoped>
/* General Layout */
.live-updates {
  padding: 20px;
  background-color: #f8f8ff;
  border-top: 1px solid #ccc;
  color: black;
}
.live-updates-header{
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

/* Toggle Button */
.toggle-button {
  background-color: #568EA6;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 5px;
  font-size: 14px;
  cursor: pointer;
  margin-bottom: 10px;
}

.toggle-button:hover {
  background-color: #305F72;
}

/* Update List */
.update-list {
  list-style: none;
  padding: 0;
}

.user-updates {
  list-style: none;
  padding-left: 15px;
}

h3 {
  color: #305F72;
  margin-bottom: 5px;
}

.update-item {
  background: #f1f1f1;
  margin-bottom: 5px;
  padding: 8px;
  border-radius: 5px;
  font-size: 14px;
}

.timestamp {
  font-weight: bold;
  color: #F18C8E;
}

.room {
  color: #568EA6;
}
</style>
