<script setup lang="ts">
import OverlayArea from './OverlayArea.vue';
import { reactive, ref } from 'vue';

// Reactive overlay areas
const overlayAreas = reactive([
  { label: 'Area 1', color: '#F18C8E', position: { top: 50, left: 50, width: 200, height: 100 } },
  { label: 'Area 2', color: '#F0B7A4', position: { top: 200, left: 100, width: 150, height: 150 } },
  { label: 'Area 3', color: '#F1D1B5', position: { top: 400, left: 50, width: 250, height: 150 } },
  { label: 'Area 4', color: '#568EA6', position: { top: 300, left: 300, width: 200, height: 200 } },
]);

// Zoom level and map position state
const zoomLevel = ref(1);
const mapPosition = ref({ x: 0, y: 0 });

// Zoom controls
const zoomIn = () => {
  if (zoomLevel.value < 2) zoomLevel.value += 0.1;
};

const zoomOut = () => {
  if (zoomLevel.value > 0.5) zoomLevel.value -= 0.1;
};

// Handle scrolling for panning
const handleScroll = (event) => {
  event.preventDefault(); // Prevent the default scrolling behavior
  mapPosition.value = {
    x: mapPosition.value.x - event.deltaX,
    y: mapPosition.value.y - event.deltaY,
  };
};
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
    >
      <div
        class="airport-map"
        :style="{
          transform: `scale(${zoomLevel}) translate(${mapPosition.x}px, ${mapPosition.y}px)`,
        }"
      >
        <img src="@/assets/terminal-map.png" alt="Airport Map" class="map" />
        <OverlayArea
          v-for="(area, index) in overlayAreas"
          :key="index"
          v-model:position="area.position"
          :label="area.label"
          :color="area.color"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.airport-map-container {
  position: relative;
  width: 100%;
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

.airport-map {
  position: relative;
  transform-origin: center center;
  transition: transform 0.05s ease-in-out;
  border: 2px solid black;
}

.map {
  width: 100%;
  height: auto;
  object-fit: contain;
}
</style>
