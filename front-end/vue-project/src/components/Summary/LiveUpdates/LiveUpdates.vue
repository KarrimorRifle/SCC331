<script setup lang="ts">
import { PropType, ref, computed } from 'vue';
import { getTextColour } from '../../../utils/helper/colorUtils';
import UserMovementModal from './UserMovementModal.vue'; 

// Props
const props = defineProps({
  userIds: {
    type: Array as PropType<number[]>,
    required: true,
  },
  areaKey:{
    type: Number, 
    required: true,
  },
  updates: {
    type: Object as PropType<Record<number, { logged_at: string; roomID: number }[]>>,
    required: true,
  },
  fullUpdates: {  // Pass all updates for accurate modal data
    type: Object as PropType<Record<number, { logged_at: string; roomID: number }[]>>,
  },
  overlayAreasConstant: {
    type: Array as PropType<{ label: string; color: string; position: object }[]>,
    required: true,
  },
});
// Modal state
const showModal = ref(false);
const selectedUserId = ref<number | null>(null);
const userRoomHistory = ref<{ roomLabel: string; loggedAt: string }[]>([]);

// Compute min/max timestamps from user data
const minMaxTimestamps = computed(() => {
  const timestamps: number[] = [];

  Object.values(props.updates).forEach(userUpdates => {
    userUpdates.forEach(({ logged_at }) => {
      timestamps.push(new Date(logged_at).getTime());
    });
  });

  if (timestamps.length === 0) return { min: null, max: null };

  return {
    min: new Date(Math.min(...timestamps)).toISOString().slice(0, 16), // Earliest timestamp
    max: new Date(Math.max(...timestamps) + 60000).toISOString().slice(0, 16), // Add 1 minute (60000 ms)
  };
});

// Time filter state (default to min/max timestamps)
const startTime = ref<string>(minMaxTimestamps.value.min || '');
const endTime = ref<string>(minMaxTimestamps.value.max || '');

// Watch for min/max timestamp updates
computed(() => {
  startTime.value = minMaxTimestamps.value.min || '';
  endTime.value = minMaxTimestamps.value.max || '';
});

// Function to show modal with user's **full movement history**
const openUserModal = (userId: number) => {
  selectedUserId.value = userId;
  showModal.value = true;

  const userData = props.fullUpdates?.[userId] || props.updates[userId];

  // Retrieve **full history** of the selected user across all areas
  userRoomHistory.value = userData.map(({ logged_at, roomID }) => {
    return {
      roomLabel: `Area ${roomID}`,
      loggedAt: new Date(logged_at).toLocaleString(),
    };
  }) || [];
};

// Close modal function
const closeModal = () => {
  showModal.value = false;
  selectedUserId.value = null;
  userRoomHistory.value = [];
};

// Group user visits by area and then by time
const groupedUsersByRoom = computed(() => {
  const roomMap = new Map<string, { hour: string; hourNumeric: number; users: { userId: number; loggedAt: string }[] }[]>();

  // Convert filter timestamps to Date objects
  const start = startTime.value ? new Date(startTime.value).getTime() : null;
  const end = endTime.value ? new Date(endTime.value).getTime() : null;

  // ✅ **Determine Which Area Filter to Use**
  const areasToShow = 
    props.areaKey ? 
    props.overlayAreasConstant.filter(area => area.label === `Area ${props.areaKey}`) : 
    props.overlayAreasConstant;

  console.log("area to show: ", areasToShow);
  // Populate roomMap **only for the filtered users of the area**
  Object.entries(props.updates).forEach(([userId, userUpdates]) => {
    userUpdates.forEach(({ logged_at, roomID }) => {
      const date = new Date(logged_at);
      const timestamp = date.getTime();

      // ✅ **Apply time filtering**
      if (start !== null && end !== null && (timestamp < start || timestamp > end)) {
        return; // Skip entries outside the selected time range
      }

      const hour = date.toLocaleTimeString([], { hour: 'numeric', hour12: true });
      const hourNumeric = date.getHours();
      const fullTime = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });

      const formattedRoomLabel = `Area ${roomID}`;

      // ✅ **Ensure only selected areas are displayed**
      if (!areasToShow.some(area => area.label === formattedRoomLabel)) return;

      if (!roomMap.has(formattedRoomLabel)) {
        roomMap.set(formattedRoomLabel, []);
      }

      const roomEntry = roomMap.get(formattedRoomLabel);
      const existingHourEntry = roomEntry?.find(entry => entry.hour === hour);

      if (existingHourEntry) {
        existingHourEntry.users.push({ userId: Number(userId), loggedAt: fullTime });
      } else {
        roomEntry?.push({ hour, hourNumeric, users: [{ userId: Number(userId), loggedAt: fullTime }] });
      }
    });
  });

  // ✅ **Ensure correct area list is used (Summary = all, Dashboard = filtered)**
  return areasToShow.map((area) => ({
    roomLabel: area.label,
    roomColor: area.color,
    entries: (roomMap.get(area.label) || []).sort((a, b) => a.hourNumeric - b.hourNumeric),
  }));
});

