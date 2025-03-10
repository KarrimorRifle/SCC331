<template>
  <div :style="themeStyles" class="container">
    <div class="super-admin-view-header">
      <h1>Update Configuration</h1>
      <button type="submit" class="update-button" @click="handleSubmit">
        Update Configuration
      </button>
    </div>

    <form @submit.prevent="handleSubmit">
      <!-- Theme Section -->
      <section>
        <ThemeEditor v-model:theme="form.theme" />
      </section>

      <!-- General Config Section -->
      <section class="hero-config-section">
        <div class="hero-content-container">
          <!-- Live Preview (looks like the actual homepage hero) -->
          <header class="hero-preview">
            <div class="overlay"></div>
            <div class="hero-preview-content">
              <h1>
                <!-- Optionally, include an icon if desired -->
                <FontAwesomeIcon :icon="heroIcon" class="icon" />
                {{ form.config.hero.title }}
              </h1>
              <p>{{ form.config.hero.subtitle }}</p>
              <div v-if="form.config.loginText" class="cta-button-preview">
                {{ form.config.loginText }}
              </div>
            </div>
            <div class="hero-preview-image">
              <img :src="imageSrc" alt="hero image" />
            </div>
          </header>

          <!-- Edit Panel for Hero Section -->
          <div class="hero-edit-panel">
            <h2>Edit Hero Section</h2>
            <div class="edit-field">
              <label>Domain:</label>
              <input type="text" v-model="form.config.domain" />
            </div>
            <div class="edit-field">
              <label>Hero Title:</label>
              <input type="text" v-model="form.config.hero.title" />
            </div>
            <div class="edit-field">
              <label>Hero Subtitle:</label>
              <input type="text" v-model="form.config.hero.subtitle" />
            </div>
            <div class="edit-field">
              <label>Login Text:</label>
              <input type="text" v-model="form.config.loginText" />
            </div>
            <div class="edit-field">
              <label>Upload Hero Image:</label>
              <input type="file" @change="handleImageUpload" accept="image/*" />
              <div v-if="form.config.hero.image.name">
                Current file: {{ form.config.hero.image.name }}
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Features Section -->
      <section>
        <FeatureListEditor v-model:features="form.features" />
      </section>

      <!-- How It Works Section -->
      <section>
        <HowItWorksEditor v-model:steps="form.howItWorks" />
      </section>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import FeatureListEditor from '@/components/SuperAdmin/FeatureListEditor.vue';
import HowItWorksEditor from '@/components/SuperAdmin/HowItWorksEditor.vue';
import ThemeEditor from '@/components/SuperAdmin/ThemeEditor.vue';
import {
  getHeroIcon,
} from '../constants/HomeConfig';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { library } from '@fortawesome/fontawesome-svg-core';
import { fas } from '@fortawesome/free-solid-svg-icons';
library.add(fas);


const form = ref({
  config: {
    domain: '',
    loginText: '',
    hero: {
      title: '',
      subtitle: '',
      image: {
        name: '',
        data: ''
      }
    }
  },
  features: [],
  howItWorks: [],
  theme: {
    primaryDarkBg: '',
    primaryDarkText: '',
    primarySecondaryBg: '',
    primarySecondaryText: '',
    primaryLightBg: '',
    primaryLightText: '',
    accent: '',
    accentHover: ''
  }
});

// Fetch current configuration from the backend on mount.
onMounted(async () => {
  try {
    const response = await axios.get('http://localhost:5010/home', { withCredentials: true });
    if (response.status === 200 && response.data) {
      form.value = response.data;
    }
  } catch (error) {
    console.error('Error fetching configuration:', error);
  }
});

const heroIcon = computed(() => getHeroIcon(form.value.config.domain));

// Compute imageSrc for the hero image preview.
const imageSrc = computed(() => {
  const imageName = form.value.config.hero.image.name;
  let base64 = form.value.config.hero.image.data;
  if (base64) {
    base64 = base64.replace(/\s/g, ''); // Remove extra spaces/newlines
  }
  if (base64 && imageName && imageName.includes('.')) {
    const imageType = imageName.split('.').pop();
    return `data:image/${imageType};base64,${base64}`;
  }
  return '/newcastle-airport-image.webp';
});

