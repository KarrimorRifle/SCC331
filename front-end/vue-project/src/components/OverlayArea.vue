<script setup lang="ts">
import { defineProps } from 'vue';

defineProps({
  label: String,
  color: String,
  position: {
    type: Object,
    default: () => ({ top: 0, left: 0, width: 100, height: 100 }),
  },
});
</script>

<template>
  <div
    class="overlay-area"
    :style="{ 
      top: position.top + 'px',
      left: position.left + 'px',
      width: position.width + 'px',
      height: position.height + 'px',
      backgroundColor: color,
    }"
  >
    <span>{{ label }}</span>
  </div>
</template>

<style scoped>
.overlay-area {
  position: absolute;
  opacity: 0.5;
  border: 1px solid #000;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
