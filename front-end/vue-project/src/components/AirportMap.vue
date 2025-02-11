<script setup lang="ts">
import OverlayArea from './OverlayArea.vue';
import NewPreset from './Maps/NewPreset.vue';
import ImageUpload from './Maps/ImageUpload.vue';
import { ref, onMounted, onUnmounted, watch } from 'vue';
import type { boxAndData, dataObject, presetListType, preset } from '@/utils/mapTypes';
import { Modal } from 'bootstrap';
import axios from 'axios';
import terminalMap from '@/assets/terminal-map.png';

const props = defineProps({
  modelValue: {
    type: Object as () => boxAndData,
    required: true,
  },
  presetList: {
    type: Object as () => presetListType,
    required: true,
  },
  canCreate: {
    type: Boolean,
    required: true,
  },
  canEdit: {
    type: Boolean,
    required: true,
  },
  settable: {
    type: Boolean,
    required: true,
  },
  defaultPresetId: {
    type: [Number, String],
    required: true,
  },
  currentPreset: {
    type: [Number, String],
    required: true,
  },
  backgroundImage: {
    type: String,
    default: ''
  },
  canDelete: {
    type: Boolean,
    required: true,
  },
  presetData: {
    type: Object as () => preset,
    required: true,
  },
  editMode: {
    type: Boolean,
    required: true
  }
});

const emit = defineEmits(["update:modelValue", "selectPreset", "getNewPreset", "setDefault", "newPreset", "newImage", "delete", "edit", "save", "cancel"]);

/** Update only the box data for a given key. */
const internalModelValue = ref<boxAndData>({ ...props.modelValue });

watch(
  () => props.modelValue,
  (newValue) => {
    internalModelValue.value = { ...newValue };
  },
  { deep: true }
);

function updateBox(key: string, newPosition: any) {
  const updated = { ...internalModelValue.value };
  if (!updated[key]) updated[key] = <dataObject>{};
  updated[key] = {
    ...updated[key],
    box: {
      ...updated[key].box,
      ...newPosition,
    },
  };
  internalModelValue.value = updated;
  emit("update:modelValue", updated);
}

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
const handleScroll = (event: WheelEvent) => {
  event.preventDefault(); // Prevent the default scrolling behavior
  if (event.deltaY < 0) {
    zoomIn(false);
  } else {
    zoomOut(false);
  }
};

// Handle dragging start
const handleMouseDown = (event: MouseEvent) => {
  // Check if the target is an OverlayArea
  if ((event.target as HTMLElement)?.closest('.overlay-area')) {
    return;
  }
  isDragging.value = true;
  dragStart.value = { x: event.clientX, y: event.clientY };
};

const handleTouchStart = (event: TouchEvent) => {
  if ((event.target as HTMLElement)?.closest('.overlay-area')) {
    return;
  }
  isDragging.value = true;
  const touch = event.touches[0];
  dragStart.value = { x: touch.clientX, y: touch.clientY };
};

// Handle dragging
const handleMouseMove = (event: MouseEvent) => {
  if (isDragging.value) {
    const speedFactor = 1.3; // Adjust this factor to make the dragging faster
    mapPosition.value = {
      x: mapPosition.value.x + (event.clientX - dragStart.value.x) * speedFactor / zoomLevel.value,
      y: mapPosition.value.y + (event.clientY - dragStart.value.y) * speedFactor / zoomLevel.value,
    };
    dragStart.value = { x: event.clientX, y: event.clientY };
  }
};

