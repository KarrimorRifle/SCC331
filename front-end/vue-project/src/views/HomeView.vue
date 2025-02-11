<script setup lang="ts">
import { RouterLink } from 'vue-router';
</script>

<template>
  <div class="welcome-container">
    <h1>Welcome to the Airport Information System</h1>
    <p>Please log in to access detailed information and features.</p>
    <RouterLink to="/login" class="login-link">Go to Login</RouterLink>
  </div>
</template>

<style scoped>
.welcome-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  text-align: center;
  background-color: #f8f8ff;
  color: #333;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

p {
  font-size: 1.25rem;
  margin-bottom: 2rem;
}

.login-link {
  font-size: 1.25rem;
  color: #007bff;
  text-decoration: none;
}

.login-link:hover {
  text-decoration: underline;
}
</style>