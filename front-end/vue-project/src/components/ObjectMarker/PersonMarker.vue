<script setup lang="ts">
const props = defineProps({
  position: {
    type: Object,
    required: true,
  },
  color: {
    type: String,
    default: '#4caf50', // Default color for people markers
  },
});
</script>

<template>
  <div
    class="person-marker"
    :style="{ 
      top: props.position.top + 'px',
      left: props.position.left + 'px',
      backgroundColor: props.color
    }"
  ></div>
</template>

<style scoped>
.person-marker {
  position: absolute;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
}
</style>
