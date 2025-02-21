<template>
  <div class="inspection bg-light text-dark mt-0 p-0">
    <div class="row bg-theme p-3 rounded">
      <div class="row g-3 align-items-end col-lg-7 mt-0 col-12">
        <div class="col-md-5">
          <label for="start-time" class="form-label">Start Time:</label>
          <input id="start-time" type="datetime-local" v-model="startTime" class="form-control">
        </div>
        <div class="col-md-5">
          <label for="end-time" class="form-label">End Time:</label>
          <input id="end-time" type="datetime-local" v-model="endTime" class="form-control">
        </div>
        <div class="col-md-2">
          <button @click="fetchMovementData" class="btn btn-primary w-100">Fetch Data</button>
        </div>
      </div>
      <div class="row g-3 col-lg-5 col-12">
        <div class="range-selector">
          <label for="time-range" class="form-label">Select Time:</label>
          <input id="time-range" type="range" :min="0" :max="timeKeys.length - 1" v-model="selectedTimeIndex" class="form-range mb-3">
          <span>{{ timeKeys[0] }} - {{ timeKeys[timeKeys.length - 1] }}</span>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="loading-throbber">
      <div class="spinner"></div>
      <p>Loading data...</p>
    </div>

    <div v-else-if="!movementData || Object.keys(movementData).length === 0" class="no-data">
      <p>No data selected</p>
    </div>

    <div v-else class="movement-data p-3">
      <h4 class="current-time">{{ timeKeys[selectedTimeIndex] }}</h4>
      <div class="row">
        <div v-for="(rooms, roomID) in movementData[selectedTime]" :key="roomID" class="col-md-4 mb-4">
          <div class="card">
            <div class="card-header">
              Room {{ roomID }}
            </div>
            <div class="card-body">
              <table class="table">
                <thead>
                  <tr>
                    <th>picoID</th>
                    <th>Type</th>
                    <th>Came From</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(type, picoID) in rooms" :key="picoID" :class="{ 'new-row': previousLocation[selectedTime][picoID] === 'NEW' }">
                    <td>{{ picoID }}</td>
                    <td>{{ type }}</td>
                    <td>{{ previousLocation[selectedTime][picoID] }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col-md-12 mb-4">
          <div class="card">
            <div class="card-header">
              Deactivated Devices
            </div>
            <div class="card-body">
              <table class="table">
                <thead>
                  <tr>
                    <th>picoID</th>
                    <th>Type</th>
                    <th>Last Seen</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="picoID in deactivated[selectedTime]" :key="picoID">
                    <td>{{ picoID }}</td>
                    <td>{{ movementData[selectedTime][picoID]?.type || 'Unknown' }}</td>
                    <td>{{ selectedTime }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import axios from 'axios';
import type { Record } from 'vue'; // Add this line

const showModal = ref(false);
const isLoading = ref(false);
const movementData = ref<Record<string, Record<string, Record<string, string>>>>({});

// Default start time to 3 hours before now and end time to now
const startTime = ref(new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString().slice(0, 16));
const endTime = ref(new Date().toISOString().slice(0, 16));

const fetchMovementData = async () => {
  isLoading.value = true;
  try {
    const response = await axios.get('http://localhost:5003/movement', {
      withCredentials: true
    });
    movementData.value = response.data;
    console.log(response)
  } catch (error) {
    console.error('Error fetching movement data:', error);
  } finally {
    isLoading.value = false;
  }
};

// Fetch initial data on mount
fetchMovementData();

const timeKeys = computed(() => Object.keys(movementData.value));
const selectedTimeIndex = ref(0);
const selectedTime = computed(() => timeKeys.value[selectedTimeIndex.value]);

const previousLocation = computed(() => {
  const result: Record<string, Record<string, string>> = {};

  timeKeys.value.forEach((time, index) => {
    result[time] = {};
    const currentData = movementData.value[time];

    for (const roomID in currentData) {
      const occupants = currentData[roomID];
      for (const picoID in occupants) {
        if (index === 0) {
          result[time][picoID] = 'Unknown';
        } else {
          const previousTime = timeKeys.value[index - 1];
          const previousData = movementData.value[previousTime];
          let found = false;

          for (const prevRoomID in previousData) {
            if (previousData[prevRoomID][picoID]) {
              result[time][picoID] = prevRoomID;
              found = true;
              break;
            }
          }

          if (!found) {
            result[time][picoID] = 'NEW';
          }
        }
      }
    }
  });

  return result;
});

const deactivated = computed(() => {
  const deactivated: Record<string, string[]> = {};
  timeKeys.value.forEach((time, index) => {
    const IDsInRooms: string[] = [];
    for (const room in movementData.value[time]) {
      IDsInRooms.push(...Object.keys(movementData.value[time][room]));
    }

    const previousTime = timeKeys.value[index - 1];
    if (previousTime) {
      const previousIDs = Object.keys(previousLocation.value[previousTime]);
      deactivated[time] = previousIDs.filter(id => !IDsInRooms.includes(id));
    } else {
      deactivated[time] = [];
    }
  });
  return deactivated;
});
</script>

<style scoped>
.inspection {
  padding: 20px;
}

.bg-theme {
  background-color: #305f72;
  color: white;
}

.time-selector {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.loading-throbber {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100px;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-top: 4px solid #568EA6;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.no-data {
  text-align: center;
  font-size: 16px;
  color: #999;
}

.movement-data {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.current-time {
  margin-bottom: 20px;
}

.range-selector {
  display: flex;
  align-items: end;
  gap: 20px;
}

.card {
  border: 1px solid #ccc;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  background-color: #305f72;
  color: white;
  padding: 10px;
  font-weight: bold;
}

.card-body {
  padding: 10px;
}

.new-row > td {
  background-color: #b6dfbf;
}

.deactivated-data {
  margin-top: 20px;
}

.deactivated-data table {
  width: 100%;
  border-collapse: collapse;
}

.deactivated-data th, .deactivated-data td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: left;
}

.deactivated-data th {
  background-color: #f2f2f2;
}
</style>
