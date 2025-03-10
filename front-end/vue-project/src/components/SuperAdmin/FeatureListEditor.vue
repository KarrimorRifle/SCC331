<template>
  <div class="features">
    <!--<h2>Key Features</h2>-->
    <div class="feature-cards">
      <div v-for="(feature, index) in featuresModel" :key="index" class="feature-card">
        <button class="remove-feature-btn" @click="removeFeature(index)">
          <FontAwesomeIcon :icon="faTimes" />
        </button>
        <!-- Feature Icon (clickable to change) -->
        <FontAwesomeIcon :icon="getIcon(feature.icon)" class="feature-icon" @click="openIconSelector(index)"/>

        <!-- Editable Title -->
        <input type="text" v-model="feature.title" class="feature-title" placeholder="Feature Title" />

        <!-- Editable Description -->
        <textarea v-model="feature.description" class="feature-description" placeholder="Feature Description"></textarea>
      </div>

      <!-- "Add Feature" styled as a feature card -->
      <div class="feature-card add-feature-card" @click="addFeature">
        <FontAwesomeIcon :icon="faPlus" class="feature-icon add-icon" />
        <p>Add Feature</p>
      </div>
    </div>

    <!-- Icon Selector Modal -->
    <div v-if="selectedFeatureIndex !== null" class="modal-overlay">
      <div class="modal-content">
        <button class="close-btn" @click="closeIconSelector">
          <FontAwesomeIcon :icon="faTimes" />
        </button>
        <IconSelector @iconSelected="updateFeatureIcon" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faPlus, faTimes } from '@fortawesome/free-solid-svg-icons';
import { fas } from '@fortawesome/free-solid-svg-icons';
import IconSelector from './IconSelector.vue';

import {
  domainConfig,
  fetchDomainConfig,
} from '../../constants/HomeConfig';

library.add(fas);

const props = defineProps({
  features: {
    type: Array,
    default: () => []
  }
});
const emit = defineEmits(['update:features']);

const homeConfig = computed(() => {
  return domainConfig.value
});

const featuresModel = computed({
  get() {
    return props.features;
  },
  set(newValue) {
    emit('update:features', newValue);
  }
});

function addFeature() {
  featuresModel.value = [
    ...featuresModel.value,
    { icon: 'question-circle', title: 'New Feature', description: 'Description...' }
  ];
}

function removeFeature(index: number) {
  const newFeatures = [...featuresModel.value];
  newFeatures.splice(index, 1);
  featuresModel.value = newFeatures;
}

function getIcon(iconName: string) {
  if (!iconName) return fas.faQuestionCircle;

  const formattedName = iconName
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join('');

  return fas[`fa${formattedName}`] || fas.faQuestionCircle;
}


// Modal state for icon selection
const selectedFeatureIndex = ref<number | null>(null);
function openIconSelector(index: number) {
  selectedFeatureIndex.value = index;
}
function closeIconSelector() {
  selectedFeatureIndex.value = null;
}
function updateFeatureIcon(iconName: string) {
  if (selectedFeatureIndex.value !== null) {
    featuresModel.value[selectedFeatureIndex.value].icon = iconName;
  }
  closeIconSelector();
}

</script>

<style scoped>
.features {
  text-align: center;
  color: var(--home-primary-dark-text);
  background: var(--home-secondary-bg);
}

.features h2 {
  font-size: 2.5rem;
  margin-bottom: 3rem;
}

.feature-cards {
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.feature-card {
  background: var(--home-primary-light-bg);
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0px 6px 16px rgba(0, 0, 0, 0.15);
  width: 280px;
  text-align: center;
  position: relative;
  transition: transform 0.2s ease-in-out;
  cursor: pointer;
}

.feature-icon {
  font-size: 3rem;
  color: var(--home-primary-dark-text);
  margin-bottom: 10px;
  transition: transform 0.3s ease;
}

.feature-icon:hover{
  transform: scale(1.2);
  translate: (-5px);
}

.feature-title {
  font-size: 1.4rem;
  font-weight: bold;
  text-align: center;
  width: 100%;
  border: 1px solid #ccc;
  background: transparent;
  color: var(--home-primary-dark-text);
  outline: none;
  margin-bottom: 5px;
}

.feature-description {
  font-size: 1rem;
  text-align: center;
  width: 100%;
  background: transparent;
  border: 1px solid #ccc;
  color: var(--home-primary-dark-text);
  outline: none;
  resize: none;
  height: 100px;
}

/* Add Feature Card */
.add-feature-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2px dashed var(--home-primary-dark-text);
  cursor: pointer;
}

.add-icon {
  font-size: 3rem;
  color: var(--home-primary-dark-text);
}

.add-feature-card:hover {
  background: var(--home-primary-light-bg-hover);
}

.remove-feature-btn {
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

.remove-feature-btn:hover {
  background: var(--warning-bg-hover);
}


/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
  text-align: center;
  max-width: 600px;
  width: 90%;
  position: relative;
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--primary-dark-text);
}

.close-btn:hover {
  color: var(--warning-text-hover);
}


</style>
