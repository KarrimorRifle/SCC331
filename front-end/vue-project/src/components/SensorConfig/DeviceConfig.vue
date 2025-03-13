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
            <!-- Show tracking group only if picoType === 2 -->
            <div v-if="config.picoType === 2">
              <select v-model="config.trackingGroupID">
                <option :value="-1">None</option>
                <option
                  v-for="group in trackingGroups"
                  :key="group.groupID"
                  :value="group.groupID"
                >
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
import { ref, onMounted } from 'vue';
import axios from 'axios';

// Reactive arrays to store data
const deviceConfigs = ref([]);
const trackingGroups = ref([]);

/**
 * Load device configs from /get/device/configs and tracking groups from /get/tracking/groups.
 * Both endpoints are on port 5006 (Flask server).
 */
const loadData = async () => {
  try {
    // Fetch device configs
    const configRes = await axios.get('http://localhost:5006/get/device/configs', {
      withCredentials: true, // Important to send session_id cookie
    });
    deviceConfigs.value = configRes.data.configs;
  } catch (err) {
    console.error("Failed to load device configs:", err);
  }

  try {
    // Fetch tracking groups
    const groupsRes = await axios.get('http://localhost:5006/get/tracking/groups', {
      withCredentials: true,
    });
    trackingGroups.value = groupsRes.data.groups;
  } catch (err) {
    console.error("Failed to load tracking groups:", err);
  }
};

/**
 * Send a PATCH request to update a single device config.
 * Endpoint: /patch/device/config/<pico_id>
 */
const updateDeviceConfig = async (config: any) => {
  try {
    // Construct the PATCH data. We always send `readablePicoID` & `picoType`.
    const patchData: any = {
      readablePicoID: config.readablePicoID,
      picoType: config.picoType,
    };

    // If it's a BT Tracker (picoType=2), also send trackingGroupID
    if (config.picoType === 2) {
      patchData.trackingGroupID = config.trackingGroupID;
    }

    // Make the PATCH request
    await axios.patch(
      `http://localhost:5006/patch/device/config/${config.picoID}`,
      patchData,
      { withCredentials: true }
    );

    alert(`Device config for ${config.picoID} updated!`);
  } catch (err) {
    console.error("Failed to patch device config:", err);
    alert("Update failed. See console for details.");
  }
};

/**
 * onMounted: load data from the server as soon as this component is mounted.
 */
onMounted(() => {
  loadData();
});
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
  cursor: pointer;
}
</style>
