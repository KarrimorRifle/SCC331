<script setup lang="ts">
import { boxAndData } from '@/utils/mapTypes';
import LuggageMarker from './ObjectMarker/LuggageMarker.vue';
import PersonMarker from './ObjectMarker/PersonMarker.vue';
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  modelValue: {
    type: Object as () => boxAndData,
    required: true,
  }
});

const emit = defineEmits(["update:modelValue"]);

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

function getTextColor(color: string | undefined): string {
  const c = color ?? "#FFFFFF";
  const hex = c.replace("#", "");
  const r = parseInt(hex.slice(0, 2), 16);
  const g = parseInt(hex.slice(2, 4), 16);
  const b = parseInt(hex.slice(4, 6), 16);
  const brightness = (r * 299 + g * 587 + b * 114) / 1000;
  return brightness < 128 ? "white" : "black";
}
</script>

<template>
  <div class="dashboard">
    <!-- Show "No data available" if empty -->
    <div v-if="!modelValue || Object.keys(modelValue).length === 0">
      No data available
    </div>

    <!-- Render each item -->
    <div
      v-for="([key, data]) in Object.entries(modelValue)"
      :key="key"
      class="dashboard-area"
      :style="{ backgroundColor: data.box?.colour ?? '#FFFFFF', color: getTextColor(data.box?.colour) }"
    >
      <button class="btn btn-success add-button">+</button>

      <!-- Update only the label -->
      <input
        type="text"
        :value="data.label"
        :placeholder="data.label || key"
        class="input-group-text text-start"
        style="width: 80%;"
        @input="(evt) => updateLabel(key, evt.target.value)"
      />

      <!-- Luggage Count -->
      <div class="count-container">
        <div class="marker-container">
          <LuggageMarker :color="'#f44336'" :position="{ top: 0, left: 0 }" />
        </div>
        <p>Luggage: {{ data.tracker?.luggage?.count || 0 }}</p>
      </div>
      
      <!-- People Count -->
      <div class="count-container">
        <div class="marker-container">
          <PersonMarker :color="'#4caf50'" :position="{ top: 0, left: 0 }" />
        </div>
        <p>People: {{ data.tracker?.users?.count || 0 }}</p>
      </div>

      <!-- Environment Data -->
      <div class="environment-container">
        <h4>Environment Data:</h4>
        <table style="width: 100%;">
          <tbody>
            <tr>
              <th class="emoji-column">🌡️</th>
              <th class="data-column">{{ data.tracker?.environment?.temperature || '--' }} °C</th>
              <th class="emoji-column">🌬️</th>
              <th class="data-column">{{ data.tracker?.environment?.IAQ || '--' }} %</th>
            </tr>
            <tr>
              <th class="emoji-column">🔊</th>
              <th class="data-column">{{ data.tracker?.environment?.sound || '--' }} dB</th>
              <th class="emoji-column">🌡️</th>
              <th class="data-column">{{ data.tracker?.environment?.pressure || '--' }} hPa</th>
            </tr>
            <tr>
              <th class="emoji-column">💡</th>
              <th class="data-column">{{ data.tracker?.environment?.light || '--' }} lux</th>
              <th class="emoji-column">💧</th>
              <th class="data-column">{{ data.tracker?.environment?.humidity || '--' }} %</th>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  width: 300px;
  padding: 20px;
  background-color: #f8f8ff;
  border-left: 1px solid #ccc;
  max-height: 100%;
  overflow-y: auto;
  color: black;
  font-weight: bold;
}

.dashboard-area {
  margin-bottom: 20px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
}

.dashboard-area h3 {
  margin: 0;
  font-size: 18px;
  font-weight: bold;
  text-decoration: underline;
}

.count-container {
  display: flex;
  align-items: center;
  margin: 5px 0;
}

.marker-container {
  position: relative;
  width: 20px;
  height: 20px;
  margin-right: 8px;
}

.environment-container {
  margin-top: 10px;
  padding: 8px;
  border-radius: 5px;
  background-color: rgba(255, 255, 255, 0.2);
}

.environment-container h4 {
  margin-bottom: 5px;
  font-size: 14px;
  text-decoration: underline;
}

.environment-container p {
  margin: 3px 0;
  font-size: 12px;
}

.emoji-column {
  text-align: center;
}

.data-column {
  width: auto;
}

.add-button {
  position: absolute;
  right: 10px;
  top: 10px;
}
</style>
