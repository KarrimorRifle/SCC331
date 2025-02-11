<script setup lang="ts">
import Navbar from '@/components/Navbar.vue';
import { useFetchData } from '@/utils/useFetchData';
import { ref } from "vue";
import { useCookies } from 'vue3-cookies';


const picoIds = [1, 2, 3, 4, 5, 6, 9, 10, 14, 59];

const { overlayAreasConstant, overlayAreasData, updates, environmentHistory } = useFetchData(picoIds);

const { cookies } = useCookies();

const isLoggedIn = ref<boolean>(!!cookies.get("session_id"));
</script>

<template>
  <div id="app" class="d-flex flex-column max-vh-100">
    <Navbar class="nav" :loggedIn="isLoggedIn" @logout="isLoggedIn = false"/>
    <router-view
      class="flex-grow-1 app"
      :picoIds="picoIds"
      :updates="updates"
      :environmentHistory="environmentHistory"
      :overlayAreasConstant="overlayAreasConstant"
      :overlayAreasData="overlayAreasData"
      @login="isLoggedIn = true"
    />
  </div>
</template>

<style>
:root {
  --nav-height: 4rem;
}

.nav {
  height: var(--nav-height);
}

html, body, #app {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  overflow-x: hidden;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100% !important;
}

.app {
  max-height: calc(100% - var(--nav-height))
}

.router-view {
  flex-grow: 1;
  width: 100%;
  max-height: calc(100% - var(--nav-height));
}

.flex-grow-1 {
  flex-grow: 1;
}
</style>
