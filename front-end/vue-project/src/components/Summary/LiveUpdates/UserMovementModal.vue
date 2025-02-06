<script setup lang="ts">
import { defineProps, defineEmits, ref, watch, computed, PropType } from 'vue';

const props = defineProps({
  showModal: {
    type: Boolean,
    required: true,
  },
  selectedUserId: {
    type: Number,
    default: null,
  },
  userRoomHistory: {
    type: Array as PropType<{ roomLabel: string; loggedAt: string }[]>,
    required: true,
  },
});

const emit = defineEmits(['close']);

// State for tracking movement replay
const currentRoom = ref<string | null>(null);
const replayIndex = ref(0);
const isPlaying = ref(false);
const speed = ref(500); // Default speed is 500ms per step
const loopReplay = ref(false); // Loop Replay Toggle
let replayInterval: ReturnType<typeof setInterval> | null = null;

// Compute formatted timestamps for the slider
const timestamps = computed(() => props.userRoomHistory.map(entry => entry.loggedAt));
const totalSteps = computed(() => props.userRoomHistory.length * 10); // Smoother dragging
const currentTime = ref(timestamps.value[Math.floor(replayIndex.value / 10)] || '');

// Start Replay Animation
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
      currentRoom.value = props.userRoomHistory[index]?.roomLabel || null;
      currentTime.value = timestamps.value[index] || '';
    } else if (loopReplay.value) {
      // Restart the replay if loop is enabled
      replayIndex.value = 0;
      currentRoom.value = props.userRoomHistory[0]?.roomLabel || null;
      currentTime.value = timestamps.value[0] || '';
    } else {
      clearInterval(replayInterval as ReturnType<typeof setInterval>);
      isPlaying.value = false;
    }
  }, speed.value);
};

// Pause Replay
const pauseReplay = () => {
  isPlaying.value = false;
  if (replayInterval) clearInterval(replayInterval);
};

// Reset Replay
const resetReplay = () => {
  if (replayInterval) clearInterval(replayInterval);
  replayIndex.value = 0;
  currentRoom.value = props.userRoomHistory[0]?.roomLabel || null;
  currentTime.value = timestamps.value[0] || '';
  isPlaying.value = false;
};

// **Manual Drag Movement via Scaled Slider**
const updateReplayIndex = (event: Event) => {
  const target = event.target as HTMLInputElement;
  replayIndex.value = parseFloat(target.value);
  const index = Math.floor(replayIndex.value / 10);
  currentRoom.value = props.userRoomHistory[index]?.roomLabel || null;
  currentTime.value = timestamps.value[index] || ''; // **Fix: Updates the time instantly**
};

// Watch for modal close, reset replay
watch(() => props.showModal, (newValue) => {
  if (!newValue) resetReplay();
});

// Change Speed Control
const updateSpeed = (event: Event) => {
  const target = event.target as HTMLInputElement;
  speed.value = parseInt(target.value);
  if (isPlaying.value) {
    pauseReplay();
    startReplay();
  }
};
</script>

<template>
  <div v-if="showModal" class="modal-overlay">
    <div class="modal-content">
      <h2>User {{ selectedUserId }} Movement </h2>

      <!-- 4 Grid Area Layout -->
      <div class="grid-container">
        <div v-for="area in ['Area 1', 'Area 2', 'Area 3', 'Area 4']" 
             :key="area" 
             :class="['grid-item', { active: currentRoom === area }]">
          {{ area }}
        </div>
      </div>

      <!-- Display Time -->
      <p class="time-display">📍 Current Time: <strong>{{ currentTime }}</strong></p>

      <!-- **Smoother Replay Timeline (Scaled Slider)** -->
      <div class="slider-container">
        <input 
          type="range" 
          min="0" 
          :max="totalSteps - 1" 
          v-model="replayIndex" 
          @input="updateReplayIndex" 
          class="timeline-slider"
        />
      </div>

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

      <button @click="emit('close')">Close</button>
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

.modal-content {
  background: white;
  padding: 20px;
  width: 70%;
  border-radius: 10px;
  text-align: center;
}

/* 4-Grid Layout */
.grid-container {
  display: grid;
  grid-template-columns: repeat(2, 150px);
  grid-template-rows: repeat(2, 150px);
  gap: 10px;
  justify-content: center;
  margin: 20px 0;
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

/* Time Display */
.time-display {
  font-size: 16px;
  color: #305F72;
  margin: 10px 0;
}

/* Speed & Loop Settings */
.settings {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

@media (max-width: 786px) {
  .modal-content{
    width: 90%;
  }
  .settings{
    flex-direction: column;
    align-items: flex-start;
  }
}

</style>
