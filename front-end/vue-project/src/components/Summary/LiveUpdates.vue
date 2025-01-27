<script setup lang="ts">
import { PropType, defineEmits } from 'vue';

const props = defineProps({
  updates: {
    type: Array as PropType<string[]>,
    required: true,
  },
});

const emit = defineEmits(['add-update']);

const addUpdate = (newUpdate: string) => {
  emit('add-update', newUpdate); 
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
