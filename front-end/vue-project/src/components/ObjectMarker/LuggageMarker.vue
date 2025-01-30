<script setup lang="ts">
const props = defineProps({
  position: {
    type: Object,
    required: true,
  },
  color: {
    type: String,
    default: '#f44336', // Default color for luggage markers
  },
});
</script>

<template>
  <div
    class="luggage-marker"
    :style="{ 
      top: props.position.top + 'px',
      left: props.position.left + 'px',
      backgroundColor: props.color
    }"
  ></div>
</template>

<style scoped>
.luggage-marker {
  position: absolute;
  width: 12px;
  height: 12px;
  border-radius: 3px;
  border: 2px solid white;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
}
</style>
