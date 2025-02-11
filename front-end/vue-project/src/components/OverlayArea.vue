<script setup lang="ts">
import PersonMarker from "./ObjectMarker/PersonMarker.vue"
import LuggageMarker from "./ObjectMarker/LuggageMarker.vue";
import { ref, computed, shallowReactive } from 'vue';

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
    type: Object, 
    default: () => ({}),
  },
  editMode: {
    type: Boolean,
    required: true,
  },
});

const getAreaKey = (label: string): string | null => {
  if (!label || !label.match) {
    return null;
  }
  const match = label.match(/\d+/);
  return match ? match[0] : null;
};

const usersList = computed(() => {
  const key = getAreaKey(props.label);

  if (!key || !props.data[key]?.users?.id) return [];
  
  return props.data[key].users.id.map((userId, index) => ({
    id: userId,
    position: { top: 50 + index * 10, left: 20 + index * 10 },
  }));
});

const luggageList = computed(() => {
  const key = getAreaKey(props.label);
  if (!key || !props.data[key]?.luggage?.id) return [];

  return props.data[key].luggage.id.map((itemId, index) => ({
    id: itemId,
    position: { top: 50 + index * 10, left: 50 + index * 10 },
  }));
});

const emit = defineEmits(['update:position']);

// Local states
const dragging = ref(false);
const resizing = ref(false);
const dragOffset = ref({ x: 0, y: 0 });
const resizeStart = ref({ x: 0, y: 0 });

// Start Dragging
const startDrag = (event: MouseEvent | TouchEvent) => {
  if(!props.editMode) return;
  dragging.value = true;
  const clientX = event instanceof MouseEvent ? event.clientX : event.touches[0].clientX;
  const clientY = event instanceof MouseEvent ? event.clientY : event.touches[0].clientY;
  // Calculate drag offset, accounting for the zoom level
  dragOffset.value = {
    x: (clientX - props.position.left * props.zoomLevel),
    y: (clientY - props.position.top * props.zoomLevel),
  };
};

// Perform Dragging
const drag = (event: MouseEvent | TouchEvent) => {
  if(!props.editMode) return;
  if (dragging.value) {
    const clientX = event instanceof MouseEvent ? event.clientX : event.touches[0].clientX;
    const clientY = event instanceof MouseEvent ? event.clientY : event.touches[0].clientY;
    emit('update:position', {
      ...props.position,
      // Normalize the position changes by the zoom level
      top: (clientY - dragOffset.value.y) / props.zoomLevel,
      left: (clientX - dragOffset.value.x) / props.zoomLevel,
    });
  }
};

// End Dragging
const endDrag = () => {
  if(!props.editMode) return;
  dragging.value = false;
};

// Start Resizing
const startResize = (event: MouseEvent | TouchEvent) => {
  if(!props.editMode) return;
  resizing.value = true;
  const clientX = event instanceof MouseEvent ? event.clientX : event.touches[0].clientX;
  const clientY = event instanceof MouseEvent ? event.clientY : event.touches[0].clientY;
  resizeStart.value = { x: clientX, y: clientY };

  // Add global event listeners
  window.addEventListener('mousemove', resize);
  window.addEventListener('mouseup', endResize);
  window.addEventListener('touchmove', resize);
  window.addEventListener('touchend', endResize);
};

// Perform Resizing
const resize = (event: MouseEvent | TouchEvent) => {
  if(!props.editMode) return;
  if (resizing.value) {
    const clientX = event instanceof MouseEvent ? event.clientX : event.touches[0].clientX;
    const clientY = event instanceof MouseEvent ? event.clientY : event.touches[0].clientY;
    emit('update:position', {
      ...props.position,
      // Adjust resizing for zoom level
      width: props.position.width + (clientX - resizeStart.value.x) / props.zoomLevel,
      height: props.position.height + (clientY - resizeStart.value.y) / props.zoomLevel,
    });
    resizeStart.value = { x: clientX, y: clientY };
  }
};

// End Resizing
const endResize = () => {
  if(!props.editMode) return;
  resizing.value = false;

  // Remove global event listeners
  window.removeEventListener('mousemove', resize);
  window.removeEventListener('mouseup', endResize);
  window.removeEventListener('touchmove', resize);
  window.removeEventListener('touchend', endResize);
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
      backgroundColor: color + '7D',
      overflow: 'visible',
      pointerEvents: props.editMode ? 'auto' : 'none',
    }"
    @mousedown="startDrag"
    @mousemove="drag"
    @mouseup="endDrag"
    @mouseleave="endDrag"
    @touchstart="startDrag"
    @touchmove="drag"
    @touchend="endDrag"
  >
    <span class="overlay-area-label">{{ label }}</span>

    <PersonMarker
      v-for="(person, index) in usersList"
      :key="'person-' + index"
      :position="person.position"
      :color="person.color"
      :id="person.id"
    />

    <LuggageMarker
      v-for="(item, index) in luggageList"
      :key="'luggage-' + index"
      :position="item.position"
      :color="item.color"
    />

    <!-- Resize Handle -->
    <div
      class="resize-handle"
      v-if="props.editMode"
      @mousedown.stop="startResize"
      @touchstart.stop="startResize"
    ></div>
  </div>
</template>

<style scoped>
.overlay-area {
  position: absolute;
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
  background: #FFF;
  border: #000 2px solid;
  cursor: se-resize;
  position: absolute;
  bottom: -0.3em;
  right: -0.3rem;
  z-index: 100;
}
</style>