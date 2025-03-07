<script setup lang="ts">
import { ref, computed, shallowReactive, PropType} from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faExclamationTriangle} from '@fortawesome/free-solid-svg-icons';
import { handleWarningButtonPressed } from '@/utils/helper/warningUtils';
import { usePresetLocalCache } from '../stores/presetLocalCache';
import {sensorMapping, sensors} from "../stores/sensorTypeStore";
import PersonMarker from "./ObjectMarker/PersonMarker.vue"
import LuggageMarker from "./ObjectMarker/LuggageMarker.vue";

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
  warnings: {
    type: Array as PropType<{ Title: string; Location: string; Severity: string; Summary: string }[]>,
    default: () => [],
  },
  enabledSensors: Array, 
  showDisconnected: Boolean, 
  showAll: Boolean,
});
console.log(props.enabledSensors);
const presetCache = usePresetLocalCache();
const getAreaKey = (label: string): string | null => {
  if (!label || !label.match) {
    return null;
  }
  const match = label.match(/\d+/);
  return match ? match[0] : null;
};

const filteredSensors = computed(() => {
  const areaKey = getAreaKey(props.label);
  const connectedAreaSet = presetCache.connectedSensors.get(areaKey) || new Set();

  if (props.showAll) {
    // When "All" is toggled, show only selected sensor types
    return sensors.value
      .filter(sensor => props.enabledSensors.includes(sensor.name)) // Only selected sensors
      .map(sensor => sensor.name);
  } else if (props.showDisconnected) {
    // When "Disconnected" is toggled, show only disconnected sensors of selected types
    return sensors.value
      .filter(sensor => !connectedAreaSet.has(sensor.name) && props.enabledSensors.includes(sensor.name))
      .map(sensor => sensor.name);
  }
  
  // Fallback: return only selected sensor types
  return sensors.value
    .filter(sensor => props.enabledSensors.includes(sensor.name))
    .map(sensor => sensor.name);
});

/**
 * Limit the number of displayed sensors based on area size.
 * If the box is too small, show an ellipsis "..." instead of overflowing icons.
 */
const displayedSensors = computed(() => {
  const iconWidth = 60; // match max-width in CSS
  const iconHeight = 60; // match max-height in CSS

  // Compute maximum columns and rows that can fit in the overlay area.
  const maxColumns = Math.floor(props.position.width / iconWidth);
  const maxRows = Math.floor(props.position.height / iconHeight);

  // Get the connection info for this area.
  const areaKey = getAreaKey(props.label);
  const connectedAreaSet = presetCache.connectedSensors.get(areaKey) || new Set();

  // Map filtered sensor names into an array of sensor objects that include connection state.
  const sensorsWithState = filteredSensors.value.map(sensor => ({
    name: sensor,
    disconnected: !connectedAreaSet.has(sensor)
  }));

  // Partition the sensors into rows based on maxColumns.
  const rows = [];
  for (let i = 0; i < sensorsWithState.length; i += maxColumns) {
    rows.push(sensorsWithState.slice(i, i + maxColumns));
  }

  // If the total number of rows exceeds the maximum allowed by height...
  if (rows.length > maxRows) {
    // For the last allowed row, take only up to (maxColumns - 1) items and add ellipsis.
    const allowedLastRow = rows[maxRows - 1].slice(0, maxColumns - 1);
    allowedLastRow.push({ name: 'ellipsis', disconnected: false });

    // Keep only the rows that fit.
    const allowedRows = rows.slice(0, maxRows - 1);
    allowedRows.push(allowedLastRow);

    // Flatten the grid back to an array.
    return allowedRows.flat();
  }

  // If we do not exceed the maximum rows, return the full list.
  return sensorsWithState;
});

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

const hasWarnings = computed(() => props.warnings.length > 0);

const onWarningButtonClick = () => {
  handleWarningButtonPressed(props.label, props.warnings);
};
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
  const minWidth = 50; // set the min widht so that the resize doesn't fall below
  const minHeight = 50; // set the min height so that the resize doesn't fall below
  if (!props.editMode) return;
  if (resizing.value) {
    const clientX = event instanceof MouseEvent ? event.clientX : event.touches[0].clientX;
    const clientY = event instanceof MouseEvent ? event.clientY : event.touches[0].clientY;
    
    const newWidth = Math.max(minWidth, props.position.width + (clientX - resizeStart.value.x) / props.zoomLevel);
    const newHeight = Math.max(minHeight, props.position.height + (clientY - resizeStart.value.y) / props.zoomLevel);

    emit('update:position', {
      ...props.position,
      width: newWidth,
      height: newHeight,
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


const getSensorStyle = () => {
  const minDimension = Math.min(props.position.width, props.position.height);
  return {
    fontSize: minDimension < 60 ? '8px' : minDimension < 100 ? '12px' : '14px',  
    padding: minDimension < 60 ? '2px' : '5px', 
    minWidth: minDimension < 60 ? '25px' : '40px', 
  };
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
  <!--
    <button 
      v-if="hasWarnings"
      class="warning-btn"
      @click="onWarningButtonClick"
    >
      <font-awesome-icon :icon="faExclamationTriangle" />
    </button>
  -->
    <div class="d-flex flex-column">
      <span class="overlay-area-label">{{ label }}</span>

      <div class="sensor-container">
        <div 
          v-for="sensor in displayedSensors" 
          :key="sensor.name" 
          class="sensor-item"
          :class="{ 'disconnected-sensor': sensor.disconnected }" 
          :style="getSensorStyle(sensor)"
        >
          <font-awesome-icon 
            v-if="sensor.name !== 'ellipsis'"
            :icon="sensorMapping[sensor.name]?.icon || 'question'"
            class="sensor-icon"
          />
          <span v-else class="ellipsis">...</span>
        </div>
      </div>
    </div>

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
  padding: 20px;
  text-align: center;
}

.overlay-area:active {
  cursor: grabbing;
}

.warning-btn {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  background: red;
  color: white;
  border: none;
  padding: 5px 0;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  z-index: 100;
}
.warning-btn:hover {
  background: darkred;
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
.sensor-container {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-start;
  width: 100%;  /* Ensure it fills the overlay-area */
  height: 100%;
  padding: 2px; /* Adjusted padding to avoid overflow */
  gap: 2px;
  overflow: hidden; /* Prevents overflow */
}

.sensor-item {
  display: flex;
  align-items: center;
  justify-content: center;
  width: calc(100% / 5); /* Ensures items fit dynamically */
  height: calc(100% / 3); /* Adjusted for aspect ratio */
  min-width: 15px; /* Smallest possible size */
  min-height: 15px;
  max-width: 40px;
  max-height: 40px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 10px;
  font-size: clamp(8px, 2vw, 16px);
}

.disconnected-sensor {
  background: rgba(255, 0, 0, 0.8); 
  color: white;
}

.ellipsis {
  font-size: 14px;
  font-weight: bold;
  color: black;
  text-align: center;
}

.sensor-icon {
  font-size: clamp(8px, 2vw, 18px);
  color: black;
}

</style>