<template>
  <div>
    <h3>How It Works</h3>
    <div v-for="(step, index) in stepsModel" :key="index" class="mb-2">
      <input type="number" v-model.number="step.step" placeholder="Step Number" />
      <input type="text" v-model="step.title" placeholder="Step Title" />
      <input type="text" v-model="step.description" placeholder="Step Description" />
      <button @click="removeStep(index)">Remove</button>
    </div>
    <button @click="addStep">Add Step</button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  steps: {
    type: Array,
    default: () => []
  }
});
const emit = defineEmits(['update:steps']);

// Use computed getter/setter to avoid recursive updates.
const stepsModel = computed({
  get() {
    return props.steps;
  },
  set(newValue) {
    emit('update:steps', newValue);
  }
});

function addStep() {
  const newSteps = [
    ...stepsModel.value,
    { step: stepsModel.value.length + 1, title: '', description: '' }
  ];
  stepsModel.value = newSteps;
}

function removeStep(index: number) {
  const newSteps = [...stepsModel.value];
  newSteps.splice(index, 1);
  // Re-number steps
  newSteps.forEach((s, i) => (s.step = i + 1));
  stepsModel.value = newSteps;
}
</script>
