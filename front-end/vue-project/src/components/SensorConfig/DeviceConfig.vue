<template>
  <div>
    <table>
      <thead>
        <tr>
          <th>Pico ID</th>
          <th>Readable Pico ID</th>
          <th>Pico Type</th>
          <th>Tracking Group</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="config in deviceConfigs" :key="config.picoID">
          <td>{{ config.picoID }}</td>
          <td>
            <input type="text" v-model="config.readablePicoID" />
          </td>
          <td>
            <select v-model="config.picoType">
              <option :value="0">Unassigned</option>
              <option :value="1">Environment</option>
              <option :value="2">BT Tracker</option>
            </select>
          </td>
          <td>
            <div v-if="config.picoType === 2">
              <select v-model="config.trackingGroupID">
                <option :value="-1">None</option>
                <option v-for="group in trackingGroups" :key="group.groupID" :value="group.groupID">
                  {{ group.groupName }}
                </option>
              </select>
            </div>
            <div v-else>
              N/A
            </div>
          </td>
          <td>
            <button @click="updateDeviceConfig(config)">Update</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

// Dummy device config data (simulate GET /get/device/configs)
const deviceConfigs = ref([
  { picoID: '00:11:22:33:44:55', readablePicoID: 'Sensor 1', picoType: 1, trackingGroupID: -1 },
  { picoID: 'AA:BB:CC:DD:EE:FF', readablePicoID: 'Sensor 2', picoType: 2, trackingGroupID: 1 },
]);

// Dummy tracking groups (simulate GET /get/tracking/groups)
const trackingGroups = ref([
  { groupID: 1, groupName: 'Group A' },
  { groupID: 2, groupName: 'Group B' },
]);

const updateDeviceConfig = (config: any) => {
  // Simulate PATCH /patch/device/config/<PicoID>
  console.log("Updating device config:", config);
  alert(`Device config for ${config.picoID} updated (dummy)`);
};
</script>

<style scoped>
table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  border: 1px solid #ccc;
  padding: 0.5rem;
  text-align: left;
}
input[type="text"], select {
  width: 100%;
  padding: 0.25rem;
  box-sizing: border-box;
}
button {
  padding: 0.5rem;
}
</style>
