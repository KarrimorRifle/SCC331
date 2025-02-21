<script setup lang="ts">
import { ref, defineEmits, defineProps } from "vue";

const props = defineProps({
    presetData: Object,
    isRoomSelectionVisible: Boolean, 
});

// Ensure rooms are reactive and derived from props
const rooms = ref(props.presetData?.boxes || []);
const selectedRooms = ref<string[]>([]);
const emit = defineEmits(["updateRooms"]);

// Function to handle room selection
const toggleRoomSelection = (room: any) => {
    const index = selectedRooms.value.findIndex(r => r === room.roomID);
    if (index !== -1) {
        selectedRooms.value.splice(index, 1); // Deselect room
    } else {
        selectedRooms.value.push(room.roomID); // Select room
    }
    emit("updateRooms", { label: room.label, roomID: room.roomID });
};
</script>

<template>
  <h3 v-if="!isRoomSelectionVisible" class="warning-message">
    Select a warning first
  </h3>

  <div v-else class="room-selection">
    <h3>Select Areas</h3>
    <div class="room-grid">
      <div 
        v-for="room in rooms" 
        :key="room.roomID"
        class="room-card"
        :style="{ backgroundColor: room.colour }"
        @click="toggleRoomSelection(room)"
      >
        <label>
          <input 
            type="checkbox" 
            :value="room.roomID" 
            v-model="selectedRooms"
            @click.stop="toggleRoomSelection(room)"
          />
          {{ room.label }}
        </label>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Overall Room Selection Container */

.warning-message {
  background: #FF6B6B !important;
  color: white !important;
  border: none;
  cursor: pointer;
  font-weight: bold;
}

.room-selection {
  padding: 20px;
  border-radius: 10px;
}

/* Title */
h3 {
  text-align: left;
  margin-bottom: 15px;
}

/* Grid Layout */
.room-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); /* Up to 3 per row */
  gap: 15px;
}

/* Room Cards */
.room-card {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s ease-in-out;
  text-align: center;
}

.room-card:hover {
  transform: scale(1.05);
}

/* Checkbox Styling */
input[type="checkbox"] {
  width: 18px;
  height: 18px;
  margin-right: 8px;
  cursor: pointer;
}

label {
  font-size: 18px;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

/* Responsive */
@media (max-width: 600px) {
  .room-grid {
    grid-template-columns: repeat(2, 1fr); /* 2 per row on small screens */
  }
}

@media (max-width: 400px) {
  .room-grid {
    grid-template-columns: repeat(1, 1fr); /* 1 per row on very small screens */
  }
}
</style>
