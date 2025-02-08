<script setup lang="ts">
import OverlayArea from './OverlayArea.vue';
import { ref, onMounted, onUnmounted, watch } from 'vue';
import type { boxAndData } from '@/utils/mapTypes';

const props = defineProps({
  modelValue: {
    type: Object as () => boxAndData,
    required: true,
  }
});

const emit = defineEmits(["update:modelValue"]);

const localValue = ref({ ...props.modelValue });

watch(() => props.modelValue, (newValue) => {
  localValue.value = { ...newValue };
});

watch(localValue, (newValue) => {
  emit('update:modelValue', newValue);
}, { deep: true });

const updateValue = () => {
  emit('update:modelValue', localValue.value);
};

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

const handleTouchStart = (event) => {
  if (event.target.closest('.overlay-area')) {
    return;
  }
  isDragging.value = true;
  const touch = event.touches[0];
  dragStart.value = { x: touch.clientX, y: touch.clientY };
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

const handleTouchMove = (event) => {
  if (isDragging.value) {
    const touch = event.touches[0];
    const speedFactor = 1.3; // Adjust this factor to make the dragging faster
    mapPosition.value = {
      x: mapPosition.value.x + (touch.clientX - dragStart.value.x) * speedFactor / zoomLevel.value,
      y: mapPosition.value.y + (touch.clientY - dragStart.value.y) * speedFactor / zoomLevel.value,
    };
    dragStart.value = { x: touch.clientX, y: touch.clientY };
  }
};

// Handle dragging end
const handleMouseUp = () => {
  isDragging.value = false;
};

const handleTouchEnd = () => {
  isDragging.value = false;
};

// Add event listeners for dragging
onMounted(() => {
  window.addEventListener('mousemove', handleMouseMove);
  window.addEventListener('mouseup', handleMouseUp);
  window.addEventListener('touchmove', handleTouchMove);
  window.addEventListener('touchend', handleTouchEnd);
});

onUnmounted(() => {
  window.removeEventListener('mousemove', handleMouseMove);
  window.removeEventListener('mouseup', handleMouseUp);
  window.removeEventListener('touchmove', handleTouchMove);
  window.removeEventListener('touchend', handleTouchEnd);
});

// Watch for zoom level changes to reset isZooming after transition
watch(zoomLevel, () => {
  setTimeout(() => {
    isZooming.value = false;
  }, 120); // Match the transition duration
});
</script>

<template>
  <div class="airport-map-container" id="">
    <div class="modal fade" id="staticBackdrop" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1" aria-labelledby="staticBackdropLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="staticBackdropLabel">Modal title</h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            ...
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button type="button" class="btn btn-primary">Understood</button>
          </div>
        </div>
      </div>
    </div>
    <div class="zoom-controls d-flex flex-column align-items-end" style="pointer-events: none;">
      <div class="preset-container card p-2">
        <div class="input-group" style="pointer-events: all;">
          <label class="input-group-text bg-dark text-light" for="inputGroupSelect01">Preset</label>
          <!-- add v-model and make it a v-if to change the name -->
          <select class="form-select" id="inputGroupSelect02" style="min-width: 20rem">
            <option selected>Choose...</option>
            <option value="1">One</option>
            <option value="2">Two</option>
            <option value="3">Three</option>
          </select>
        </div>
      </div>
      <div class="button-container d-flex flex-column align-items-end" style="pointer-events: all;">
        <button class="mb-1" @click="zoomIn">+</button>
        <button class="mb-1" @click="zoomOut">-</button>
        <div> <!--will add v-if-->
          <hr class="text-dark my-1" style="width: 100%; height: 3px;">
          <button class="mb-1 p-0 py-1 d-flex align-items-center justify-content-center">
            <img src="@/assets/pencil.svg" alt="" style="max-width: 1.5rem;">
          </button>
          <button class="p-0 py-1 d-flex align-items-center justify-content-center" data-bs-toggle="modal" data-bs-target="#staticBackdrop">
            <img src="@/assets/image.svg" alt="" style="max-width: 1.5rem;">
            <!-- Add a modal popout for this -->
          </button>
        </div>
      </div>
    </div>
    <!-- Add scroll event listener -->
    <div
      class="airport-map-wrapper"
      @wheel="handleScroll"
      @mousedown="handleMouseDown"
      @touchstart="handleTouchStart"
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
          v-for="([key, data]) in Object.entries(localValue).filter(([key, data]) => data.box)"
          :key="key"
          :position="data.box"
          :label="data.label"
          :color="data.box.colour"
          :zoomLevel="zoomLevel"
          :data="data.tracker"
          @update:position="(newPosition) => {
            localValue[key].box.height = newPosition.height
            localValue[key].box.width = newPosition.width
            localValue[key].box.top = newPosition.top
            localValue[key].box.left = newPosition.left
          }"
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

.zoom-controls > .button-container button {
  background-color: #568ea6;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
  width: 2rem;
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