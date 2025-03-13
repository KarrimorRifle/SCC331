<template>
  <div class="how-it-works">
    <!--<h2>How It Works</h2> -->
    <div class="steps">
      <!-- Each Step Card -->
      <div v-for="(step, index) in stepsModel" :key="index" class="step-card">
        <!-- Remove Step Button (top-right) -->
        <button class="remove-step-btn" @click="removeStep(index)">
          <FontAwesomeIcon :icon="faTimes" />
        </button>

        <!-- Step Number -->
        <span class="step-number">{{ step.step }}</span>

        <!-- Editable Title -->
        <input
          type="text"
          v-model="step.title"
          class="step-title"
          placeholder="Step Title"
        />

        <!-- Editable Description -->
        <textarea
          v-model="step.description"
          class="step-description"
          placeholder="Step Description"
        ></textarea>
      </div>

      <!-- Add Step Card -->
      <div class="step-card add-step-card" @click="addStep">
        <span>
          <FontAwesomeIcon :icon="faPlus" class="add-icon" />
        </span>
        <p>Add Step</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faPlus, faTimes } from '@fortawesome/free-solid-svg-icons';

const props = defineProps({
  steps: {
    type: Array,
    default: () => []
  }
});
const emit = defineEmits(['update:steps']);

// Computed getter/setter for two-way binding
const stepsModel = computed({
  get() {
    return props.steps;
  },
  set(newValue) {
    emit('update:steps', newValue);
  }
});

function addStep() {
  stepsModel.value = [
    ...stepsModel.value,
    { step: stepsModel.value.length + 1, title: '', description: '' }
  ];
}

function removeStep(index: number) {
  const newSteps = [...stepsModel.value];
  newSteps.splice(index, 1);
  // Re-number steps
  newSteps.forEach((s, i) => (s.step = i + 1));
  stepsModel.value = newSteps;
}
</script>


<style scoped>
.how-it-works {
  text-align: center;
  color: var(--home-primary-light-text);
  background: var(--home-primary-dark-bg);
  padding: 2rem 0;
}

.how-it-works h2 {
  font-size: 2.5rem;
  margin-bottom: 2.5rem;
}

.steps {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 2rem;
}

/* Step Card */
.step-card {
  position: relative;
  background: var(--home-primary-light-bg);
  color: var(--home-primary-dark-text);
  padding: 2rem;
  border-radius: 12px;
  width: 250px;
  text-align: center;
  font-weight: bold;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0px 6px 16px rgba(0, 0, 0, 0.15);
}

/* Step Number Circle */
.step-number {
  position: absolute;
  top: -18px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--home-active);
  color: var(--home-primary-light-text);
  width: 45px;
  height: 45px;
  line-height: 45px;
  border-radius: 50%;
  font-size: 1.4rem;
  font-weight: bold;
  text-align: center;
  box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1);
}

/* Editable Fields */
.step-title {
  font-size: 1.6rem;
  font-weight: bold;
  text-align: center;
  width: 100%;
  border: none;
  background: transparent;
  color: var(--home-primary-dark-text);
  outline: none;
  margin-top: 40px; /* push below the step number circle */
}

.step-description {
  font-size: 1rem;
  text-align: center;
  width: 100%;
  background: transparent;
  border: none;
  color: var(--home-primary-dark-text);
  outline: none;
  resize: none;
  height: 60px;
  margin-top: 10px;
}

/* Remove Step Button (top-right) */
.remove-step-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  background: var(--warning-bg);
  color: white;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s ease-in-out;
}

.remove-step-btn:hover {
  background: var(--warning-bg-hover);
}

/* Add Step Card */
.add-step-card {
  background: var(--primary-light-bg);
  border: 2px dashed var(--home-primary-dark-text);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.add-icon {
  font-size: 3rem;
  color: var(--home-primary-dark-text);
}

.add-step-card:hover {
  background: var(--primary-light-bg-hover);
}

</style>