<script setup lang="ts">
import OverlayArea from './OverlayArea.vue';
import { ref, onMounted } from 'vue';

const props = defineProps({
  overlayAreasConstant: {
    type: Array,
    required: true,
  },
  overlayAreasData: {
    type: Array,
    required: true,
  },
});


// Zoom level and map position state
const zoomLevel = ref(0.9);
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
  user-select: none;
  filter: brightness(50%);
}
</style>
