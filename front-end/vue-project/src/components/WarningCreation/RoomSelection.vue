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
