<script setup lang="ts">
import { ref, defineEmits, defineProps } from "vue";

const props = defineProps ({
    presetData: Object,
})

const rooms = props.presetData.boxes;
const selectedRooms = ref<string[]>([]);

const emit = defineEmits(["updateRooms"]);

</script>

<template>
  <div>
    <h3>Select Rooms</h3>
    <div v-for="room in rooms" :key="room">

      <label>
        <input 
            type="checkbox" 
            :value="room" 
            v-model="selectedRooms" 
            @change="emit('updateRooms', {label: room.label, roomID: room.roomID})"/>
        {{ room.label }}
      </label>
    </div>
  </div>
</template>

<style scoped>
/* Room Selection Wrapper */
div {
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
}

/* Title */
h3 {
  font-size: 22px;
  color: #305F72; /* Text Color */
  text-align: center;
  margin-bottom: 15px;
}

/* Room Checkbox List */
div > div {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #F0B7A4; /* Secondary Color */
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: 0.3s ease-in-out;
}

div > div:hover {
  background: #F18C8E; /* Primary Color */
  color: #ffffff; /* White Text */
}

/* Checkbox Styling */
input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: #568EA6; /* Accent Color */
  cursor: pointer;
}

/* Room Label */
label {
  font-size: 18px;
  color: #305F72; /* Text Color */
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Selected Room Highlight */
input[type="checkbox"]:checked + label {
  font-weight: bold;
  color: #ffffff; /* White Text */
}

@media (max-width: 768px) {
  div {
    width: 90%;
  }
}
</style>
