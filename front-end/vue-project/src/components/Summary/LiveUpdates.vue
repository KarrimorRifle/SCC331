<script setup lang="ts">
import { ref } from 'vue';

const updates = ref([
  'Person 1 moved to Area 2',
  'Luggage 3 detected in Area 1',
  'Person 5 left Area 4',
]);

const addUpdate = (newUpdate: string) => {
  updates.value.unshift(newUpdate); // Add new updates to the top
};
</script>

<template>
  <div class="live-updates">
    <h2>Live Updates</h2>
    <ul>
      <li v-for="(update, index) in updates" :key="index">{{ update }}</li>
    </ul>
  </div>
</template>

<style scoped>
.live-updates {
  padding: 20px;
  background-color: #f8f8ff;
  border-top: 1px solid #ccc;
}

.live-updates h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.live-updates ul {
  list-style: none;
  padding: 0;
  margin-top: 10px;
}

.live-updates li {
  margin-bottom: 5px;
  font-size: 14px;
  color: #666;
}
</style>
