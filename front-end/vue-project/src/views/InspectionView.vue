<template>
  <div class="inspection bg-light text-dark mt-0 p-0" style="flex-grow: 1;">
    <div :class="['row', 'bg-theme', 'p-3', 'pt-0', 'rounded', 'sticky-top', { 'd-none': hideHeader }]" style="z-index: 1;">
      <div class="g-3 align-items-end col-lg-5 mt-0 col-12">
        <div class="row mb-2">
          <label for="start-time" class="col-form-label col-1">Start:</label>
          <div class="col-5">
            <input id="start-time" type="date" v-model="startTime" class="form-control">
          </div>
          <label for="end-time" class="col-form-label col-1">End:</label>
          <div class="col-5">
            <input id="end-time" type="date" v-model="endTime" class="form-control">
          </div>
        </div>
      </div>
      <div class="row g-3 col-lg-7 col-12">
        <div class="range-selector">
          <label for="time-range" class="form-label">Select Time:</label>
          <input id="time-range" type="range" :min="0" :max="timeKeys.length - 1" v-model="selectedTimeIndex" class="form-range mb-3">
          <span v-if="timeKeys.length">{{ formatTime(timeKeys[0]) }} - {{ formatTime(timeKeys[timeKeys.length - 1]) }}</span>
          <span v-else>No time data available</span>
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

    <div v-else class="movement-data p-3" style="flex-grow: 1; overflow: auto;" @scroll="handleScroll">
      <h4 class="current-time">{{ formatTime(timeKeys[selectedTimeIndex]) }}</h4>
      <div class="row">
        <div v-for="(box, roomID) in boxes" :key="roomID" class="col-md-4 mb-4">
          <div class="card">
            <div class="card-header text-dark" :style="{backgroundColor: box.colour || generateMutedColor(), borderColor: box.colour || generateMutedColor()}" :title="box.label.startsWith('%') ? 'Temporary value as no label available' : ''">
              {{ box.label || generateTempLabel() }}
            </div>
            <div class="card-body">
              <table class="table rounded-top-1">
                <thead class="rounded-top-1">
                  <tr class="rounded-top-1">
                    <th class="rounded-top-1 rounded-end-0"
                        @click="sortBy('picoID')"
                        style="font-weight: 600; background-color: rgb(200, 200, 200); cursor: pointer;">
                      picoID <span>{{ getArrows('picoID') }}</span>
                    </th>
                    <th @click="sortBy('type')"
                        style="font-weight: 600; background-color: rgb(200, 200, 200); cursor: pointer;">
                      Type <span>{{ getArrows('type') }}</span>
                    </th>
                    <th class="rounded-top-1 rounded-start-0"
                        @click="sortBy('cameFrom')"
                        style="font-weight: 600; background-color: rgb(200, 200, 200); cursor: pointer;">
                      Came From <span>{{ getArrows('cameFrom') }}</span>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="([picoID, type]) in Object.entries(movementData[selectedTime][roomID] || {}).sort((a, b) => {
                      let comp = 0;
                      if (sortColumn === 'picoID') {
                        comp = a[0].localeCompare(b[0]);
                      } else if (sortColumn === 'type') {
                        comp = a[1].localeCompare(b[1]);
                      } else {
                        const cameA = previousLocation[selectedTime][a[0]] || '';
                        const cameB = previousLocation[selectedTime][b[0]] || '';
                        comp = cameA.localeCompare(cameB);
                      }
                      return sortDirection === 'asc' ? comp : -comp;
                    })" :key="picoID" :class="{ 'new-row': previousLocation[selectedTime][picoID] === 'NEW' }">
                    <td @click="userID = picoID + ''; showModal = true" style="color: blue; text-decoration: underline; cursor: pointer;">{{ picoID }}</td>
                    <td>
                      <font-awesome-icon :icon="getIcon(type)" :style="{ color: getRoleColor(type) }"/> {{ type }}
                    </td>
                    <td :style="{backgroundColor: boxes[previousLocation[selectedTime][picoID]]?.colour}">
                      {{ boxes[previousLocation[selectedTime][picoID]]?.label || previousLocation[selectedTime][picoID] }}
                    </td>
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
                    <th>Last Room</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(lastRoom, picoID) in deactivated[selectedTime]" :key="picoID">
                    <td>{{ picoID }}</td>
                    <td>{{ movementData[selectedTime][picoID]?.type || 'Unknown' }}</td>
                    <td>{{ formatTime(selectedTime) }}</td>
                    <td :style="{backgroundColor: boxes[lastRoom].colour || '#FFFFFF'}">{{ boxes[lastRoom].label }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- Modal -->

  <user-movement-modal class="text-dark" :show-modal="showModal" :selected-user-id="Number.parseInt(userID)" :overlay-areas-constant="boxData" :user-room-history="userMovementHistory" @close="showModal = false"/>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import axios from 'axios';
import type { Record } from 'vue';
import type { presetListType, preset, boxType } from '@/utils/mapTypes';
import UserMovementModal from '@/components/Summary/LiveUpdates/UserMovementModal.vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faUser, faClipboardCheck, faShieldAlt, faSuitcase, faQuestion } from '@fortawesome/free-solid-svg-icons';

const showModal = ref(false);
const isLoading = ref(false);
const movementData = ref<Record<string, Record<string, Record<string, string>>>>({});
const boxes = ref<Record<string, { label: string; colour: string }>>({});

const userID = ref<string>("");
const userMovementHistory = ref<{ roomLabel: string; loggedAt: string }[]>([]);
const boxData = ref<{ label: string; color: string; position: object }[]>([]);

const hideHeader = ref(false);
let lastScrollTop = 0;

const handleScroll = (event: Event) => {
  const target = event.target as HTMLElement;
  const scrollTop = target.scrollTop;
  hideHeader.value = scrollTop > lastScrollTop;
  lastScrollTop = scrollTop;
};

// Default start time to the start of the day and end time to the end of the day
const startTime = ref(new Date(new Date().setHours(0, 0, 0, 0)).toISOString().slice(0,10));
const endTime = ref(new Date(new Date().setHours(23, 59, 59, 999)).toISOString().slice(0,10));

const fetchMovementData = async () => {
  try {
    const response = await axios.get('http://localhost:5003/movement', {
      withCredentials: true
    });
    movementData.value = response.data;
    console.log(response)
  } catch (error) {
    console.error('Error fetching movement data:', error);
  }
};

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
  const deactivated: Record<string, Record<string, string>> = {};
  timeKeys.value.forEach((time, index) => {
    const IDsInRooms: string[] = [];
    for (const room in movementData.value[time]) {
      IDsInRooms.push(...Object.keys(movementData.value[time][room]));
    }

    const previousTime = timeKeys.value[index - 1];
    if (previousTime) {
      const previousData = movementData.value[previousTime];
      deactivated[time] = Object.keys(previousData).reduce((acc, roomID) => {
        const occupants = previousData[roomID];
        for (const picoID in occupants) {
          if (!IDsInRooms.includes(picoID)) {
            acc[picoID] = roomID;
          }
        }
        return acc;
      }, {} as Record<string, string>);
    } else {
      deactivated[time] = {};
    }
  });
  return deactivated;
});

