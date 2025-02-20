<script setup lang="ts">
import { ref, defineProps, defineEmits, watch } from "vue";

const props = defineProps({
  conditions: Object as () => Record<string, any>, // Receive set conditions
});
console.log(props.conditions);
const emit = defineEmits(["updateMessages"]);

// Store custom messages for each condition
const customMessages = ref<Record<string, string>>({});

// Watch for changes in conditions and pre-fill the text area
watch(() => props.conditions, (newConditions) => {
  Object.entries(newConditions).forEach(([room, roomData]) => {
    if (!roomData.messages) return; // Ensure messages exist

    roomData.messages.forEach((message) => {
        if (!customMessages.value[message.Title]) {
        customMessages.value[message.Title] = message.Summary;
        }
    });
  });
}, { deep: true, immediate: true });


const updateMessages = () => {
  const formattedMessages = Object.entries(customMessages.value).map(([key, summary]) => {
    // Extract room ID and title correctly
    const existingMessage = Object.values(props.conditions)
      .reduce((acc, room) => acc.concat(room.messages || []), []) // Flatten messages array
      .find(m => m.Title.trim() === key.trim());

    return {
      Authority: existingMessage?.Authority || "everyone",
      Title: existingMessage?.Title || key.trim(),
      Location: existingMessage?.Location?.trim() || key.split("-")[0].trim(),
      Severity: existingMessage?.Severity || "warning",
      Summary: summary // Use the updated custom message
    };
  });

  emit("updateMessages", formattedMessages);
};

</script>

<template>
  <div>
    <h3>Customize Warning Messages</h3>
    <div v-for="(roomData, room) in props.conditions" :key="room">
      <h4>{{ room }}</h4>
      <div v-for="(message, index) in roomData.messages" :key="index" class="message-container">
        <label>Title: {{ message.Title }}</label>

        <label>Custom Summary:
          <textarea v-model="customMessages[message.Title]" placeholder="Enter custom message"></textarea>
        </label>
      </div>
    </div>
    <button @click="updateMessages">Save Messages</button>
  </div>
</template>