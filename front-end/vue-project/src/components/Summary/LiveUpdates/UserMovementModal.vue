<script setup lang="ts">
import UserMovementArrow from "./UserMovementArrow.vue";
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faXmark } from '@fortawesome/free-solid-svg-icons';
import { defineProps, defineEmits, ref, watch, computed, PropType } from 'vue';
import { getTextColour } from '../../../utils/helper/colorUtils';
import { usePresetStore } from "../../../utils/useFetchPresets";

const props = defineProps({
  showModal: { type: Boolean, required: true },
  selectedUserId: { type: [Number, String], default: null },
  userRoomHistory: {
    type: Array as PropType<{ roomLabel: string; loggedAt: string }[]>,
    required: true,
  },
});
console.log("jf: ", props.userRoomHistory);
const emit = defineEmits(['close']);

const presetStore = usePresetStore();
const presetData = computed(() => Object.values(presetStore.boxes_and_data));
/* HELPERS */
const convertToTimestamp = (date: string | Date | null): number => {
  if (!date) return 0;

  if (typeof date === "string") {
    // If in ISO format, parse directly
      if (date.includes('T'))
        return new Date(date).getTime();

    // Convert "17/02/2025, 05:55:32" → "2025-02-17T05:55:32"
    const [day, month, year, time] = date.split(/[/, ]+/);
    const formattedDate = `${year}-${month}-${day}T${time}`;
    return new Date(formattedDate).getTime();
  }
  return new Date(date).getTime();
};

const getRoomColor = (roomLabel: string): string => {
  return currentRoom.value === roomLabel
    ? props.userRoomHistory.find(entry => entry.roomLabel === roomLabel)?.roomColor || 'lightgray'
    : 'lightgray'; // Show lightgray if it's not the current room
};

/* COMPUTED PROPERTIES */
const timestamps = computed(() => props.userRoomHistory.map(entry => entry.loggedAt));
const timelineStart = computed(() =>
  props.userRoomHistory.length ? new Date(convertToTimestamp(props.userRoomHistory[0].loggedAt)) : new Date()
);
const timelineEnd = computed(() =>
  props.userRoomHistory.length ? new Date(convertToTimestamp(props.userRoomHistory[props.userRoomHistory.length - 1].loggedAt)) : new Date()
);
const totalSteps = computed(() => props.userRoomHistory.length * 10); // Smoother dragging

/* STATE VARIABLES */
const currentRoom = ref<string | null>(null);
const prevRoom = ref<string | null>(null);
const replayIndex = ref(0);
const isPlaying = ref(false);
const speed = ref(500); // Default speed is 500ms per step
const loopReplay = ref(false);
const timelinePosition = ref(convertToTimestamp(timelineStart.value));
const movementArrows = ref<{ from: string; to: string }[]>([]);
const currentTime = ref(timestamps.value[Math.floor(replayIndex.value / 10)] || timelineStart.value.toISOString());

let replayInterval: ReturnType<typeof setInterval> | null = null;

/* AREA POSITIONS */

const areaPositions = computed(() => {
  const positions = [
    { x: 50, y: 50 },   // Top-left
    { x: 250, y: 50 },  // Top-right
    { x: 50, y: 250 },  // Bottom-left
    { x: 250, y: 250 }, // Bottom-right
  ];

  const mappedPositions: Record<string, { x: number; y: number }> = {};

  presetData.value.forEach((area, index) => {
    if (positions[index]) {
      mappedPositions[area.label] = positions[index]; 
    }
  });

  return mappedPositions;
});

/* TIMELINE & PLAYBACK */
const updateReplayIndex = (event: Event) => {
  const target = event.target as HTMLInputElement;
  replayIndex.value = parseFloat(target.value);
  const index = Math.floor(replayIndex.value / 10);
  currentRoom.value = props.userRoomHistory[index]?.roomLabel || null;
  currentTime.value = timestamps.value[index] || '';
};

