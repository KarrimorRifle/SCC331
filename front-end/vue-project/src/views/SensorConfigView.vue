<template>
  <div class="sensor-config-container">
    <h1>Sensor Configuration</h1>

    <section class="device-config-section">
      <h2>Device Configurations</h2>
      <DeviceConfigs />
    </section>

    <section class="tracking-groups-section">
      <h2>Tracking Groups</h2>
      <TrackingGroups />
    </section>

    <!--
    <section class="sensor-mapping-section">
      <h2>Sensor Mapping</h2>
      <SensorMappingEditor />
    </section>
    -->
  </div>
</template>

<script setup lang="ts">
import DeviceConfigs from '../components/SensorConfig/DeviceConfig.vue';
import TrackingGroups from '../components/SensorConfig/TrackingGroups.vue';
// import SensorMappingEditor from '@/components/SensorMappingEditor.vue';
</script>

<style scoped>
.sensor-config-container {
  padding: 1rem;
  background: var(--primary-light-bg);
  color: var(--primary-dark-text);
  overflow-y: auto;
}
.sensor-config-container h1 {
  margin-bottom: 1rem;
}
section {
  margin-bottom: 2rem;
  border: 1px solid #ccc;
  padding: 1rem;
  border-radius: 4px;
}
</style>
