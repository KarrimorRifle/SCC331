<script setup lang="ts">
import {LResize} from 'vue3-resizable';
import 'vue3-resizable/dist/index.css';
</script>

<template>
  <LResize
    :minWidth="500"
    :minHeight="500"
    :maxWidth="1000"
    :maxHeight="1000"
    :initialWidth="150"
    :initialHeight="150"
    :initialTop="50"
    :initialLeft="550"
    :cssUnit="'px'"
    :showPosition="true"
  >
    <slot />
  </LResize>
</template>

<style scoped>
.resizable-container {
  border: 1px solid #ccc;
  background-color: #f9f9f9;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
