<template>
  <div>
    <h3>Features</h3>
    <div v-for="(feature, index) in featuresModel" :key="index" class="mb-2">
      <input type="text" v-model="feature.icon" placeholder="Icon (e.g. shield)" />
      <input type="text" v-model="feature.title" placeholder="Feature Title" />
      <input type="text" v-model="feature.description" placeholder="Feature Description" />
      <button @click="removeFeature(index)">Remove</button>
    </div>
    <button @click="addFeature">Add Feature</button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps({
  features: {
    type: Array,
    default: () => []
  }
});
const emit = defineEmits(['update:features']);

// Use a computed getter/setter to bind the parent's value without extra watchers.
const featuresModel = computed({
  get() {
    return props.features;
  },
  set(newValue) {
    emit('update:features', newValue);
  }
});

function addFeature() {
  // Create a new array with the added feature
  featuresModel.value = [
    ...featuresModel.value,
    { icon: '', title: '', description: '' }
  ];
}

function removeFeature(index: number) {
  const newFeatures = featuresModel.value.slice();
  newFeatures.splice(index, 1);
  featuresModel.value = newFeatures;
}
</script>
