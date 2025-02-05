<script setup lang="ts">
import { ref, onMounted, onUnmounted} from 'vue';
import Navbar from '@/components/Navbar.vue';
import { useFetchData } from '@/utils/useFetchData';

const picoIds = [1, 2, 3, 4, 5, 6, 9, 10, 14, 59];

const { overlayAreasConstant, overlayAreasData, updates, environmentHistory, warnings} = useFetchData(picoIds);
const isMobile = ref(window.innerWidth < 768);

const updateIsMobile = () => {
  isMobile.value = window.innerWidth < 768;
};

onMounted(() => {
  window.addEventListener("resize", updateIsMobile);
});

onUnmounted(() => {
  window.removeEventListener("resize", updateIsMobile);
});

</script>

<template>
  <div id="app" class="d-flex flex-column max-vh-100">
    <Navbar class="nav"/>
    <router-view
      class="flex-grow-1 app"
      :picoIds="picoIds"
      :overlayAreasConstant="overlayAreasConstant"
      :overlayAreasData="overlayAreasData" 
      :updates="updates"
      :environmentHistory="environmentHistory"
      :warnings="warnings"
      :isMobile="isMobile"
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