const formatTime = (time: string) => {
  const date = new Date(time);
  return window.innerWidth <= 768 ? date.toLocaleTimeString() : date.toLocaleString();
};

let labelIndex = 0;
const generateTempLabel = () => {
  const callsigns = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "India", "Juliet", "Kilo", "Lima", "Mike", "November", "Oscar", "Papa", "Quebec", "Romeo", "Sierra", "Tango", "Uniform", "Victor", "Whiskey", "X-ray", "Yankee", "Zulu"];
  return `%${callsigns[labelIndex++]}`;
};

let colorIndex = 0;
const generateMutedColor = () => {
  const mutedColors = ["#b0c4de", "#d3d3d3", "#add8e6", "#e0ffff", "#f0e68c", "#dda0dd", "#ffb6c1"];
  return mutedColors[colorIndex++];
};

onMounted(async () => {
  isLoading.value = true;
  // Fetch initial data on mount
  await fetchMovementData();
  const presetListData = (await axios.get<presetListType>("http://localhost:5010/presets", { withCredentials: true })).data;
  const defaultID = presetListData.default;
  const presetData = (await axios.get<preset>(`http://localhost:5010/presets/${defaultID}`, { withCredentials: true })).data;

  presetData.boxes.forEach((box: boxType) => {
    boxes.value[box.roomID] = {
      label: box.label,
      colour: box.colour
    };
  });

  // Generate temporary labels and colors for missing room IDs
  timeKeys.value.forEach(time => {
    const currentData = movementData.value[time];
    for (const roomID in currentData) {
      if (!boxes.value[roomID + ""]) {
        boxes.value[roomID + ""] = {
          label: generateTempLabel(),
          colour: generateMutedColor()
        };
      }
    }
  });

  boxData.value = [...presetData.boxes.map(box => ({
    label: boxes.value.label,
    color: boxes.value.colour,
    position: {
      ...box
    }
  }))]

  console.log(boxes.value);
  isLoading.value = false;
});

