<script setup lang="ts">
import { PropType, ref, computed, watch } from 'vue';

// Props for user IDs, updates, and room configuration
const props = defineProps({
  userIds: {
    type: Array as PropType<number[]>,
    required: true,
  },
  updates: {
    type: Object as PropType<Record<number, { logged_at: string; roomID: number }[]>>,
    required: true,
  },
  overlayAreasConstant: {
    type: Array as PropType<{ label: string; color: string; position: object }[]>,
    required: true,
  },
});

// Reactive state for selected users
const selectedUsers = ref<number[]>([...props.userIds]);

// Calculate the earliest and latest timestamps from the updates
const allTimestamps = computed(() =>
  Object.values(props.updates)
    .flat()
    .map(update => new Date(update.logged_at))
    .sort((a, b) => a.getTime() - b.getTime())
);

// Initialize startDate and endDate based on timestamps
const startDate = ref(
  allTimestamps.value.length
    ? allTimestamps.value[0].toISOString().slice(0, 16)
    : new Date().toISOString().slice(0, 16)
);

// Add an extra minute to the original end date
const endDate = ref(
  allTimestamps.value.length
    ? new Date(allTimestamps.value[allTimestamps.value.length - 1].getTime() + 60000)
        .toISOString()
        .slice(0, 16)
    : new Date(new Date().getTime() + 60000).toISOString().slice(0, 16)
);
// Watch for updates in timestamps and adjust startDate and endDate dynamically
watch(allTimestamps, (timestamps) => {
  if (timestamps.length) {
    startDate.value = timestamps[0].toISOString().slice(0, 16);
    endDate.value = timestamps[timestamps.length - 1].toISOString().slice(0, 16);
  }
});

// Group user visits by area and then by time
const groupedUsersByRoom = computed(() => {
  const roomMap = new Map<string, { hour: string; users: { userId: number; loggedAt: string }[] }[]>();

  // Populate roomMap with updates
  Object.entries(props.updates).forEach(([userId, updates]) => {
    updates.forEach(({ logged_at, roomID }) => {
      const date = new Date(logged_at);
      const hour = date.toLocaleTimeString([], { hour: 'numeric', hour12: true });
      const fullTime = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });

      // Map roomID to room label
      const roomLabel = props.overlayAreasConstant[roomID - 1]?.label || `Room ${roomID}`;

      // Apply Date-Time Range Filtering
      if (date >= new Date(startDate.value) && date <= new Date(endDate.value)) {
        if (!roomMap.has(roomLabel)) {
          roomMap.set(roomLabel, []);
        }
        const roomEntry = roomMap.get(roomLabel);
        const existingHourEntry = roomEntry?.find(entry => entry.hour === hour);

        if (existingHourEntry) {
          existingHourEntry.users.push({ userId: Number(userId), loggedAt: fullTime });
        } else {
          roomEntry?.push({
            hour,
            users: [{ userId: Number(userId), loggedAt: fullTime }],
          });
        }
      }
    });
  });

  // Ensure all areas from overlayAreasConstant are included
  props.overlayAreasConstant.forEach((area) => {
    if (!roomMap.has(area.label)) {
      roomMap.set(area.label, []); // Add empty area with no users
    }
  });

  // Convert map to array and sort it based on the order in overlayAreasConstant
  return props.overlayAreasConstant.map((area) => {
    const entries = roomMap.get(area.label) || [];
    return {
      roomLabel: area.label,
      roomColor: area.color,
      entries,
    };
  });
});

</script>

<template>
  <div class="live-updates">
    <div class="live-updates-header">
      <h1>Live Updates</h1>
    </div>

    <!-- Date-Time Filter -->
    <div class="date-time-filter">
      <label>Start Date & Time:</label>
      <input type="datetime-local" v-model="startDate" />
      <label>End Date & Time:</label>
      <input type="datetime-local" v-model="endDate" />
    </div>

    <!-- Room List -->
    <div class="room-list">
      <template v-if="groupedUsersByRoom.length">
        <div
          v-for="{ roomLabel, roomColor, entries } in groupedUsersByRoom"
          :key="roomLabel"
          class="room-card"
        >
          <h3 :style="{ backgroundColor: roomColor }">{{ roomLabel }}</h3>
          <template v-if="entries.length">
            <div
              v-for="{ hour, users } in entries"
              :key="hour"
              class="hour-group"
            >
              <h4 class="hour-title">{{ hour }}</h4>
              <ul class="user-list">
                <li
                  v-for="({ userId, loggedAt }, index) in users"
                  :key="index"
                  class="user-item"
                >
                  👤 User {{ userId }} - <span class="timestamp">{{ loggedAt }}</span>
                </li>
              </ul>
            </div>
          </template>
          <template v-else>
            <p class="no-users">No users entered this area.</p>
          </template>
        </div>
      </template>
      <template v-else>
        <div class="no-data">
          <p>No data available for the selected time range.</p>
        </div>
      </template>
    </div>
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
  background: #f1f1f1;
  margin-bottom: 5px;
  padding: 8px;
  border-radius: 5px;
  font-size: 14px;
  text-align: center;
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
