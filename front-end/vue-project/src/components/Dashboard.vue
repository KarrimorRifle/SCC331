<script setup lang="ts">
import { boxAndData } from '@/utils/mapTypes';
import LuggageMarker from './ObjectMarker/LuggageMarker.vue';
import PersonMarker from './ObjectMarker/PersonMarker.vue';
import { defineProps, defineEmits, ref } from 'vue';
import { Sketch } from '@ckpack/vue-color';

const props = defineProps({
  modelValue: {
    type: Object as () => boxAndData,
    required: true,
  }
});

const emit = defineEmits(["update:modelValue", "newBox","colourChange", "removeBox"]);

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

const colorPickerVisible = ref<string | null>(null);
const selectedColor = ref<string>('#FFFFFF');

function showColorPicker(key: string) {
  colorPickerVisible.value = key;
}

function hideColorPicker() {
  colorPickerVisible.value = null;
}

function changeColor(key: string) {
  emit('colourChange', key, selectedColor.value );
  hideColorPicker();
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
      <button class="btn btn-success add-button" @click="emit('newBox', key)" v-if="!data.box">+</button>
      <button class="btn btn-danger add-button" @click="emit('removeBox', key)" v-else-if="data.box && !data.tracker">-</button>
      <button
        title="Change box colour"
        class="btn add-button d-flex align-items-center justify-content-center"
        style="max-width: 2.5rem; background-color: #568ea6;"
        @click="showColorPicker(key)"
        v-else
      >
        <img src="@/assets/cog.svg" alt="" style="max-width: 1.5rem;">
      </button>

      <!-- Color Picker Popover -->
      <div v-if="colorPickerVisible === key" class="color-picker-popover">
        <Sketch v-model="selectedColor" />
        <button class="btn btn-success me-2 mt-2 btn-sm" @click="changeColor(key)">Done</button>
        <button class="btn btn-secondary mt-2 btn-sm" @click="hideColorPicker">Cancel</button>
      </div>

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

.color-picker-popover {
  position: absolute;
  top: 40px;
  right: 10px;
  z-index: 1000;
  background: white;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>
