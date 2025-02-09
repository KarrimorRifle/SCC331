<script setup lang="ts">
import { RouterLink } from 'vue-router';
import { useCookies } from 'vue3-cookies';
import { defineProps, defineEmits } from "vue";
import axios from "axios"
import router from '@/router';

const props = defineProps({
  loggedIn: {
    type: Boolean,
    default: null
  }
});

const emit = defineEmits(["logout"]);

const { cookies } = useCookies();

const handleLogout = async() => {
  try {
    await axios.post("http://localhost:5002/logout", {}, {
      withCredentials: true
    })
    cookies.remove('session_id');
    emit("logout");
    router.push("/");
  }catch(err) {
    console.log("Error encountered logging out:", err)
  }
}
</script>

<template>
  <nav class="navbar">
    <RouterLink to="/" class="nav-link" exact-active-class="active" v-if="props.loggedIn">Home</RouterLink>
    <RouterLink to="/map" class="nav-link" exact-active-class="active" v-if="props.loggedIn">Map</RouterLink>
    <RouterLink to="/summary" class="nav-link" exact-active-class="active" v-if="props.loggedIn">Summary</RouterLink>
    <RouterLink to="/login" class="nav-link" exact-active-class="active" v-if="!props.loggedIn">Login</RouterLink>
    <RouterLink to="#" class="nav-link" v-if="props.loggedIn" @click.prevent="handleLogout">
      Log out
    </RouterLink>
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
  color: rgb(196, 196, 196);
  text-decoration: none;
  font-size: 16px;
  font-weight: bold;
}

.nav-link:hover {
  color: #f1d1b5;
}

.active {
  color: #ffffff;
}
</style>
