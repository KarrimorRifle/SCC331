<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import WarningNotificationModal from "./components/Notifications/WarningNotification/WarningNotificationModal.vue";
import WarningAreaModal from "./components/Notifications/WarningNotification/WarningAreaModal.vue";
import NotificationIcon from "./components/Notifications/NotificationIcon.vue";
import Navbar from '@/components/Navbar.vue';
import { useFetchData } from '@/utils/useFetchData';
import { useCookies } from 'vue3-cookies';
import { notificationQueue, addNotification, dismissNotification } from '@/stores/notificationStore';
import { fetchWarnings, fetchFullWarningConditions, warningsList, fullWarningConditions } from './stores/warningStore';
import { usePresetStore } from './utils/useFetchPresets';
import { checkWarningAreas } from './utils/warningChecker';
import axios from 'axios';
import { useAuthStore } from '@/stores/authStore';

const picoIds = [1, 2, 3, 4, 5, 6, 9, 10, 14, 59];
const { updates, warnings } = useFetchData(picoIds);
const presetStore = usePresetStore();
const isMobile = ref(window.innerWidth < 768);
const isWarningModalOpen = ref(false);
const showSeverePopup = ref(false);
const safeWarnings = computed(() => Array.isArray(warnings.value) ? warnings.value : []);
const warningCount = computed(() => notificationQueue.value.length);
const authStore = useAuthStore();

// first time loading for the warnings
let firstTime = true;

// Sync `notificationQueue` when `safeWarnings` updates
watch(
  () => JSON.stringify(safeWarnings.value),
  (newWarnings) => {
    if (!newWarnings || newWarnings === "[]") {
      // console.log("Waiting for safeWarnings to load...");
      return;
    }

    const parsedWarnings = JSON.parse(newWarnings);
    if (parsedWarnings.length === 0) {
      return;
    }

    // // ✅ Clear and re-add warnings to force reactivity
    // notificationQueue.value = [];
    if(firstTime) firstTime = false;
    else return;
    parsedWarnings.forEach((warning) => {
      addNotification(warning);
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

onMounted(async () => {
  await fetchWarnings();
  await fetchFullWarningConditions();
});

onMounted(() => {
  authStore.checkUserAuthority();
});

onUnmounted(() => {
  window.removeEventListener("resize", updateIsMobile);
});

const { cookies } = useCookies();

const isLoggedIn = ref<boolean>(!!cookies.get("session_id"));

// Save a real expiration date from the server after login

// Use the stored expiration for refreshCookie
const refreshCookie = () => {
  const expiryString = localStorage.getItem("session_expiry");
  if (expiryString) {
    const expiryTime = new Date(expiryString).getTime();
    const currentTime = new Date().getTime();
    const tenMinutes = 10 * 60 * 1000;

    if (expiryTime - currentTime < tenMinutes) {
      axios.post("http://localhost:5002/refresh_cookie", {}, { withCredentials: true })
        .then((response) => {
          // Update the expiration date (if present)
          if (response.data && response.data.expires) {
            localStorage.setItem("session_expiry", response.data.expires);
          }
        })
        .catch((error) => console.error("Failed to refresh cookie:", error));
    }
  }
};

watch(
  () => presetStore.summary,
  (newSummary) => {
    if (!newSummary || Object.keys(newSummary).length === 0) return;

    Object.entries(fullWarningConditions.value).forEach(([warningId, warning]) => {
      const triggeredAreas = checkWarningAreas(newSummary, warning);
      triggeredAreas.forEach(({ roomID, messages }) => {
        messages.forEach(msg => {
          addNotification(msg); // Ensure unique notifications get added
        });

        // Show severe pop-up if applicable
        if (messages.some(m => ["doomed", "danger"].includes(m.Severity))) {
          showSeverePopup.value = true;
        }
      });
    });
  },
  { deep: true, immediate: true }
);


</script>

<template>
  <!--<div id="app" class="d-flex flex-column max-vh-100" @click="refreshCookie">-->
  <div id="app" class="d-flex flex-column max-vh-100">
    <Navbar
      class="nav"
      :isMobile="isMobile"
      :isWarningModalOpen="isWarningModalOpen"
      :warnings="notificationQueue"
      :warningCount="warningCount"
      :loggedIn="authStore.isLoggedIn"
      :isAdmin="authStore.userAuthority === 'Admin'"
      @toggleWarningModal="isWarningModalOpen = !isWarningModalOpen"
      @logout="authStore.logout"
    />
    <router-view
      class="flex-grow-1 app"
      :picoIds="picoIds"
      :updates="updates"
      :warnings="notificationQueue"
      :isMobile="isMobile"
      :loggedIn="authStore.isLoggedIn"
      @login="authStore.login"
    />

    <!-- Notification Icon Component -->
    <NotificationIcon
      v-if="!isMobile && authStore.isLoggedIn"
      :warnings="notificationQueue"
      :warningCount="warningCount"
      :isWarningModalOpen="isWarningModalOpen"
      @toggleWarningModal="isWarningModalOpen = !isWarningModalOpen"
    />

    <!-- Warning Area Modal that pops up when the user clicks on the warning button -->
    <WarningAreaModal/>

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
  background: var(--primary-light-bg);
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
}

.warning-content h2 {
  color: var(--warning-text);
  font-size: 24px;
  margin-bottom: 10px;
}

.warning-content p {
  color: var(--primary-dark-text);
  font-size: 18px;
  margin-bottom: 15px;
}

.close-popup {
  background: var(--warning-bg);
  color: var(--primary-light-text);
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