const fetchUserMovementData = async () => {
  if (userID.value && selectedTime.value) {
    try {
      const response = await axios.get(`http://localhost:5003/pico/${userID.value}`, { data: {time: selectedTime.value},withCredentials: true });
      const picoMovementData = response.data.movement;
      userMovementHistory.value = Object.entries(picoMovementData).map(([timestamp, roomID]) => ({
        roomLabel: roomID as string, // he hard coded the area names... bad coding practice- will bring this up
        loggedAt: timestamp,
      }));
    } catch (error) {
      console.error('Error fetching user movement data:', error);
    }
  }
};

watch([selectedTime, userID], fetchUserMovementData);

// Add helper function to return icon mapping based on type using imported icons
const getIcon = (type: string) => {
  switch (type.toLowerCase()) {
    case 'guard':
      return faShieldAlt;
    case 'luggage':
      return faSuitcase;
    case 'user':
      return faUser;
    case 'staff':
      return faClipboardCheck;
    default:
      return faQuestion;
  }
};

// New helper to return color per role
const getRoleColor = (type: string) => {
  switch (type.toLowerCase()) {
    case 'guard':
      return 'blue';
    case 'luggage':
      return 'grey';
    case 'user':
      return 'darkblue';
    case 'staff':
      return 'green';
    default:
      return 'black';
  }
};

const sortColumn = ref('cameFrom'); // options: 'picoID', 'type', 'cameFrom'
const sortDirection = ref('asc'); // options: 'asc', 'desc'

// Add helper to return arrow icons for header
const getArrows = (col: string) => {
  if(sortColumn.value === col) {
    return sortDirection.value === 'asc' ? '▲ ▽' : '△ ▼';
  }
  return '△ ▽';
};

// Add function to change sort column/direction on header click
const sortBy = (col: string) => {
  if (sortColumn.value === col) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortColumn.value = col;
    sortDirection.value = 'asc';
  }
};
</script>

<style scoped>
.inspection {
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.bg-theme {
  background-color: var(--primary-dark-bg);
  color: var(--primary-light-text);
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
  color: var(--negative-text);
}

.movement-data {
  display: flex;
  flex-direction: column;
  gap: 20px;
  flex-grow: 1;
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
  background-color: var(--primary-dark-bg);
  color: var(--primary-light-text);
  padding: 10px;
  font-weight: bold;
}

.card-body {
  padding: 10px;
}

.new-row > td {
  background-color: var(--positive);
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
  background-color: var(--primary-light-bg);
}
</style>
