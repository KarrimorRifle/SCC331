<script setup lang="ts">
import { ref, PropType, onMounted, onUnmounted, computed, defineProps, defineEmits} from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faExpand, faCompress, faExclamationTriangle} from '@fortawesome/free-solid-svg-icons';
import { handleWarningButtonPressed } from '@/utils/helper/warningUtils';
import { updateTabHeight } from '@/utils/helper/domUtils';
import { boxAndData } from '@/utils/mapTypes';
import { Sketch } from '@ckpack/vue-color';
import { usePresetStore } from '../utils/useFetchPresets';
import { sensorMapping } from '../stores/sensorTypeStore';
import LuggageMarker from './ObjectMarker/LuggageMarker.vue';
import PersonMarker from './ObjectMarker/PersonMarker.vue';
import LiveUpdates from './Summary/LiveUpdates/LiveUpdates.vue';
import LoadingSpinner from "@/components/LoadingSpinner/LoadingSpinner.vue";

const props = defineProps({
  modelValue: {
    type: Object as () => boxAndData,
    required: true,
  },
  userIds: {
    type: Array,
    required: true,
  },
  updates: {
    type: Object,
    required: true,
  },
  warnings: {
    type: Array as PropType<{ Title: string; Location: string; Severity: string; Summary: string }[]>,
    required: true,
  },
  editMode: {
    type: Boolean,
    required: true
  },
  isLoading: Boolean,

});
const emit = defineEmits(["update:modelValue", "newBox","colourChange", "removeBox"]);

const presetStore = usePresetStore();
const presetData = computed(() => Object.values(presetStore.presetData));
const colourPickerVisible = ref<string | null>(null);
const selectedColour = ref({});
const isExpanded = ref(false);
const bottomTabHeight = ref(0);

const toggleDashboard = () => {
  isExpanded.value = !isExpanded.value;
};


function updateLabel(key: string, newLabel: string) {
  const updatedData = { ...props.modelValue };

  if (updatedData[key]) {
    updatedData[key] = {
      ...updatedData[key],
      label: newLabel,
    };
  }

  emit("update:modelValue", updatedData);
}

function getTextColour(colour: string | undefined): string {
  if (typeof colour !== 'string') {
    return "black";
  }
  const c = colour ?? "#FFFFFF";
  const hex = c.replace("#", "");
  const r = parseInt(hex.slice(0, 2), 16);
  const g = parseInt(hex.slice(2, 4), 16);
  const b = parseInt(hex.slice(4, 6), 16);
  const brightness = (r * 299 + g * 587 + b * 114) / 1000;
  return brightness < 128 ? "white" : "black";
}

const getUpdatesForArea = (areaKey) => {
  // Filter updates to only include users in this specific area
  const filteredUpdates: Record<number, { logged_at: string; roomID: number }[]> = {};

  Object.entries(props.updates).forEach(([userId, userUpdates]) => {
    const relevantUpdates = userUpdates.filter(update => update.roomID === areaKey);
    filteredUpdates[Number(userId)] = relevantUpdates;
    
  });

  return filteredUpdates;
};

const warningsByArea = computed(() => {
  return presetData.value[0].reduce((acc, area) => {
    acc[area.label] = props.warnings.filter(warning => warning.Location === area.roomID);
    return acc;
  }, {} as Record<string, { Title: string; Location: string; Severity: string; Summary: string }[]>);
});

const onWarningButtonClick = (areaLabel: string) => {
  const warningsForArea = warningsByArea.value[areaLabel] || [];
  handleWarningButtonPressed(areaLabel, warningsForArea);
};

function showColourPicker(key: string, colour: string) {
  selectedColour.value = { hex: colour };
  colourPickerVisible.value = key;
}

function hideColourPicker() {
  colourPickerVisible.value = null;
}

function changeColour(key: string) {
  const colour = typeof selectedColour.value.hex === 'string' ? selectedColour.value.hex : '#FFFFFF';
  emit('colourChange', key, colour);
  hideColourPicker();
}

