<script setup lang="ts">
import { RouterLink } from 'vue-router';
import { useCookies } from 'vue3-cookies';

const { cookies } = useCookies();
const sessionId = cookies.get('session-id');
</script>

<template>
  <nav class="navbar">
    <RouterLink to="/" class="nav-link" exact-active-class="active">Airport View</RouterLink>
    <RouterLink to="/summary" class="nav-link" exact-active-class="active">Summary View</RouterLink>
    <RouterLink to="/login" class="nav-link" exact-active-class="active" v-if="!sessionId">Login</RouterLink>
  </nav>
</template>

<style scoped>
.navbar {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #305f72;
  padding: 10px 0px;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 100%;
  margin: 0;
}

.nav-link {
  margin: 0 15px;
  color: white;
  text-decoration: none;
  font-size: 16px;
  font-weight: bold;
}

.nav-link:hover {
  color: #f1d1b5;
}

.active {
  color: #a9a9a9;
}
</style>
