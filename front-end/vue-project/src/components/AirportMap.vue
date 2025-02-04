<script setup lang="ts">
import OverlayArea from './OverlayArea.vue';
import { ref, onMounted, onUnmounted, watch } from 'vue';

const props = defineProps({
  overlayAreasConstant: {
    type: Array,
    required: true,
  },
  overlayAreasData: {
    type: Object,
    required: true,
  },
});

// Zoom level and map position state
const zoomLevel = ref(0.9);
const mapPosition = ref({ x: 0, y: 0 });
const isDragging = ref(false);
const dragStart = ref({ x: 0, y: 0 });
const isZooming = ref(false);

// Zoom controls
const zoomIn = (ease?: boolean) => {
  if (zoomLevel.value < 2) {
    zoomLevel.value += 0.1;
    isZooming.value = ease ? true : false;
  }
};

const zoomOut = (ease?: boolean) => {
  if (zoomLevel.value > 0.5) {
    zoomLevel.value -= 0.1;
    isZooming.value = ease ? true : false;
  }
};

// Handle scrolling for zooming
const handleScroll = (event) => {
  event.preventDefault(); // Prevent the default scrolling behavior
  if (event.deltaY < 0) {
    zoomIn(false);
  } else {
    zoomOut(false);
  }
};

// Handle dragging start
const handleMouseDown = (event) => {
  // Check if the target is an OverlayArea
  if (event.target.closest('.overlay-area')) {
    return;
  }
  isDragging.value = true;
  dragStart.value = { x: event.clientX, y: event.clientY };
};

// Handle dragging
const handleMouseMove = (event) => {
  if (isDragging.value) {
    const speedFactor = 1.3; // Adjust this factor to make the dragging faster
    mapPosition.value = {
      x: mapPosition.value.x + (event.clientX - dragStart.value.x) * speedFactor / zoomLevel.value,
      y: mapPosition.value.y + (event.clientY - dragStart.value.y) * speedFactor / zoomLevel.value,
    };
    dragStart.value = { x: event.clientX, y: event.clientY };
  }
};

// Handle dragging end
const handleMouseUp = () => {
  isDragging.value = false;
};

// Add event listeners for dragging
onMounted(() => {
  window.addEventListener('mousemove', handleMouseMove);
  window.addEventListener('mouseup', handleMouseUp);
});

onUnmounted(() => {
  window.removeEventListener('mousemove', handleMouseMove);
  window.removeEventListener('mouseup', handleMouseUp);
});

// Watch for zoom level changes to reset isZooming after transition
watch(zoomLevel, () => {
  setTimeout(() => {
    isZooming.value = false;
  }, 120); // Match the transition duration
});
</script>

<template>
  <div class="airport-map-container">
    <div class="zoom-controls">
      <button @click="zoomOut">-</button>
      <button @click="zoomIn">+</button>
    </div>
    <!-- Add scroll event listener -->
    <div
      class="airport-map-wrapper"
      @wheel="handleScroll"
      @mousedown="handleMouseDown"
    >
      <div
        class="airport-map"
        :class="{ 'zooming': isZooming }"
        :style="{
          transform: `scale(${zoomLevel}) translate(${mapPosition.x}px, ${mapPosition.y}px)`,
        }"
      >
        <img src="@/assets/terminal-map.png" alt="Airport Map" class="map" @dragstart.prevent/>
        <OverlayArea
          v-for="(area, index) in props.overlayAreasConstant"
          :key="index"
          :position="area.position"
          :label="area.label"
          :color="area.color"
          :zoomLevel="zoomLevel"
          :data="props.overlayAreasData"
          @update:position="(newPosition) => overlayAreasConstant[index].position = newPosition"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.airport-map-container {
  position: relative;
  height: 100%;
  overflow: hidden;
  background-color: #f8f8ff;
}

.zoom-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1000;
  display: flex;
  gap: 10px;
}

.zoom-controls button {
  background-color: #568ea6;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
}

.zoom-controls button:hover {
  background-color: #305f72;
}

.airport-map-wrapper {
  width: 100%;
  height: 100%;
  cursor: grab;
  overflow: hidden; /* Ensure the map doesn't go out of bounds */
}

.airport-map-wrapper:active {
  cursor: grabbing;
}

.airport-map {
  position: relative;
  transform-origin: center center;
}

.airport-map.zooming {
  transition: transform 0.12s ease-in;
}

.map {
  object-fit: contain;
  user-select: none;
  filter: brightness(50%);
  border: 2px solid black;
}
</style>