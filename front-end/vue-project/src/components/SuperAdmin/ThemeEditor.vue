<template>
  <div class="theme-editor">
    <h3 class="theme-title">Theme Settings</h3>
    <div class="theme-grid">
      <div class="theme-field" v-for="(value, key) in themeModel" :key="key">
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
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  theme: {
    type: Object,
    default: () => ({})
  }
});
const emit = defineEmits(['update:theme']);

// Computed model for two-way binding
const themeModel = computed({
  get() {
    return props.theme;
  },
  set(newValue) {
    emit('update:theme', newValue);
  }
});

// Format property keys into human-readable labels
function formatLabel(key: string): string {
  return key.replace(/([A-Z])/g, ' $1').replace(/^./, (str) => str.toUpperCase());
}

// Convert CSS color names (e.g., "white", "lightgray") into hex values
function getHex(color: string): string {
  const tempElem = document.createElement('div');
  tempElem.style.color = color;
  document.body.appendChild(tempElem);
  const computedColor = getComputedStyle(tempElem).color;
  document.body.removeChild(tempElem);

  const match = computedColor.match(/\d+/g);
  if (!match) return color; // If not a valid color, return as is

  const [r, g, b] = match.map(Number);
  return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase()}`;
}

// Update color picker when text input loses focus (on blur)
function updateHex(key: string) {
  if (!/^#[0-9A-F]{6}$/i.test(themeModel.value[key])) {
    themeModel.value[key] = getHex(themeModel.value[key]); // Convert only when input is done
  }
}

// Update text input when color picker changes
function updateColor(event: Event, key: string) {
  const target = event.target as HTMLInputElement;
  themeModel.value[key] = target.value;
}
</script>

<style scoped>
.theme-editor {
  padding: 1rem;
  background: var(--home-primary-light-bg);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.theme-title {
  font-size: 1.8rem;
  font-weight: bold;
  margin-bottom: 1rem;
  color: var(--home-primary-dark-text);
}

.theme-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.theme-field {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--home-primary-light-bg);
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

.theme-field label {
  font-weight: bold;
  color: var(--home-primary-dark-text);
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
