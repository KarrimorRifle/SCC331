<script setup lang="ts">
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faXmark } from '@fortawesome/free-solid-svg-icons';
import { defineProps, defineEmits, ref, watch, computed, PropType } from 'vue';

const props = defineProps({
  showModal: { type: Boolean, required: true },
  overlayAreasConstant: {
    type: Array as PropType<{ label: string; color: string; position: object }[]>,
    required: true,
  },
  selectedUserId: { type: Number, default: null },
  userRoomHistory: {
    type: Array as PropType<{ roomLabel: string; loggedAt: string }[]>,
    required: true,
  },
});

const emit = defineEmits(['close']);

/* HELPERS */
const convertToTimestamp = (date: string | Date | null): number =>
  date ? new Date(date).getTime() : 0;

const getRoomColor = (roomLabel: string): string => {
  return currentRoom.value === roomLabel
    ? props.overlayAreasConstant.find(area => area.label === roomLabel)?.color || 'lightgray'
    : 'lightgray';
};

const getArrowPosition = (from: string, to: string) => {
  const positions = areaPositions.value;
  if (!positions[from] || !positions[to]) return null;

  const start = positions[from];
  const end = positions[to];
  const offsetFactor = 0.3; // Adjust arrow length (0 = full length, 0.5 = half length)

  const dx = end.x - start.x;
  const dy = end.y - start.y;
  const distance = Math.sqrt(dx * dx + dy * dy);

  // Normalize the vector and apply offset
  const normalizedDx = (dx / distance) * (distance * offsetFactor);
  const normalizedDy = (dy / distance) * (distance * offsetFactor);

  let x1 = start.x + normalizedDx;
  let y1 = start.y + normalizedDy;
  let x2 = end.x - normalizedDx;
  let y2 = end.y - normalizedDy;

  if (start.x === end.x) {
    x1 += 20;
    x2 += 20;
  }
  if (start.y === end.y) {
    y1 += 20; 
    y2 += 20;
  }

  return { x1, y1, x2, y2 };
};

/* COMPUTED PROPERTIES */
const timestamps = computed(() => props.userRoomHistory.map(entry => entry.loggedAt));
const timelineStart = computed(() =>
  props.userRoomHistory.length ? new Date(props.userRoomHistory[0].loggedAt) : new Date()
);
const timelineEnd = computed(() =>
  props.userRoomHistory.length ? new Date(props.userRoomHistory[props.userRoomHistory.length - 1].loggedAt) : new Date()
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
const areaPositions = computed(() => ({
  "Area 1": { x: 50, y: 50 },   // Top-left
  "Area 2": { x: 250, y: 50 },  // Top-right
  "Area 3": { x: 50, y: 250 },  // Bottom-left
  "Area 4": { x: 250, y: 250 }, // Bottom-right
}));

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
          <svg class="movement-arrows" viewBox="0 0 300 300">
            <line
              v-for="arrow in movementArrows"
              v-bind="getArrowPosition(arrow.from, arrow.to)"
              :key="`${arrow.from}-${arrow.to}`"
              stroke="black"
              stroke-width="1"
              marker-end="url(#arrowhead)"
            />
            <defs>
              <marker id="arrowhead" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
                <polygon points="0 0, 6 3, 0 6" fill="black" />
              </marker>
            </defs>
          </svg>
          <div
            v-for="area in ['Area 1', 'Area 2', 'Area 3', 'Area 4']"
            :key="area"
            :class="['grid-item', { active: currentRoom === area }]"
            :style="{ backgroundColor: getRoomColor(area), color: currentRoom === area ? 'white' : 'black' }"
          >
            {{ area }}
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
  background: white;
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
  background: lightgray;
  border-radius: 10px;
  font-weight: bold;
  transition: background 0.3s ease-in-out;
}

.active {
  background: #568EA6;
  color: white;
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
  color: #305F72;
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
  color: #305F72;
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
  background: #305F72;
  color: white;
  border-radius: 5px;
  cursor: pointer;
}

.controls button:disabled {
  background: gray;
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
  background: #305F72;
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
  background: #F18C8E;
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
  color: #305F72;
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