const updateReplayFromTimeline = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const newTimestamp = parseFloat(target.value);
  const index = props.userRoomHistory.findIndex(entry => convertToTimestamp(entry.loggedAt) >= newTimestamp);

  if (index >= 0) {
    replayIndex.value = index * 10;
    prevRoom.value = currentRoom.value;
    currentRoom.value = props.userRoomHistory[index]?.roomLabel || null;
    currentTime.value = props.userRoomHistory[index]?.loggedAt || '';
    timelinePosition.value = newTimestamp;

    if (prevRoom.value && currentRoom.value && prevRoom.value !== currentRoom.value) {
      movementArrows.value = [{ from: prevRoom.value, to: currentRoom.value }];
    }
  }
};

const updateSpeed = (event: Event) => {
  speed.value = parseInt((event.target as HTMLInputElement).value);
  if (isPlaying.value) {
    pauseReplay();
    startReplay();
  }
};

/* REPLAY CONTROLS */
const startReplay = () => {
  if (props.userRoomHistory.length === 0) return;
  isPlaying.value = true;
  replayIndex.value = 0;
  currentRoom.value = props.userRoomHistory[0]?.roomLabel || null;
  currentTime.value = timestamps.value[0] || '';

  replayInterval = setInterval(() => {
    if (replayIndex.value < totalSteps.value - 1) {
      replayIndex.value += 10;
      const index = Math.floor(replayIndex.value / 10);
      prevRoom.value = currentRoom.value;
      currentRoom.value = props.userRoomHistory[index]?.roomLabel || null;
      currentTime.value = timestamps.value[index] || '';
      timelinePosition.value = convertToTimestamp(props.userRoomHistory[index]?.loggedAt);

      if (prevRoom.value && currentRoom.value && prevRoom.value !== currentRoom.value) {
        movementArrows.value = [{ from: prevRoom.value, to: currentRoom.value }];
      }
    } else {
      clearInterval(replayInterval as ReturnType<typeof setInterval>);
      isPlaying.value = false;
      movementArrows.value = [];
    }
  }, speed.value);
};

const pauseReplay = () => {
  isPlaying.value = false;
  if (replayInterval) clearInterval(replayInterval);
};

const resetReplay = () => {
  if (replayInterval) clearInterval(replayInterval);
  replayIndex.value = 0;
  prevRoom.value = null;
  movementArrows.value = [];
  currentRoom.value = props.userRoomHistory[0]?.roomLabel || null;
  currentTime.value = timestamps.value[0] || '';
  isPlaying.value = false;
};

/* WATCHERS */
watch(() => props.showModal, (newValue) => {
  if (newValue && props.userRoomHistory.length > 0) {
    replayIndex.value = 0;
    currentRoom.value = props.userRoomHistory[0]?.roomLabel || null;
    currentTime.value = props.userRoomHistory[0]?.loggedAt || '';
  }
});
</script>

