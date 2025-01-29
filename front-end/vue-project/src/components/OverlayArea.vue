<script setup lang="ts">
import PersonMarker from "./ObjectMarker/PersonMarker.vue"
import LuggageMarker from "./ObjectMarker/LuggageMarker.vue";
import { ref } from 'vue';

// Define props and emits
const props = defineProps({
  label: String,
  color: String,
  position: {
    type: Object,
    default: () => ({ top: 0, left: 0, width: 100, height: 100 }),
  },
  zoomLevel: {
    type: Number,
    default: 1,
  },
  data: {
    type: Array,
    default: () => [],
  }
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
  // Calculate drag offset, accounting for the zoom level
  dragOffset.value = {
    x: (event.clientX - props.position.left * props.zoomLevel),
    y: (event.clientY - props.position.top * props.zoomLevel),
  };
};

// Perform Dragging
const drag = (event: MouseEvent) => {
  if (dragging.value) {
    emit('update:position', {
      ...props.position,
      // Normalize the position changes by the zoom level
      top: (event.clientY - dragOffset.value.y) / props.zoomLevel,
      left: (event.clientX - dragOffset.value.x) / props.zoomLevel,
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
      // Adjust resizing for zoom level
      width: props.position.width + (event.clientX - resizeStart.value.x) / props.zoomLevel,
      height: props.position.height + (event.clientY - resizeStart.value.y) / props.zoomLevel,
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
    <span class="overlay-area-label">{{ label }}</span>

    <PersonMarker
      v-for="(person, index) in props.data.people"
      :key="'person-' + index"
      :position="person.position"
      :color="person.color"
    />

    <LuggageMarker
      v-for="(item, index) in props.data.luggage"
      :key="'luggage-' + index"
      :position="item.position"
      :color="item.color"
    />

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
  overflow: hidden;
}

.overlay-area:active {
  cursor: grabbing;
}

.overlay-area-label{
    user-select: none;
    color: black;
    font-weight: bold;
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
