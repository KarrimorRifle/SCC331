<template>
  <div class="table-container">
    <!-- Added global update & cancel buttons -->
      <button @click="updateAllDeviceConfigs" class="my-2 btn btn-primary me-2">Update</button>
      <button @click="cancelChanges" class="my-2 btn btn-secondary btn-secondary" style="background-color: rgb(205, 30, 30);">Cancel</button>
    <table>
      <thead>
        <tr>
          <th>Pico ID</th>
          <th>Readable Pico ID</th>
          <th>Pico Type</th>
          <th>Tracking Group</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="config in deviceConfigs" :key="config.picoID">
          <td>{{ config.picoID }}</td>
          <td>
            <input type="text" v-model="config.readablePicoID" @input="config.dirty = true" />
          </td>
          <td>
            <select v-model="config.picoType" @change="config.dirty = true">
              <option :value="0">Unassigned</option>
              <option :value="1">Environment</option>
              <option :value="2">BT Tracker</option>
            </select>
          </td>
          <td>
            <div v-if="config.picoType === 2">
              <select v-model="config.trackingGroupID" @change="config.dirty = true">
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
            <div v-else>N/A</div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

interface DeviceConfig {
  picoID: string;
  readablePicoID: string;
  picoType: number;
  trackingGroupID?: number;
  dirty: boolean;
}

const deviceConfigs = ref<DeviceConfig[]>([]);
interface TrackingGroup {
  groupID: number;
  groupName: string;
}

const trackingGroups = ref<TrackingGroup[]>([]);

const loadData = async () => {
  try {
    const configRes = await axios.get('/api/hardware/get/device/configs', {
      withCredentials: true,
    });
    // Initialize a 'dirty' flag for each config
    deviceConfigs.value = configRes.data.configs.map((c: any) => ({ ...c, dirty: false }));
  } catch (err) {
    console.error("Failed to load device configs:", err);
  }

  try {
    const groupsRes = await axios.get('/api/hardware/get/tracking/groups', {
      withCredentials: true,
    });
    trackingGroups.value = groupsRes.data.groups;
  } catch (err) {
    console.error("Failed to load tracking groups:", err);
  }
};

const updateAllDeviceConfigs = async () => {
  const promises = [];
  deviceConfigs.value.forEach((config: any) => {
    if (config.dirty) {
      const patchData: any = {
        readablePicoID: config.readablePicoID,
        picoType: config.picoType,
      };
      if (config.picoType === 2) {
        patchData.trackingGroupID = config.trackingGroupID;
      }
      promises.push(
        axios.patch(
          `/api/hardware/patch/device/config/${config.picoID}`,
          patchData,
          { withCredentials: true }
        ).then(() => {
          config.dirty = false;
        }).catch(err => {
          console.error(`Failed to patch device config ${config.picoID}:`, err);
        })
      );
    }
  });
  try {
    await Promise.all(promises);
    alert("All updated changes are saved!");
  } catch (err) {
    alert("Some updates failed. See console for details.");
  }
};

const cancelChanges = async () => {
  // Reload initial data to revert unsaved changes
  await loadData();
};

onMounted(() => {
  loadData();
});
</script>

<style scoped>
/* Ensure the table container allows horizontal scrolling on smaller screens */
.table-container {
  width: 100%;
  overflow-x: auto;
}

/* Style the table */
table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}

/* Style the table headers and cells */
th, td {
  border: 1px solid #ccc;
  padding: 0.75rem;
  text-align: left;
  white-space: nowrap; /* Prevent text from breaking in an ugly way */
}

/* Make inputs and select fields responsive */
input[type="text"], select {
  width: 100%;
  padding: 0.5rem;
  box-sizing: border-box;
  font-size: 1rem;
}

/* Style the button */
button {
  padding: 0.5rem;
  cursor: pointer;
  background-color: var(--primary-dark-bg);
  color: white;
  border: none;
  border-radius: 5px;
  transition: background 0.3s ease;
}

button:hover {
  background-color: var(--primary-dark-bg-hover);
}

/* Mobile Styles */
@media (max-width: 768px) {
  .table-container {
    overflow-x: auto;
    display: block;
  }

  /* Reduce padding and font sizes */
  th, td {
    padding: 0.5rem;
    font-size: 0.875rem;
  }

  /* Hide Pico ID and Tracking Group on very small screens */
  th:nth-child(1), td:nth-child(1),
  th:nth-child(4), td:nth-child(4) {
    display: none;
  }

  /* Ensure input fields are touch-friendly */
  input[type="text"], select {
    font-size: 0.875rem;
  }

  /* Reduce button size */
  button {
    font-size: 0.875rem;
    padding: 0.4rem;
  }
}
</style>