<template>
  <div v-if="showModal" class="modal-overlay">
    <div class="modal-content">

      <div class="modal-user-movement-header">
        <h2>User {{ selectedUserId }} Movement</h2>

        <button class="close-btn" @click="emit('close')">
          <font-awesome-icon :icon="faXmark" />
        </button>
      </div>
      <!-- Flexbox Container for Grids and Tools -->
      <div class="flex-container">
        <!-- 4 Grid Area Layout -->
        <div class="grid-container">
          <UserMovementArrow 
            :movementArrows="movementArrows" 
            :areaPositions="areaPositions" 
            :moveXPositionBy=20
            :moveYPositionBy=20
          />
          <div
            v-for="area in presetData" 
            :key="area.label"
            :class="['grid-item', { active: currentRoom === area }]"
            :style="{ backgroundColor: getRoomColor(area.label), color: getTextColour(getRoomColor(area.label)) }"
          >
            {{ area.label }}
          </div>
          <!-- Display Time -->
        </div>

        <!-- Tools (Controls and Settings) -->
        <div class="tools-container">

          <!-- Speed & Loop Replay Controls -->
          <div class="settings">
            <div class="speed-control">
              <label for="speed">⏩ Speed:</label>
              <input
                type="range"
                id="speed"
                min="200"
                max="2000"
                step="100"
                v-model="speed"
                @input="updateSpeed"
              />
              <span>{{ speed }}ms</span>
            </div>

            <div class="loop-control">
              <label>🔄 Loop Replay:</label>
              <input type="checkbox" v-model="loopReplay" />
            </div>
          </div>

          <!-- Replay Controls -->
          <div class="controls">
            <button @click="startReplay" :disabled="isPlaying">▶ Play</button>
            <button @click="pauseReplay" :disabled="!isPlaying">⏸ Pause</button>
            <button @click="resetReplay">🔄 Reset</button>
          </div>
        </div>
        
      </div>

      <div class="timeline-container">
        <input
          type="range"
          :min="convertToTimestamp(timelineStart)"
          :max="convertToTimestamp(timelineEnd)"
          :step="1000"
          v-model="timelinePosition"
          class="timeline-slider"
          :disabled="
            !timelineStart || 
            !timelineEnd || 
            convertToTimestamp(timelineStart) === convertToTimestamp(timelineEnd)"
          @input="updateReplayFromTimeline"
        />
        <div class="timeline-labels">
          <span>{{ timelineStart ? timelineStart.toLocaleTimeString() : 'Start' }}</span>
          <span>{{ timelineEnd ? timelineEnd.toLocaleTimeString() : 'End' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.modal-user-movement-header{
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}
/* Close Button */
.close-btn {
  border: none;
  outline: none;
  font-size: 1.5rem;
  cursor: pointer;
  background: none;
  transition: transform 0.3s ease-in-out 0.1s;
}
.close-btn:hover{
  transform: scale(1.2);
}
.close-btn i {
  font-size: 24px;
}

.modal-content {
  background: var(--primary-light-bg);
  padding: 20px;
  width: 70%;
  border-radius: 10px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.flex-container {
  display: flex;
  gap: 0px;
}

.movement-arrows {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

/* 4-Grid Layout */
.grid-container {
  position: relative;
  display: grid;
  grid-template-columns: repeat(2, 150px);
  grid-template-rows: repeat(2, 150px);
  gap: 10px;
  flex: 1;
  justify-content: center;
}

.grid-item {
  width: 150px;
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--not-active-bg);
  border-radius: 10px;
  font-weight: bold;
  transition: background 0.3s ease-in-out;
}

.active {
  background: var(--primary-bg);
  color: var(--primary-light-text);
  border: 3px solid #F18C8E;
}

/* Tools Container */
.tools-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 20px;
  flex: 1;
}

/* Time Display */
.time-display {
  font-size: 16px;
  color: var(--primary-dark-text);
  margin: 10px 0;
}

/* Speed & Loop Settings */
.settings {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-start;
  margin: 10px 0;
}

.speed-control, .loop-control {
  display: flex;
  align-items: center;
}

.speed-control label, .loop-control label {
  font-weight: bold;
  color: var(--primary-dark-text);
  margin-right: 5px;
}

.loop-control input {
  transform: scale(1.2);
}

/* Controls */
.controls {
  margin-top: 10px;
}

.controls button {
  margin: 5px;
  padding: 8px 12px;
  border: none;
  background: var(--primary-dark-bg);
  color: var(--primary-light-text);
  border-radius: 5px;
  cursor: pointer;
}

.controls button:disabled {
  background: var(--negative-bg);
  cursor: not-allowed;
}

/* Timeline Container */
.timeline-container {
  margin: 15px 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* Timeline Slider */
.timeline-slider {
  width: 100%;
  appearance: none;
  height: 6px;
  background: var(--primary-dark-bg);
  border-radius: 5px;
  outline: none;
}

.timeline-slider:disabled{
  cursor: not-allowed;
  opacity: 0.5;
}
.timeline-slider::-webkit-slider-thumb {
  appearance: none;
  width: 16px;
  height: 16px;
  background: var(--active-bg);
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.2s ease-in-out;
}

.timeline-slider::-webkit-slider-thumb:hover {
  transform: scale(1.2);
}

/* Timeline Labels */
.timeline-labels {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: var(--primary-dark-text);
  width: 100%;
  margin-top: 5px;
}


@media (max-width: 786px) {
  .modal-content{
    width: 90%;
  }
  .flex-container{
    flex-direction: column;
  }
  .settings{
    flex-direction: column;
    align-items: flex-start;
  }
}

</style>