</script>

<template>
  <div class="live-updates">
    <div class="live-updates-header">
      <h1>Live Updates</h1>
    </div>

    <!-- Time Filter Inputs -->
    <div class="date-time-filter">
      <div>
        <label for="start-time">Start Time:</label>
        <input id="start-time" type="datetime-local" v-model="startTime">
      </div>
      <div>
        <label for="end-time">End Time:</label>
        <input id="end-time" type="datetime-local" v-model="endTime">
      </div>
    </div>

    <!-- Room List -->
    <div class="room-list">
      <template v-if="groupedUsersByRoom.length">
        <div
          v-for="{ roomLabel, roomColor, entries } in groupedUsersByRoom"
          :key="roomLabel"
          class="room-card"
        >
          <h3 :style="{ backgroundColor: roomColor, color: getTextColour(roomColor) }">{{ roomLabel }}</h3>
          <template v-if="entries.length">
            <div v-for="{ hour, users } in entries" :key="hour" class="hour-group">
              <h4 class="hour-title">{{ hour }}</h4>
              <ul class="user-list">
                <li
                  v-for="({ userId, loggedAt }, index) in users"
                  :key="index"
                  class="user-item"
                  @click="openUserModal(userId)"
                >
                  👤 User {{ userId }} - <span class="timestamp">{{ loggedAt }}</span>
                </li>
              </ul>
            </div>
          </template>
        </div>
      </template>
    </div>

    <!-- User Movement Modal -->
    <UserMovementModal
      :showModal="showModal"
      :overlayAreasConstant="overlayAreasConstant"
      :selectedUserId="selectedUserId"
      :userRoomHistory="userRoomHistory"
      @close="closeModal"
    />
  </div>
</template>


<style scoped>
.live-updates {
  padding: 20px;
  background-color: #f8f8ff;
  border-top: 1px solid #ccc;
  color: black;
}

.date-time-filter {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background: #ffffff;
  border: 2px solid #568EA6;
  border-radius: 10px;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
}

.date-time-filter label {
  font-weight: bold;
  font-size: 14px;
  color: #305F72;
  margin-bottom: 5px;
}

.date-time-filter input {
  padding: 10px;
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 8px;
  outline: none;
  width: 220px;
  transition: border-color 0.3s ease;
}

.date-time-filter input:focus {
  border-color: #568EA6;
  box-shadow: 0 0 5px rgba(86, 142, 166, 0.5);
}

.room-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 10px;
}

.room-card {
  border: 2px solid #568EA6;
  border-radius: 10px;
  padding: 15px;
  background: white;
  text-align: center;
}

h3 {
  color: white;
  margin-bottom: 10px;
  padding: 10px;
  border-radius: 5px;
}

.hour-group {
  margin-top: 15px;
  padding: 10px;
  background: #f0f0f0;
  border-radius: 5px;
}

.hour-title {
  color: #F18C8E;
  font-size: 16px;
  margin-bottom: 5px;
}

.user-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.user-item {
  cursor: pointer;
  background: #f1f1f1;
  margin-bottom: 5px;
  padding: 8px;
  border-radius: 5px;
  font-size: 14px;
  text-align: left;
  cursor: pointer;
}

.timestamp {
  font-weight: bold;
  color: #568EA6;
  margin-left: 5px;
}

.no-data {
  grid-column: 1 / -1;
  text-align: center;
  font-size: 16px;
  color: #999;
  margin-top: 20px;
}
</style>