// Handle image upload event.
function handleImageUpload(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length) {
    const file = target.files[0];
    form.value.config.hero.image.name = file.name;
    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      const base64Index = result.indexOf('base64,');
      form.value.config.hero.image.data =
        base64Index !== -1 ? result.substring(base64Index + 7) : result;
      // Force reactivity update if necessary:
      form.value = { ...form.value };
    };
    reader.readAsDataURL(file);
  }
}

// Compute themeStyles so that children can use CSS variables.
const themeStyles = computed(() => ({
  '--home-primary-dark-bg': form.value.theme.primaryDarkBg,
  '--home-primary-dark-text': form.value.theme.primaryDarkText,
  '--home-secondary-bg': form.value.theme.primarySecondaryBg,
  '--home-secondary-text': form.value.theme.primarySecondaryText,
  '--home-primary-light-bg': form.value.theme.primaryLightBg,
  '--home-primary-light-text': form.value.theme.primaryLightText,
  '--home-accent': form.value.theme.accent,
  '--home-accent-hover': form.value.theme.accentHover
}));

// Submit updated configuration to backend.
const handleSubmit = async () => {
  try {
    const response = await axios.patch('http://localhost:5011/home', form.value, { withCredentials: true });
    if (response.status === 200) {
      alert('Configuration updated successfully.');
    }
  } catch (error) {
    alert('Error updating configuration.');
    console.error('Update error:', error);
  }
};
</script>

<style scoped>
.container {
  margin: 0;
  min-width: 100%;
  background: var(--primary-light-bg);
  overflow-y: auto;
}

.super-admin-view-header {
    position: sticky;
    top: 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--primary-light-bg);
    color: var(--primary-dark-text);
    padding: 1rem 2rem;
    z-index: 200;
}


.update-button {
  background: var(--positive);
  color: var(--primary-light-text);
  border: none;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: bold;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s ease-in-out;
}


/* Hero-like Section */
.hero-config-section {
  margin-bottom: 2rem;
  padding: 1rem;
}

.hero-content-container {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  gap: 2rem;
}

/* Hero Preview (replicates the live homepage hero) */
.hero-preview {
  position: relative;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  background: var(--home-primary-dark-bg);
  padding: 2rem;
  border-radius: 10px;
}

.hero-preview-content {
  position: relative;
  z-index: 2;
  max-width: 600px;
  text-align: left;
}
.hero-preview-content h1 {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: var(--home-accent);
}
.hero-preview-content p {
  font-size: 0.75rem;
  margin-bottom: 0.75rem;
}
.cta-button-preview {
  display: inline-block;
  padding: 0.75rem 2rem;
  font-size: 1.2rem;
  background-color: var(--home-accent-hover);
  border-radius: 10px;
  text-align: center;
  font-weight: bold;
  margin-top: 1rem;
}

/* Hero Image Preview */
.hero-preview-image {
  position: relative;
  z-index: 2;
  max-width: 400px; min-width: 400px;
}
.hero-preview-image img {
  width: 100%;
  height: auto;
  border-radius: 10px;
  box-shadow: 0px 6px 16px rgba(0, 0, 0, 0.2);
}

/* Edit Panel for Hero Section */
.hero-edit-panel {
  margin-top: 2rem;
  background: var(--primary-light-bg);
  padding: 1rem;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.hero-edit-panel h2 {
  margin-bottom: 1rem;
  color: var(--primary-dark-text);
}
.edit-field {
  margin-bottom: 1rem;
  color: var(--primary-dark-text);
}
.edit-field label {
  display: block;
  font-weight: bold;
  margin-bottom: 0.25rem;
  color: var(--primary-dark-text);
}
.edit-field input[type="text"],
.edit-field input[type="file"],
.edit-field textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  color: var(--primary-dark-text);
  border-radius: 5px;
}

/* Other sections */
section {
  margin-bottom: 2rem;
  padding: 1rem;
}

button {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
}
@media (max-width: 768px) {
    .hero-content-container {
        flex-direction: column;
    } 
    .hero-preview-image{
        display: none;
    }
}
</style>
