<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue';

// Define props and emits
const props = defineProps({
  label: String,
  color: String,
  position: {
    type: Object,
    default: () => ({ top: 0, left: 0, width: 100, height: 100 }),
  },
});

const emit = defineEmits(['update:position']);

// Local states
const dragging = ref(false);
const resizing = ref(false);
const dragOffset = ref({ x: 0, y: 0 });
const resizeStart = ref({ x: 0, y: 0 });

// Start Dragging
const startDrag = (event: MouseEvent) => {
  dragging.value = true;
  dragOffset.value = {
    x: event.clientX - props.position.left,
    y: event.clientY - props.position.top,
  };
};

// Perform Dragging
const drag = (event: MouseEvent) => {
  if (dragging.value) {
    emit('update:position', {
      ...props.position,
      top: event.clientY - dragOffset.value.y,
      left: event.clientX - dragOffset.value.x,
    });
  }
};

// End Dragging
const endDrag = () => {
  dragging.value = false;
};

// Start Resizing
const startResize = (event: MouseEvent) => {
  resizing.value = true;
  resizeStart.value = { x: event.clientX, y: event.clientY };

  // Add global event listeners
  window.addEventListener('mousemove', resize);
  window.addEventListener('mouseup', endResize);
};

// Perform Resizing
const resize = (event: MouseEvent) => {
  if (resizing.value) {
    emit('update:position', {
      ...props.position,
      width: props.position.width + (event.clientX - resizeStart.value.x),
      height: props.position.height + (event.clientY - resizeStart.value.y),
    });
    resizeStart.value = { x: event.clientX, y: event.clientY };
  }
};

// End Resizing
const endResize = () => {
  resizing.value = false;

  // Remove global event listeners
  window.removeEventListener('mousemove', resize);
  window.removeEventListener('mouseup', endResize);
};
</script>

<template>
  <div
    class="overlay-area"
    :style="{ 
      top: props.position.top + 'px',
      left: props.position.left + 'px',
      width: props.position.width + 'px',
      height: props.position.height + 'px',
      backgroundColor: color,
    }"
    @mousedown="startDrag"
    @mousemove="drag"
    @mouseup="endDrag"
    @mouseleave="endDrag"
  >
    <span>{{ label }}</span>
    <!-- Resize Handle -->
    <div
      class="resize-handle"
      @mousedown.stop="startResize"
    ></div>
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
  cursor: grab;
}

.overlay-area:active {
  cursor: grabbing;
}

.resize-handle {
  position: absolute;
  width: 10px;
  height: 10px;
  bottom: 0;
  right: 0;
  background: #000;
  cursor: se-resize;
}
</style>
