<script setup lang="ts">
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faChartSimple, faMap} from '@fortawesome/free-solid-svg-icons';
import { ref } from "vue";

// Tracks the selected tab (default is "map")
const selectedTab = ref("map");
</script>

<template>
  <div class="bottom-tab-container">
    <!-- Tab Content: Show Map or Dashboard -->
    <div class="tab-content">
      <slot v-if="selectedTab === 'map'" name="map"></slot>
      <slot v-if="selectedTab === 'dashboard'" name="dashboard"></slot>
    </div>

    <!-- Bottom Tab Navigation -->
    <div class="tab-bar">
      <button 
        :class="{ active: selectedTab === 'map' }"
        @click="selectedTab = 'map'"
      >
        <font-awesome-icon :icon="faMap" />
        Map
      </button>

      <button 
        :class="{ active: selectedTab === 'dashboard' }"
        @click="selectedTab = 'dashboard'"
      >
        <font-awesome-icon :icon="faChartSimple" />
        Dashboard
      </button>
    </div>
  </div>
</template>

<style scoped>
/* Container for the whole bottom navigation system */
.bottom-tab-container {
  display: flex;
  flex-direction: column;
}

/* Content area (Map or Dashboard) */
.tab-content {
  flex-grow: 1;
  overflow: auto;
}

/* Bottom navigation bar */
.tab-bar {
  display: flex;
  justify-content: space-around;
  background: var(--primary-dark-bg);
  padding: 12px;
  position: fixed;
  bottom: 0;
  width: 100%;
  box-shadow: 0px -2px 8px rgba(0, 0, 0, 0.2);
  height: 77px;
}

/* Buttons for tab navigation */
.tab-bar button {
  flex: 1;
  background: none;
  border: none;
  padding: 12px;
  font-size: 18px;
  color: var(--primary-light-text);
  cursor: pointer;
  transition: 0.3s;
}

.tab-bar button.active {
  border-bottom: 3px solid var(--active);
  font-weight: bold;
}
</style>