// Object Trackers (picoType: 2)
const getObjectTrackers = (area) => {
  return Object.entries(sensorMapping.value)
    .filter(([_, sensor]) => sensor.type === 2) // Only Object Trackers
    .map(([key, sensor]) => ({
      key,
      name: sensor.name,
      icon: sensor.icon,
      count: area?.tracker?.[key]?.count ?? "--" // Default to 0 if missing
    }));
};

// Environment Sensors (picoType: 1)
const getEnvironmentSensors = (area) => {
  return Object.entries(sensorMapping.value)
    .filter(([_, sensor]) => sensor.type === 1) // Only Environment Sensors
    .map(([key, sensor]) => ({
      key,
      name: sensor.name,
      icon: sensor.icon,
      value: area.tracker?.environment?.[key] ?? '--' // Default to "N/A" if missing
    }));
};

const formatSensorName = (name: string): string => {
  return name.replace(/\s*Sensor\s*/i, '').trim();
};

onMounted(() => {
  updateTabHeight('.tab-bar', bottomTabHeight);
  window.addEventListener('resize', updateTabHeight);
});

// Cleanup event listener
onUnmounted(() => {
  window.removeEventListener('resize', () => updateTabHeight('.tab-bar', bottomTabHeight));
});
</script>

<template>
  <div
    class="dashboard"
    :class="{ expanded: isExpanded }"
    :style="{
      maxHeight: `calc(100vh - ${bottomTabHeight + 65}px)`,
      minHeight: `calc(100vh - ${bottomTabHeight + 65}px)`
    }"
  >
    <LoadingSpinner v-if="isLoading" message="Loading dashboard..." />
    <div v-else>
      <!-- Dashboard Header -->
    <div class="dashboard-header">
      <h2 v-if="!isExpanded">Dashboard</h2>
      <h2 v-else>Detailed Dashboard</h2>

      <button class="expand-btn" @click="toggleDashboard">
        <font-awesome-icon :icon="isExpanded ? faCompress : faExpand" />
      </button>
    </div>

    <!-- Show "No data available" if empty -->
    <div v-if="!modelValue || Object.keys(modelValue).length === 0">
      No data available
    </div>

    <!-- Render each item -->
    <div class="dashboard-areas">
      <div
        v-for="([key, data]) in Object.entries(modelValue)"
        :key="key"
        class="dashboard-area"
        :style="{ backgroundColor: data.box?.colour ?? 'var(--primary-light-text)', color: getTextColour(data.box?.colour) }"
      >
        <!-- Colour Picker Popover -->
        <div v-if="colourPickerVisible === key" class="colour-picker-popover">
          <Sketch v-model="selectedColour" />
          <button class="btn btn-success me-2 mt-2 btn-sm" @click="changeColour(key)">Done</button>
          <button class="btn btn-secondary mt-2 btn-sm" @click="hideColourPicker">Cancel</button>
        </div>

        <!-- Update only the label -->
        <div class="area-header">
          <input
            v-if="editMode"
            type="text"
            :value="data.label"
            :placeholder="data.label || key"
            class="input-group-text text-start"
            style="width: 80%;"
            @input="(evt) => updateLabel(key, evt.target.value)"
          />

          <div
            v-else
            class="input-group-text text-start border-0"
            style="width: 80%;"
          >
            {{ data.label || key }}
          </div>

          <template v-if="editMode">
            <button class="btn btn-success add-button" @click="emit('newBox', key)" v-if="!data.box">+</button>
            <button class="btn btn-danger add-button" @click="emit('removeBox', key)" v-else-if="data.box && !data.tracker">-</button>
            <button
              title="Change box colour"
              class="btn add-button d-flex align-items-center justify-content-center"
              style="max-width: 2.5rem; background-color: var(--primary-bg);"
              @click="showColourPicker(key, data.box.colour)"
              v-else
            >
              <img src="@/assets/cog.svg" alt="" style="max-width: 1.5rem;">
            </button>
          </template>
          <button
            v-if="warningsByArea[key]?.length && !editMode"
            class="warning-btn"
            @click="onWarningButtonClick(key)"
          >
            <font-awesome-icon :icon="faExclamationTriangle" />
          </button>
        </div>

        <div class="object-grid">
          <div v-for="tracker in getObjectTrackers(area)" :key="tracker.key" class="pico-data">
            <span class="pico-data-icon">
              <FontAwesomeIcon :icon="tracker.icon" />
            </span> 
            <span class="pico-data-value">
              {{ tracker.name }}: {{ tracker.count }}
            </span>
          </div>
        </div>

        <!-- Environment Sensors -->
        <div v-if="isExpanded" class="environment-grid">
          <div v-for="sensor in getEnvironmentSensors(data)" :key="sensor.key" class="pico-data">
            <span class="pico-data-icon">
              <FontAwesomeIcon :icon="sensor.icon" />
            </span> 
            <span class="pico-data-value">
              {{ formatSensorName(sensor.name) }}: {{ sensor.value }}
            </span>
          </div>
        </div>

        <!-- Live Updates for Each Area (Expanded View Only)
        <div v-if="isExpanded" class="live-updates-section">
          <LiveUpdates 
            :userIds="userIds" 
            :areaKey="key"
            :dataLabel="data.label"
            :updates="getUpdatesForArea(key)" 
            :fullUpdates="updates"
          />
        </div>
        -->
      </div>
    </div>
    </div>
  </div>