const handleTouchMove = (event: TouchEvent) => {
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

// Function to show the modal
const showModal = () => {
  const modalElement = document.getElementById('newPresetModal');
  if (modalElement) {
    const modal = new Modal(modalElement);
    modal.show();
  }
};

const updateMode = ref<boolean>(false);
</script>

<template>
  <div class="airport-map-container" id="">
    <div class="zoom-controls d-flex flex-column align-items-end" style="pointer-events: none;">
      <div class="preset-container card p-2">
        <div class="input-group" style="pointer-events: all;">
          <button v-if="props.settable" class="btn btn-success ms-2" @click="emit('setDefault')" for="inputGroupSelect01">Set Default</button>
          <label v-else class="input-group-text bg-dark text-light" for="inputGroupSelect01">Preset</label>
          <!-- add v-model and make it a v-if to change the name -->
          <select class="form-select" id="inputGroupSelect02" style="min-width: 20rem" @change="emit('selectPreset', $event.target.value)" :value="props.currentPreset">
            <option v-for="preset in presetList.presets" :value="preset.id" :key="preset.id">
              {{ preset.id === defaultPresetId ? `Default: ${preset.name}` : preset.name }}
            </option>
          </select>
        </div>
      </div>
      <div class="button-container d-flex flex-column align-items-end" style="pointer-events: all;">
        <button class="mb-1" @click="zoomIn(true)" title="Zoom in">+</button>
        <button class="mb-1" @click="zoomOut(true)" title="Zoom out">-</button>
        <hr class="text-dark my-1" style="width: 100%; height: 3px;" v-if="canEdit || canCreate">
        <div v-if="canEdit">
          <button class="mb-1 p-0 py-1 d-flex align-items-center justify-content-center" title="Edit preset" v-if="canDelete" @click="updateMode = true; showModal()">
            <img src="@/assets/cog.svg" alt="" style="max-width: 1.5rem;">
          </button>
          <button class="p-0 py-1 d-flex align-items-center justify-content-center mb-1" data-bs-toggle="modal" data-bs-target="#imageUploadModal" title="Upload image">
            <img src="@/assets/image.svg" alt="" style="max-width: 1.5rem;">
          </button>
        </div>
        <button v-if="canCreate"
          class="bg-success rounded-end text-light mb-1"
          style="font-weight: 600;"
          title="Create new preset"
          @click="updateMode = false; showModal()"
        >+</button>
        <div v-if="canEdit">
          <hr class="text-dark my-1" style="width: 100%; height: 3px;">
          <button
            v-if="!editMode"
            class="p-0 py-1 d-flex align-items-center justify-content-center mb-1"
            @click="emit('edit')"
            title="Enable edit mode"
          >
            <img src="@/assets/pencil.svg" alt="" style="max-width: 1.5rem;">
          </button>
          <template v-else>
            <button
              class="p-0 py-1 d-flex align-items-center justify-content-center mb-1 bg-success"
              @click="emit('save')"
              title="save"
            >
              <img src="@/assets/tick.svg" alt="" style="max-width: 1.5rem;">
            </button>
            <button
              class="p-0 py-1 d-flex align-items-center justify-content-center mb-1 bg-danger"
              @click="emit('cancel')"
              title="cancel"
            >
              <img src="@/assets/cross.svg" alt="" style="max-width: 1.5rem;">
            </button>
          </template>
        </div>
        <div v-if="canDelete">
          <hr class="text-dark my-1" style="width: 100%; height: 3px;">
          <button
            class="p-0 py-1 d-flex align-items-center justify-content-center mb-1 bg-danger"
            @dblclick="emit('delete')"
            title="Double click to delete this preset"
          >
            <img src="@/assets/bin.svg" alt="" style="max-width: 1.5rem;">
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
        <img :src="props.backgroundImage && props.backgroundImage.length > 0 ? props.backgroundImage : terminalMap" alt="Airport Map" class="map" @dragstart.prevent/>
        <OverlayArea
          v-for="([key, data]) in Object.entries(internalModelValue).filter(([k, d]) => d.box)"
          :key="key"
          :position="data.box"
          :label="data.label?.length > 0 ? data.label : key"
          :color="data.box.colour"
          :zoomLevel="zoomLevel"
          :data="data.tracker"
          :edit-mode="editMode"
          @update:position="(pos) => updateBox(key, pos)"
        />
      </div>
    </div>
    <NewPreset :presetData="presetData" :updateMode="updateMode" @new-preset="emit('newPreset')"/>
    <ImageUpload :currentPresetId="props.currentPreset" @new-image="emit('newImage')"/>
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