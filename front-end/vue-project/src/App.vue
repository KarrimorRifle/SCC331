<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import WarningNotificationModal from "./components/Notifications/WarningNotification/WarningNotificationModal.vue";
import WarningAreaModal from "./components/Notifications/WarningNotification/WarningAreaModal.vue";
import NotificationIcon from "./components/Notifications/NotificationIcon.vue";
import Navbar from '@/components/Navbar.vue';
import { useFetchData } from '@/utils/useFetchData';
import { useCookies } from 'vue3-cookies';


const picoIds = [1, 2, 3, 4, 5, 6, 9, 10, 14, 59];
const { overlayAreasConstant, overlayAreasData, updateOverlayAreaColor, updateAllOverlayAreas, updates, environmentHistory, warnings } = useFetchData(picoIds);
const isMobile = ref(window.innerWidth < 768);
const isWarningModalOpen = ref(false);
const showSeverePopup = ref(false);
const safeWarnings = computed(() => Array.isArray(warnings.value) ? warnings.value : []);
const warningCount = computed(() => notificationQueue.value.length);

// ** Move notification storage to parent **
const notificationQueue = ref<{ Title: string; Location: string; Severity: string; Summary: string }[]>([]);

const dismissNotification = (index: number) => {
  notificationQueue.value.splice(index, 1);
};

const handleUpdateOverlayAreaColor = ({ roomID, colour }) => {
  updateOverlayAreaColor(roomID, colour);
};

const handleUpdateAllOverlayAreas = (newOverlayAreas) => {
  updateAllOverlayAreas(newOverlayAreas);
};
// Sync `notificationQueue` when `safeWarnings` updates
watch(
  () => JSON.stringify(safeWarnings.value), // 🔄 Track JSON string to detect deep changes
  (newWarnings) => {
    if (!newWarnings) return;

    const parsedWarnings = JSON.parse(newWarnings);

    // ✅ Clear and re-add warnings to force reactivity
    notificationQueue.value = [];
    parsedWarnings.forEach((warning) => {
      notificationQueue.value.push(warning);
    });

    // Show severe pop-up if applicable
    if (parsedWarnings.some(w => ["doomed", "danger"].includes(w.Severity))) {
      showSeverePopup.value = true;
    }
  },
  { deep: true, immediate: true }
);

const updateIsMobile = () => {
  isMobile.value = window.innerWidth < 768;
};

onMounted(() => {
  window.addEventListener("resize", updateIsMobile);
});

onUnmounted(() => {
  window.removeEventListener("resize", updateIsMobile);
});

const { cookies } = useCookies();

const isLoggedIn = ref<boolean>(!!cookies.get("session_id"));
</script>

<template>
  <div id="app" class="d-flex flex-column max-vh-100">
    <Navbar 
      class="nav" 
      :isMobile="isMobile" 
      :isWarningModalOpen="isWarningModalOpen" 
      :warnings="notificationQueue"
      :warningCount="warningCount"
      :loggedIn="isLoggedIn"
      @toggleWarningModal="isWarningModalOpen = !isWarningModalOpen"
      @logout="isLoggedIn = false"
    />
    <router-view
      class="flex-grow-1 app"
      :picoIds="picoIds"
      :updates="updates"
      :environmentHistory="environmentHistory"
      :warnings="notificationQueue"
      :isMobile="isMobile"
      :overlayAreasConstant="overlayAreasConstant"
      :overlayAreasData="overlayAreasData"
      :loggedIn="isLoggedIn"
      @login="isLoggedIn = true"
      @updateOverlayAreaColor="handleUpdateOverlayAreaColor"
      @updateOverlayAreas="handleUpdateAllOverlayAreas"
    />
    
    <!-- Notification Icon Component -->
    <NotificationIcon 
      v-if="!isMobile && isLoggedIn" 
      :warnings="notificationQueue" 
      :warningCount="warningCount"
      :isWarningModalOpen="isWarningModalOpen"
      @toggleWarningModal="isWarningModalOpen = !isWarningModalOpen"
    />

    <!-- Warning Area Modal that pops up when the user clicks on the warning button -->
    <WarningAreaModal 
      :overlayAreasConstant="overlayAreasConstant"
    />

    <!-- Warning Notification Modal -->
    <WarningNotificationModal 
      v-if="isWarningModalOpen" 
      :warnings="notificationQueue" 
      :warningCount="warningCount"
      :isMobile="isMobile"
      @close="isWarningModalOpen = false" 
      @dismiss="dismissNotification"
    />

    <!-- Full-Screen Pop-up for Severe Warnings
    <transition name="fade">
      <div v-if="showSeverePopup" class="full-screen-warning">
        <div class="warning-content">
          <h2>⚠️ CRITICAL WARNING</h2>
          <p>A severe issue has been detected that requires immediate attention.</p>
          <button @click="showSeverePopup = false" class="close-popup">Dismiss</button>
        </div>
      </div>
    </transition>
    -->

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
  max-height: calc(100% - var(--nav-height));
}

.router-view {
  flex-grow: 1;
  width: 100%;
  max-height: calc(100% - var(--nav-height));
}

/* Full-Screen Pop-up for Severe Warnings */
.full-screen-warning {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 99999;
}

.warning-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
}

.warning-content h2 {
  color: red;
  font-size: 24px;
  margin-bottom: 10px;
}

.warning-content p {
  color: black;
  font-size: 18px;
  margin-bottom: 15px;
}

.close-popup {
  background: red;
  color: white;
  padding: 10px 20px;
  border: none;
  font-size: 16px;
  cursor: pointer;
  border-radius: 5px;
}

.close-popup:hover {
  background: darkred;
}
</style>
