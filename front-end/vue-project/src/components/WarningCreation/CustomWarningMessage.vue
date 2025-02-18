<script setup lang="ts">
import { ref, defineProps, defineEmits } from "vue";

const props = defineProps({
  conditions: Object as () => Record<string, any>,
});

const emit = defineEmits(["updateMessages"]);

const customMessages = ref<Record<string, string>>({});

const updateMessages = () => {
  const messages = Object.entries(props.conditions).map(
    ([room, condition]) =>
      `Warning for ${room}: Temperature should be between ${condition.temperatureRange[0]} and ${condition.temperatureRange[1]}, Allowed Users: ${condition.allowedUsers.join(", ")}`
  );
  emit("updateMessages", messages);
};
</script>

<template>
  <div>
    <h3>Customize Warning Messages</h3>
    <div v-for="(condition, room) in props.conditions" :key="room">
      <h4>{{ room }}</h4>
      <textarea v-model="customMessages[room]" placeholder="Enter custom message"></textarea>
    </div>
    <button @click="updateMessages">Save Messages</button>
  </div>
</template>
