<template>
  <div>
    <h3>Theme</h3>
    <div class="mb-2">
      <label>Primary Dark Background:</label>
      <input type="color" v-model="themeModel.primaryDarkBg" />
    </div>
    <div class="mb-2">
      <label>Primary Dark Text:</label>
      <input type="color" v-model="themeModel.primaryDarkText" />
    </div>
    <div class="mb-2">
      <label>Primary Secondary Background:</label>
      <input type="color" v-model="themeModel.primarySecondaryBg" />
    </div>
    <div class="mb-2">
      <label>Primary Secondary Text:</label>
      <input type="color" v-model="themeModel.primarySecondaryText" />
    </div>
    <div class="mb-2">
      <label>Primary Light Background:</label>
      <input type="color" v-model="themeModel.primaryLightBg" />
    </div>
    <div class="mb-2">
      <label>Primary Light Text:</label>
      <input type="color" v-model="themeModel.primaryLightText" />
    </div>
    <div class="mb-2">
      <label>Accent:</label>
      <input type="color" v-model="themeModel.accent" />
    </div>
    <div class="mb-2">
      <label>Accent Hover:</label>
      <input type="color" v-model="themeModel.accentHover" />
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

// Use computed getter/setter
const themeModel = computed({
  get() {
    return props.theme;
  },
  set(newValue) {
    emit('update:theme', newValue);
  }
});
</script>
