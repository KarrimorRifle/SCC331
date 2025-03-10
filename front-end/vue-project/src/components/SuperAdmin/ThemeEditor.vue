<template>
  <div class="theme-editor">
    <div v-for="(keys, groupName) in groups" :key="groupName" class="theme-group">
      <!-- Group header is clickable to toggle collapse -->
      <div class="group-header" @click="toggleGroup(groupName)">
        <h4 class="group-title">{{ groupName }}</h4>
        <span class="collapse-indicator">{{ collapsed[groupName] ? '+' : '−' }}</span>
      </div>
      <div v-if="!collapsed[groupName]" class="theme-grid">
        <div class="theme-field" v-for="key in keys" :key="key">
          <div class="theme-label">
            <label>{{ formatLabel(key) }}</label>
            <input
              type="text"
              v-model="themeModel[key]"
              @blur="updateHex(key)"
              class="hex-input"
            />
          </div>
          <input
            type="color"
            :value="getHex(themeModel[key])"
            @input="updateColor($event, key)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  theme: {
    type: Object,
    default: () => ({})
  }
});
const emit = defineEmits(['update:theme']);

// Two-way binding for the theme object.
const themeModel = computed({
  get() {
    return props.theme;
  },
  set(newValue) {
    emit('update:theme', newValue);
  }
});

// Define theme groups. Note that we've split "Primary Colors" into three groups.
const groups = {
  "Active Colors": ["active", "active_bg", "active_text"],
  "Negative Colors": ["negative", "negative_bg", "negative_text"],
  "Not Active Colors": ["not_active", "not_active_bg", "not_active_text"],
  "Notification Colors": ["notification_bg", "notification_bg_hover", "notification_text", "notification_text_hover"],
  "Positive Colors": ["positive"],
  "Primary Base": ["primary_bg", "primary_bg_hover", "primary_text"],
  "Primary Dark": ["primary_dark_bg", "primary_dark_bg_hover", "primary_dark_text", "primary_dark_text_hover"],
  "Primary Light": ["primary_light_bg", "primary_light_bg_hover", "primary_light_text", "primary_light_text_hover"],
  "Warning Colors": ["warning_bg", "warning_bg_hover", "warning_text", "warning_text_hover"]
};

// Create a reactive object for collapsed state for each group.
const collapsed = ref({});
Object.keys(groups).forEach(group => {
  collapsed.value[group] = false;
});

// Toggle collapse state for a given group.
function toggleGroup(group: string) {
  collapsed.value[group] = !collapsed.value[group];
}

// Format keys (e.g., "primary_dark_bg") to human-readable labels.
function formatLabel(key: string): string {
  // Replace underscores with spaces and capitalize the first letter of each word.
  return key
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

// Convert a CSS color (name or rgb string) to a hex value.
function getHex(color: string): string {
  const tempElem = document.createElement('div');
  tempElem.style.color = color;
  document.body.appendChild(tempElem);
  const computedColor = getComputedStyle(tempElem).color;
  document.body.removeChild(tempElem);

  const match = computedColor.match(/\d+/g);
  if (!match) return color; // Return the original string if no match
  const [r, g, b] = match.map(Number);
  return `#${((1 << 24) + (r << 16) + (g << 8) + b)
    .toString(16)
    .slice(1)
    .toUpperCase()}`;
}

// Update hex value when the text input loses focus.
function updateHex(key: string) {
  if (!/^#[0-9A-F]{6}$/i.test(themeModel.value[key])) {
    themeModel.value[key] = getHex(themeModel.value[key]);
  }
}

// Update the text input when the color picker changes.
function updateColor(event: Event, key: string) {
  const target = event.target as HTMLInputElement;
  themeModel.value[key] = target.value;
}
</script>

<style scoped>
.theme-editor {
  padding: 1rem;
  background: var(--primary-light-bg);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.theme-title {
  font-size: 1.8rem;
  font-weight: bold;
  margin-bottom: 1rem;
  color: var(--primary-dark-text);
}

.theme-group {
  margin-bottom: 1.5rem;
  border: 1px solid #eee;
  border-radius: 5px;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--primary-light-bg);
  padding: 0.75rem;
  cursor: pointer;
  border-bottom: 1px solid #ddd;
}

.group-title {
  font-size: 1.4rem;
  font-weight: bold;
  margin: 0;
  color: var(--primary-dark-text);
}

.collapse-indicator {
  font-size: 1.4rem;
  font-weight: bold;
  color: var(--primary-dark-text);
}

.theme-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);  gap: 1rem;
  padding: 0.75rem;
}

.theme-field {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--primary-light-bg);
  padding: 0.75rem;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.theme-label {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  flex: 1;
}

.theme-label label {
  font-weight: bold;
  color: var(--primary-dark-text);
}

.hex-input {
  width: 80px;
  border: 1px solid #ccc;
  padding: 3px;
  border-radius: 3px;
  text-align: center;
  font-size: 0.9rem;
}

.theme-field input[type="color"] {
  width: 50px;
  height: 50px;
  border: none;
  padding: 0;
  background: none;
  cursor: pointer;
}
</style>