</template>

<style scoped>
/* Default Dashboard */
.dashboard {
  display: flex;
  flex-direction: column;
  padding: 0 20px;
  background-color: var(--primary-light-bg);
  border-left: 1px solid #ccc;
  overflow-y: auto;
  transition: all 0.8s ease-in-out;
  position: relative;
  flex: 0.2;
}

.dashboard-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  padding: 20px 0;
  position: sticky;
  top: 0;
  background: var(--primary-light-bg);
  z-index: 888;
}

.expand-btn {
  background-color: var(--primary-dark-bg);
  color: var(--primary-light-text);
  border: none;
  padding: 8px 12px;
  font-size: 18px;
  cursor: pointer;
  border-radius: 5px;
}

.expand-btn:hover {
  background-color: var(--primary-dark-bg-hover);
}

.dashboard h2 {
  color: var(--primary-dark-text);
}

/* Expanded Dashboard */
.dashboard.expanded {
  flex: 5;
  background-color: var(--primary-light-text);
  z-index: 888;
}

/* Compact Dashboard Layout */
.dashboard-areas {
  display: flex;
  flex-direction: column;
}

/* Expanded Layout - Two Areas Per Row */
.dashboard.expanded .dashboard-areas {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

@media (max-width: 600px) {
  .dashboard.expanded .dashboard-areas {
    grid-template-columns: repeat(1, 1fr);
  }
}

/* Dashboard Area Box */
.dashboard-area {
  margin-bottom: 20px;
  padding: 10px;
  border-radius: 8px;
  background-color: var(--primary-light-bg);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
}

.area-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.area-header h3{
  margin: 0;
  font-size: 18px;
  font-weight: bold;
  text-decoration: underline;
}

.warning-btn {
  background: var(--warning-bg);
  color: var(--primary-light-text);
  border: none;
  padding: 5px 8px;
  margin: 0 5px;
  border-radius: 5px;
  cursor: pointer;
  animation: bounce 0.5s infinite alternate ease-in-out;
}

.warning-btn:hover {
  background: var(--warning-bg-hover);
}

/* Live Updates inside Each Area */
.live-updates-section {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #ccc;
}

@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-5px);
  }
}

.colour-picker-popover {
  position: absolute;
  top: 40px;
  right: 10px;
  z-index: 5000;
  background: var(--primary-light-bg);
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.pico-data {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  gap: 20px;
}
.pico-data-icon{
  width: 10%;
}
.pico-data-value{
  width: 100%;
  text-align: left;
}
.environment-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  width: 100%;
  margin: 10px 0;
}
.object-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  width: 100%;
}
.expanded .object-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  width: 100%;
  border-bottom: 0.5px solid #ccc;
}

</style>
