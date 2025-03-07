<script setup lang="ts">
const props = defineProps({
  title: {
    type: String,
    default: 'Live Summary',
  },
});
</script>

<template>
  <div class="summary-header">
    <h1>{{ props.title }}</h1>
    <p>This screen provides a live summary of the current locations of people and luggage in the airport.</p>
  </div>
</template>

<style scoped>
.summary-header {
  padding: 20px;
  background-color: var(--primary-light-bg);
  border-bottom: 1px solid #ccc;
  text-align: center;
}

.summary-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
  color: var(--primary-dark-text);
}

.summary-header p {
  margin-top: 10px;
  font-size: 14px;
  color: var(--primary-dark-text);
}
</style>
