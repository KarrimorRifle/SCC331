<template>
  <div class="sensor-config-container">
    <h1>Sensor Configuration</h1>

    <section class="device-config-section">
      <h2 @click="toggleSection('deviceConfigs')">
        Device Configurations
        <span >
          <font-awesome-icon v-if="openSections.deviceConfigs" :icon="faChevronUp"/>
          <font-awesome-icon v-else :icon="faChevronDown"/>
        </span>
      </h2>
      <div v-show="openSections.deviceConfigs">
        <DeviceConfigs />
      </div>
    </section>

    <section class="tracking-groups-section">
      <h2 @click="toggleSection('trackingGroups')">
        Tracking Groups
        <span>
          <font-awesome-icon v-if="openSections.trackingGroups" :icon="faChevronUp"/>
          <font-awesome-icon v-else :icon="faChevronDown"/>
        </span>
      </h2>
      <div v-show="openSections.trackingGroups">
        <TrackingGroups />
      </div>
    </section>

    <!-- Uncomment if needed -->
    <!--
    <section class="sensor-mapping-section">
      <h2 @click="toggleSection('sensorMapping')">
        Sensor Mapping
        <span>{{ openSections.sensorMapping ? '-' : '+' }}</span>
      </h2>
      <div v-show="openSections.sensorMapping">
        <SensorMappingEditor />
      </div>
    </section>
    -->
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import DeviceConfigs from '../components/SensorConfig/DeviceConfig.vue';
import TrackingGroups from '../components/SensorConfig/TrackingGroups.vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons';
// import SensorMappingEditor from '@/components/SensorMappingEditor.vue';

// Define reactive state for section visibility
const openSections = ref({
  deviceConfigs: true,  // Open by default
  trackingGroups: false,
  sensorMapping: false,
});

// Toggle function for expanding/collapsing sections
const toggleSection = (section: keyof typeof openSections.value) => {
  openSections.value[section] = !openSections.value[section];
};
</script>

<style scoped>
/* Container styling */
.sensor-config-container {
  padding: 1rem;
  background: var(--primary-light-bg);
  color: var(--primary-dark-text);
  overflow-y: auto;
}

/* Headings & collapsible effect */
.sensor-config-container h1 {
  margin-bottom: 1rem;
}

section {
  margin-bottom: 1rem;
  border: 1px solid #ccc;
  padding: 1rem;
  border-radius: 4px;
}

/* Section titles with click effect */
h2 {
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: color 0.2s ease-in-out;
}

/* Collapse/Expand icon */
span {
  font-size: 1.2rem;
  font-weight: bold;
  transition: transform 0.3s ease;
}
</style>
