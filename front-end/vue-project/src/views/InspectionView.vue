<template>
  <div class="inspection bg-light text-dark mt-0 p-0" style="flex-grow: 1;">
    <div id="date-time-selector" :class="['row', 'bg-theme', 'p-3', 'py-1', 'rounded', 'sticky-top']" style="z-index: 1;">
      <div class="w-100 row">
        <div class="g-3 align-middle align-items-center col-xxl-4 mt-0 col-md-4 col-12 flex-wrap d-flex">
          <div class="d-flex flex-row align-middle mt-2 mt-md-0">
            <label for="calendar-picker" class="form-label mb-0 d-flex align-items-center me-2">Date:</label>
            <input type="date" id="calendar-picker" v-model="selectedDate" class="form-control me-1" />
            <div class="d-flex align-items-center justify-content-center" style="min-width: 4rem;">
              <!-- Reintroducing day navigation buttons -->
              <button @click="prevDay" class="btn-sm btn btn-secondary me-1">
                <font-awesome-icon :icon="faChevronLeft" />
              </button>
              <button :disabled="!canGoNextDay" @click="nextDay" class="btn btn-sm btn-secondary">
                <font-awesome-icon :icon="faChevronRight" />
              </button>
            </div>
          </div>
        </div>
        <div class="row col-xxl-8 col-md-8 col-12 mt-2 mt-xxl-0">
          <div class="range-selector">
            <button @mousedown.prevent.stop="startHold(decrementTimeIndex)" @mouseup="stopHold" @mouseleave="stopHold" @touchstart.prevent.stop="startHold(decrementTimeIndex)" @touchend="stopHold" @touchcancel="stopHold" @contextmenu.prevent class="btn-sm btn btn-secondary me-1">
              <font-awesome-icon :icon="faChevronLeft" />
            </button>
            <input id="time-range" type="range" :min="0" :max="dayTimeKeys.length - 1" v-model="selectedDayTimeIndex" class="form-range">
            <button @mousedown.prevent.stop="startHold(incrementTimeIndex)" @mouseup="stopHold" @mouseleave="stopHold" @touchstart.prevent.stop="startHold(incrementTimeIndex)" @touchend="stopHold" @touchcancel="stopHold" @contextmenu.prevent class="btn btn-sm btn-secondary">
              <font-awesome-icon :icon="faChevronRight" />
            </button>
            <span style="min-width: 7rem" v-if="dayTimeKeys.length" class="align-middle">{{ formatTime(dayTimeKeys[0]) }} - {{ formatTime(dayTimeKeys[dayTimeKeys.length - 1]) }}</span>
            <span v-else>No time data available</span>
          </div>
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

    <div v-else class="movement-data p-3 pb-4 pb-md-0" style="flex-grow: 1; overflow: auto; padding-bottom: 60px;" @scroll="handleScroll" @click="hideDateTimeSelector">
      <div class="d-flex justify-content-between align-items-center">
        <h4 class="current-time me-2">{{ formatTime(selectedTime) }}</h4>
        <div class="selected-filters" v-if="selectedFilterPicoIDs.length || selectedFilterTypes.length || selectedFilterRooms.length" style="margin-bottom: 10px;">
          <div v-if="selectedFilterPicoIDs.length">
            PicoIDs:
            <span v-for="id in selectedFilterPicoIDs" :key="id" style="background: #eee; padding: 2px 5px; margin-right: 5px; border-radius: 3px;">
              <button type="button" style="border:none; background:none;" @click="removeSelected('picoIDs', id)">{{ id }} X</button>
            </span>
          </div>
          <div v-if="selectedFilterTypes.length">
            Types:
            <span v-for="type in selectedFilterTypes" :key="type" style="background: #eee; padding: 2px 5px; margin-right: 5px; border-radius: 3px;">
              <button type="button" style="border:none; background:none;" @click="removeSelected('types', type)">{{ type }} X</button>
            </span>
          </div>
          <div v-if="selectedFilterRooms.length">
            Rooms:
            <span v-for="room in selectedFilterRooms" :key="room" style="background: #eee; padding: 2px 5px; margin-right: 5px; border-radius: 3px;">
              {{ room }} <button type="button" style="border:none; background:none;" @click="removeSelected('rooms', room)">{{ room }} X</button>
            </span>
          </div>
        </div>
        <div class="filter-container" style="position: relative;">
          <button class="btn btn-sm btn-secondary" @click="toggleFilter" ref="filterButton">Filter</button>
          <div v-if="showFilter" class="filter-popout card p-2" style="position: absolute; top: 100%; right: 0; z-index: 1000; width: 15rem;" ref="filterPopout">
            <div class="mb-2">
              <label>
                PicoID:
                <input type="text" v-model="searchPico"
                       @focus="searchPicoFocus = true; searchPicoIndex = 0"
                       @blur="handleSearchBlur('picoIDs')"
                       @keydown="handleKeyDown('picoIDs', $event)"
                       class="form-control form-control-sm" placeholder="Search PicoID">
              </label>
              <ul data-category="picoIDs" v-if="searchPicoFocus && searchPico" class="dropdown-list">
                <li v-for="(id, index) in picoSuggestions" :key="id"
                    :class="{ active: index === searchPicoIndex }"
                    @mousedown.prevent="selectSuggestion('picoIDs', id)">
                  {{ id }}
                </li>
              </ul>
            </div>
            <div class="mb-2">
              <label>
                Pico Type:
                <input type="text" v-model="searchType"
                       @focus="searchTypeFocus = true; searchTypeIndex = 0"
                       @blur="handleSearchBlur('types')"
                       @keydown="handleKeyDown('types', $event)"
                       class="form-control form-control-sm" placeholder="Search Type">
              </label>
              <ul data-category="types" v-if="searchTypeFocus && searchType" class="dropdown-list">
                <li v-for="(t, index) in typeSuggestions" :key="t"
                    :class="{ active: index === searchTypeIndex }"
                    @mousedown.prevent="selectSuggestion('types', t)">
                  {{ t }}
                </li>
              </ul>
            </div>
            <div class="mb-2">
              <label>
                Room:
                <input type="text" v-model="searchRoom"
                       @focus="searchRoomFocus = true; searchRoomIndex = 0"
                       @blur="handleSearchBlur('rooms')"
                       @keydown="handleKeyDown('rooms', $event)"
                       class="form-control form-control-sm" placeholder="Search Room">
              </label>
              <ul data-category="rooms" v-if="searchRoomFocus && searchRoom" class="dropdown-list">
                <li v-for="(r, index) in roomSuggestions" :key="r"
                    :class="{ active: index === searchRoomIndex }"
                    @mousedown.prevent="selectSuggestion('rooms', r)">
                  {{ r }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      <div class="row">
        <div v-for="(box, roomID) in boxes" :key="roomID" :id="'room-' + roomID" class="col-md-4 mb-4">
          <div class="card">
            <div @click="showTable[roomID] = !(showTable[roomID] ?? true)" class="card-header text-dark d-flex justify-content-between align-middle" :style="{backgroundColor: box.colour || generateMutedColor(), borderColor: box.colour || generateMutedColor()}" :title="box.label.startsWith('%') ? 'Temporary value as no label available' : ''">
              <div class="fw-bold">{{ box.label || generateTempLabel() }}</div>
              <font-awesome-icon v-if="showTable[roomID] ?? true" :icon="faChevronUp" />
              <font-awesome-icon v-else :icon="faChevronDown" />
            </div>
            <div class="card-body" v-if="movementData[selectedTime]?.[roomID]">
              <!-- New statistical counter -->
              <div class="stats mb-2">
                <div class="d-inline-block rounded me-2 p-1">Total: {{ Object.keys(movementData[selectedTime]?.[roomID] || {}).length }}</div>
                <button
                  class="d-inline-block rounded me-2 p-1 border-0"
                  @click="scrollToRoom(room)" v-for="(box, room) in boxes"
                  :key="room"
                  :style="{'background-color': box.colour}"
                >
                  {{box.label}}:
                  {{
                    //movementData = Record<timestamp, Record<picoID, type>>
                    //previousLocation = Record<timestamp, record<picoID, locationInLast>>
                    Object.entries(movementData[selectedTime]?.[roomID] ?? {}).reduce(
                      (total, obj) => {
                        if(previousLocation[selectedTime][obj[0]] == room)
                          return total? total + 1 : 1;
                        return total? total : 0;
                      }, 0)
                  }}
                </button>
                <div class="d-inline-block rounded me-2 p-1">
                  New: {{ Object.values(previousLocation[selectedTime]).filter(location => location === 'NEW').length }}
                </div>
              </div>
              <table class="table rounded-top-1" v-show="showTable[roomID] ?? true">
                <thead class="rounded-top-1">
                  <tr class="rounded-top-1">
                    <th class="rounded-top-1 rounded-end-0"
                        @click="sortBy('picoID')"
                        style="font-weight: 600; background-color: rgb(200, 200, 200); cursor: pointer;">
                      picoID <span v-html="getArrows('picoID')"></span>
                    </th>
                    <th @click="sortBy('type')"
                        style="font-weight: 600; background-color: rgb(200, 200, 200); cursor: pointer;">
                      Type <span v-html="getArrows('type')"></span>
                    </th>
                    <th class="rounded-top-1 rounded-start-0"
                        @click="sortBy('cameFrom')"
                        style="font-weight: 600; background-color: rgb(200, 200, 200); cursor: pointer;">
                      Came From <span v-html="getArrows('cameFrom')"></span>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="([picoID, type]) in Object.entries(movementData[selectedTime][roomID] || {}).filter(([picoID, type]) => {
                      const filterPico = selectedFilterPicoIDs.length ? selectedFilterPicoIDs.includes(picoID) : true;
                      const filterType = selectedFilterTypes.length ? selectedFilterTypes.includes(type) : true;
                      const filterRoom = selectedFilterRooms.length ? selectedFilterRooms.includes(previousLocation[selectedTime][picoID]) : true;
                      return filterPico && filterType && filterRoom;
                  }).sort((a, b) => {
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
        <div id="deactivated-devices" class="col-md-12 mb-4">
          <div class="card">
            <div class="card-header d-flex justify-content-between" @click="showTable['deactivated'] = !(showTable['deactivated'] ?? true)">
              <div class="fw-bold">Deactivated Devices</div>
              <font-awesome-icon v-if="showTable['deactivated'] ?? true" :icon="faChevronUp" />
              <font-awesome-icon v-else :icon="faChevronDown" />
            </div>
            <div class="card-body" v-if="movementData[selectedTime]">
              <div class="stats mb-2">
                <div class="d-inline rounded me-2 p-1">Total: {{ Object.keys(filteredDeactivatedDevices || {}).length }}</div>
                <div class="d-inline rounded me-2 p-1"
                  v-for="(box, roomID) in boxes"
                  :key="roomID" :style="{'background-color': box.colour}"
                >
                  {{box.label}}:
                  {{
                    //previousLocation = Record<timestamp, record<picoID, locationInLast>>
                    filteredDeactivatedDevices.reduce(
                      (total, [picoID, lastRoom]) => {
                        if(lastRoom == roomID)
                          return total + 1;
                        return total;
                      }
                    , 0)
                  }}
              </div>
              </div>
              <table class="table" v-show="showTable['deactivated'] ?? true">
                <thead>
                  <tr>
                    <th>picoID</th>
                    <th>Last Type</th>
                    <th>Last Seen</th>
                    <th>Last Room</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="([picoID, lastRoom]) in filteredDeactivatedDevices" :key="picoID">
                    <td>{{ picoID }}</td>
                    <td>{{ movementData[dayTimeKeys[selectedDayTimeIndex - 1 > -1 ? selectedDayTimeIndex - 1 : 0]][lastRoom][picoID] }}</td>
                    <td>{{ formatTime(dayTimeKeys[selectedDayTimeIndex - 1 > -1 ? selectedDayTimeIndex - 1 : 0]) }}</td>
                    <td :style="{backgroundColor: boxes[lastRoom]?.colour || '#FFFFFF'}">{{ boxes[lastRoom]?.label || lastRoom }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="quick-selects d-md-none fixed-bottom bg-light p-2 border-top" style="overflow-x: auto;">
      <div class="container-fluid">
        <div class="d-flex flex-nowrap justify-content-start">
          <button v-for="(box, roomID) in boxes"
                  :key="roomID"
                  @click="scrollToRoom(roomID)"
                  class="btn btn-sm text-dark me-2"
                  :style="{ backgroundColor: box.colour || generateMutedColor(), borderColor: box.colour || generateMutedColor(), color: 'white' }">
            {{ box.label }} ({{ Object.keys(movementData[selectedTime]?.[roomID] || {}).length }})
          </button>
          <button @click="scrollToDeactivated"
                  class="btn btn-sm text-dark me-2"
                  style="background-color: #568EA6; border-color: #568EA6; color: white;">
            Deactivated ({{ Object.keys(filteredDeactivatedDevices).length }})
          </button>
        </div>
      </div>
    </div>

  <!-- Modal -->
  </div>
  <user-movement-modal class="text-dark" :show-modal="showModal" :selected-user-id="Number.parseInt(userID)" :user-room-history="userMovementHistory" @close="showModal = false"/>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, onBeforeUnmount } from 'vue';
import axios from 'axios';
import type { Record } from 'vue';
import type { presetListType, preset, boxType } from '@/utils/mapTypes';
import UserMovementModal from '@/components/Summary/LiveUpdates/UserMovementModal.vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faUser, faClipboardCheck, faShieldAlt, faSuitcase, faQuestion, faChevronLeft, faChevronRight, faChevronUp, faChevronDown, faL } from '@fortawesome/free-solid-svg-icons';

const showTable = ref<Record<string, boolean>>({});

// New reactive state for date-time selector
const isMobile = ref(window.innerWidth < 768);
window.addEventListener('resize', () => {
  isMobile.value = window.innerWidth < 768;
});

const showModal = ref(false);
const isLoading = ref(false);
const movementData = ref<Record<string, Record<string, Record<string, string>>>>({});
const boxes = ref<Record<string, { label: string; colour: string }>>({});

const userID = ref<string>("");
const userMovementHistory = ref<{ roomLabel: string; loggedAt: string }[]>([]);

const hideHeader = ref(false);
let lastScrollTop = 0;

const handleScroll = (event: Event) => {
  const target = event.target as HTMLElement;
  const scrollTop = target.scrollTop;
  hideHeader.value = scrollTop > lastScrollTop;
  lastScrollTop = scrollTop;
};

const startOfDay = new Date();
startOfDay.setHours(0,0,0,0);
const endOfDay = new Date();
endOfDay.setHours(23,59,59,999);

const fetchMovementData = async () => {
  try {
    isLoading.value = true;
    const response = await axios.get('http://localhost:5003/movement', {
      headers: {
        'time_start': startOfDay.toISOString(),
        'time_end': endOfDay.toISOString()
      },
      withCredentials: true
    });
    isLoading.value = false;
    // Detect and fill gaps in timestamps
    const temp = response.data;
    const timestamps = Object.keys(temp).sort();
    for (let i = 1; i < timestamps.length; i++) {
      const prevTime = new Date(timestamps[i - 1]);
      const currTime = new Date(timestamps[i]);
      const diff = (currTime.getTime() - prevTime.getTime()) / 1000; // difference in seconds

      if (diff > 60) { // assuming a gap is more than 60 seconds
        const newTime = new Date(prevTime.getTime() + 60000).toISOString(); // add 1 minute
        temp[newTime] = {}; // add empty data for the new timestamp
      }
    }

    const sortedTemp = Object.keys(temp).sort().reduce((acc, key) => {
      acc[key] = temp[key];
      return acc;
    }, {});

    movementData.value = sortedTemp;

  } catch (error) {
    if (error.response?.status === 404) {
      movementData.value = {};
    }
    console.error('Error fetching movement data:', error);
  }
};

const timeKeys = computed(() => Object.keys(movementData.value));

const selectedDate = ref(new Date().toISOString().slice(0,10));
watch(selectedDate, (newVal) => {
  const [year, month, day] = newVal.split('-').map(Number);
  startOfDay.setFullYear(year, month - 1, day);
  startOfDay.setHours(0,0,0,0);
  endOfDay.setFullYear(year, month - 1, day);
  endOfDay.setHours(23,59,59,999);
  fetchMovementData();
});

const dayTimeKeys = computed(() => timeKeys.value.filter(t => {
  return new Date(t).toISOString().slice(0,10) === selectedDate.value;
}));

const selectedDayTimeIndex = ref(0);
const selectedTime = computed(() => dayTimeKeys.value[selectedDayTimeIndex.value]);

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

const filteredDeactivatedDevices = computed(() => {
  if (!selectedTime.value) return [];
  return Object.entries(deactivated.value[selectedTime.value] || {}).filter(([picoID, lastRoom]) => {
    const filterPico = selectedFilterPicoIDs.value.length ? selectedFilterPicoIDs.value.includes(picoID) : true;
    const filterRoom = selectedFilterRooms.value.length ? selectedFilterRooms.value.includes(lastRoom) : true;
    return filterPico && filterRoom;
  }).sort((a, b) => {
    let comp = 0;
    if (sortColumn.value === 'picoID') {
      comp = a[0].localeCompare(b[0]);
    } else if (sortColumn.value === 'lastRoom') {
      comp = a[1].localeCompare(b[1]);
    }
    return sortDirection.value === 'asc' ? comp : -comp;
  });
});

const formatTime = (time: string) => {
  if(!time) return '';
  const date = new Date(time);
  return date.toLocaleTimeString().slice(0,5);
};

let labelIndex = 0;
const generateTempLabel = () => {
  const callsigns = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "India", "Juliet", "Kilo", "Lima", "Mike", "November", "Oscar", "Papa", "Quebec", "Romeo", "Sierra", "Tango", "Uniform", "Victor", "Whiskey", "X-ray", "Yankee", "Zulu"];
  return `%${callsigns[labelIndex++]}`;
};

let colorIndex = 0;
const generateMutedColor = () => {
  const mutedColors = ["#b0c4de", "#d3d3d3", "#add8e6", "#e0ffff", "#f0e68c", "#dda0dd", "#ffb6c1"];
  return mutedColors[colorIndex++ % mutedColors.length];
};

onMounted(async () => {
  isLoading.value = true;
  // Fetch initial data on mount
  await fetchMovementData();
  let presetData
  try {
    const presetListData = (await axios.get<presetListType>("http://localhost:5010/presets", { withCredentials: true })).data;
    const defaultID = presetListData.default;
    presetData = (await axios.get<preset>(`http://localhost:5010/presets/${defaultID}`, { withCredentials: true })).data;
  } catch {
    console.error("Unable to fetch preset data");
  }

  if(presetData?.boxes)
    presetData.boxes.forEach((box: boxType) => {
      boxes.value[box.roomID] = {
        label: box.label,
        colour: box.colour,
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

  isLoading.value = false;
});

const fetchUserMovementData = async () => {
  if (userID.value && selectedTime.value) {
    try {
      const response = await axios.get(`http://localhost:5003/pico/${userID.value}`, { data: {time: selectedTime.value},withCredentials: true });
      const picoMovementData = response.data.movement;
      // Add console.log to see the object
      userMovementHistory.value = Object.entries(picoMovementData).map(([timestamp, roomID]) => ({
        roomLabel: boxes.value[roomID as string].label, // he hard coded the area names... bad coding practice- will bring this up
        loggedAt: timestamp,
      }));
      // console.log('Object:', movementData.value[new Date(new Date(selectedTime.value).getTime() - 60000).toISOString()][lastRoom][picoID]);
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

// New method for quick room selection scrolling
const scrollToRoom = (roomID: string) => {
  const element = document.getElementById('room-' + roomID);
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
};

// New method for quick jump to deactivated devices
const scrollToDeactivated = () => {
  const element = document.getElementById('deactivated-devices');
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
};

const showFilter = ref(false);
const filterPopout = ref<HTMLElement | null>(null);
const filterButton = ref<HTMLElement | null>(null);

const toggleFilter = () => {
  showFilter.value = !showFilter.value;
  if (showFilter.value) {
    document.addEventListener('click', handleClickOutsideFilter);
  } else {
    document.removeEventListener('click', handleClickOutsideFilter);
  }
};

const handleClickOutsideFilter = (event: MouseEvent) => {
  if (filterPopout.value && !filterPopout.value.contains(event.target as Node) && filterButton.value && !filterButton.value.contains(event.target as Node)) {
    showFilter.value = false;
    document.removeEventListener('click', handleClickOutsideFilter);
  }
};

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutsideFilter);
});

const searchPico = ref('');
const searchType = ref('');
const searchRoom = ref('');

const selectedFilterPicoIDs = ref<string[]>([]);
const selectedFilterTypes = ref<string[]>([]);
const selectedFilterRooms = ref<string[]>([]);

// Create computed currentData based on selectedTime
const currentData = computed(() => movementData.value[selectedTime.value] || {});

const availablePicoIDs = computed(() => {
  let ids: string[] = [];
  Object.values(currentData.value).forEach(occupants => {
    ids.push(...Object.keys(occupants));
  });
  return [...new Set(ids)];
});

const availablePicoTypes = computed(() => {
  let types: string[] = [];
  Object.values(currentData.value).forEach(occupants => {
    types.push(...Object.values(occupants));
  });
  return [...new Set(types)];
});

const availableRooms = computed(() => {
  return Object.keys(currentData.value);
});

// Methods to add and remove filters
const addSelected = (category: string, value: string) => {
  if (category === 'picoIDs' && !selectedFilterPicoIDs.value.includes(value)) {
    selectedFilterPicoIDs.value.push(value);
  } else if (category === 'types' && !selectedFilterTypes.value.includes(value)) {
    selectedFilterTypes.value.push(value);
  } else if (category === 'rooms' && !selectedFilterRooms.value.includes(value)) {
    selectedFilterRooms.value.push(value);
  }
};

const removeSelected = (category: string, value: string) => {
  if (category === 'picoIDs') {
    selectedFilterPicoIDs.value = selectedFilterPicoIDs.value.filter(v => v !== value);
  } else if (category === 'types') {
    selectedFilterTypes.value = selectedFilterTypes.value.filter(v => v !== value);
  } else if (category === 'rooms') {
    selectedFilterRooms.value = selectedFilterRooms.value.filter(v => v !== value);
  }
};

// New reactive variables for keyboard navigation in filter popout
const searchPicoFocus = ref(false);
const searchTypeFocus = ref(false);
const searchRoomFocus = ref(false);

const searchPicoIndex = ref(0);
const searchTypeIndex = ref(0);
const searchRoomIndex = ref(0);

const filteredPicoIDs = computed(() =>
  searchPico.value
    ? availablePicoIDs.value.filter(i => i.toLowerCase().includes(searchPico.value.toLowerCase()))
    : []
);
const filteredPicoTypes = computed(() =>
  searchType.value
    ? availablePicoTypes.value.filter(t => t.toLowerCase().includes(searchType.value.toLowerCase()))
    : []
);
const filteredRooms = computed(() =>
  searchRoom.value
    ? availableRooms.value.filter(r => r.toLowerCase().includes(searchRoom.value.toLowerCase()))
    : []
);

// NEW: Create suggestion lists that match the displayed dropdown
const picoSuggestions = computed(() =>
  filteredPicoIDs.value.filter(item => !selectedFilterPicoIDs.value.includes(item))
);
const typeSuggestions = computed(() =>
  filteredPicoTypes.value.filter(item => !selectedFilterTypes.value.includes(item))
);
const roomSuggestions = computed(() =>
  filteredRooms.value.filter(item => !selectedFilterRooms.value.includes(item))
);

const scrollToActiveSuggestion = (category: string) => {
  const list = document.querySelector(`.dropdown-list[data-category="${category}"]`) as HTMLElement;
  if (list) {
    const activeItem = list.querySelector("li.active") as HTMLElement;
    if (activeItem) {
      const targetScrollTop = activeItem.offsetTop - list.clientHeight / 2 + activeItem.clientHeight / 2;
      list.scrollTo({ top: targetScrollTop});
    }
  }
};

const handleKeyDown = (category: string, event: KeyboardEvent) => {
  if(event.key === "Escape") {
    showFilter.value = false;
  }
  if (category === 'picoIDs') {
    if (event.key === 'ArrowDown') {
      if (searchPicoIndex.value < picoSuggestions.value.length - 1) {
        searchPicoIndex.value++;
        scrollToActiveSuggestion('picoIDs');
      }
      event.preventDefault();
    } else if (event.key === 'ArrowUp') {
      if (searchPicoIndex.value > 0) {
        searchPicoIndex.value--;
        scrollToActiveSuggestion('picoIDs');
      }
      event.preventDefault();
    } else if (event.key === 'Enter') {
      if (picoSuggestions.value.length > 0) {
        addSelected('picoIDs', picoSuggestions.value[searchPicoIndex.value]);
        searchPico.value = '';
      }
      event.preventDefault();
    }
  } else if (category === 'types') {
    if (event.key === 'ArrowDown') {
      if (searchTypeIndex.value < typeSuggestions.value.length - 1) {
        searchTypeIndex.value++;
        scrollToActiveSuggestion('types');
      }
      event.preventDefault();
    } else if (event.key === 'ArrowUp') {
      if (searchTypeIndex.value > 0) {
        searchTypeIndex.value--;
        scrollToActiveSuggestion('types');
      }
      event.preventDefault();
    } else if (event.key === 'Enter') {
      if (typeSuggestions.value.length > 0) {
        addSelected('types', typeSuggestions.value[searchTypeIndex.value]);
        searchType.value = '';
      }
      event.preventDefault();
    }
  } else if (category === 'rooms') {
    if (event.key === 'ArrowDown') {
      if (searchRoomIndex.value < roomSuggestions.value.length - 1) {
        searchRoomIndex.value++;
        scrollToActiveSuggestion('rooms');
      }
      event.preventDefault();
    } else if (event.key === 'ArrowUp') {
      if (searchRoomIndex.value > 0) {
        searchRoomIndex.value--;
        scrollToActiveSuggestion('rooms');
      }
      event.preventDefault();
    } else if (event.key === 'Enter') {
      if (roomSuggestions.value.length > 0) {
        addSelected('rooms', roomSuggestions.value[searchRoomIndex.value]);
        searchRoom.value = '';
      }
      event.preventDefault();
    }
  }
};

const selectSuggestion = (category: string, value: string) => {
  addSelected(category, value);
  if (category === 'picoIDs') {
    searchPico.value = '';
    // Do not set searchPicoFocus to false.
  } else if (category === 'types') {
    searchType.value = '';
    // Do not set searchTypeFocus to false.
  } else if (category === 'rooms') {
    searchRoom.value = '';
    // Do not set searchRoomFocus to false.
  }
};

const handleSearchBlur = (category: string) => {
  setTimeout(() => {
    if(category === 'picoIDs') searchPicoFocus.value = false;
    else if(category === 'types') searchTypeFocus.value = false;
    else if(category === 'rooms') searchRoomFocus.value = false;
  }, 100);
};

let holdTimer: number | null = null;
let holdCounter = 0;

const startHold = (action: () => void) => {
  action();
  holdCounter = 0;
  holdTimer = window.setInterval(() => {
    action();
    holdCounter++;
    if (holdCounter > 20) {
      clearInterval(holdTimer!);
      holdTimer = window.setInterval(action, 50); // 2x speed
    }
    if (holdCounter > 40) {
      clearInterval(holdTimer!);
      holdTimer = window.setInterval(action, 10); // 10x speed
    }
  }, 100);
};

const stopHold = () => {
  if (holdTimer !== null) {
    clearInterval(holdTimer);
    holdTimer = null;
  }
};

const decrementTimeIndex = () => {
  selectedDayTimeIndex.value = Math.max(0, selectedDayTimeIndex.value - 1);
};

const incrementTimeIndex = () => {
  selectedDayTimeIndex.value = Math.min(dayTimeKeys.value.length - 1, selectedDayTimeIndex.value + 1);
};

const prevDay = () => {
  const current = new Date(selectedDate.value);
  current.setDate(current.getDate() - 1);
  selectedDate.value = current.toISOString().slice(0,10);
};

const nextDay = () => {
  const current = new Date(selectedDate.value);
  const today = new Date();
  today.setHours(0,0,0,0);
  current.setDate(current.getDate() + 1);
  if (current > today) {
    current.setTime(today.getTime());
  }
  selectedDate.value = current.toISOString().slice(0,10);
};

const canGoNextDay = computed(() => {
  const selected = new Date(selectedDate.value);
  selected.setHours(0,0,0,0);
  const today = new Date();
  today.setHours(0,0,0,0);
  return selected < today;
});
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
  align-items: center;
  gap: 20px;
  text-align: center;
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

#day-select {
  width: 150px;
}

.dropdown-list {
  max-height: 150px;
  overflow-y: auto;
  margin: 0;
  padding: 0;
  border: 1px solid #ccc;
  list-style: none;
  position: absolute;
  width: 100%;
  max-width: 15rem;
  background: white;
  z-index: 10;
}
.dropdown-list li {
  padding: 5px 10px;
  cursor: pointer;
}
.dropdown-list li.active {
  background-color: #e0e0e0;
}
</style>
