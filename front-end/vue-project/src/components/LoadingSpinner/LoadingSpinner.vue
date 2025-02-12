<template>
  <div class="loading-spinner-container">
    <div class="spinner"></div>
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps({
  message: {
    type: String,
    default: "Loading..."
  }
});
</script>

<style scoped>
.loading-spinner-container {
  position: absolute; /* Make it absolute */
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%); /* Center it */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8); /* Semi-transparent white */
  z-index: 9999; /* Ensure it's on top */
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(0, 0, 0, 0.2);
  border-top-color: #568EA6; /* Highlighted color */
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

p {
  margin-top: 10px;
  font-size: 16px;
  font-weight: bold;
  color: black;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
