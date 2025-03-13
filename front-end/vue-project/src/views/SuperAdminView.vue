<template>
  <div :style="themeStyles" class="container">
    <div class="super-admin-view-header">
      <h1>Update Configuration</h1>
      <button type="submit" class="btn-success btn fw-bold" @click="handleSubmit">
        Update
      </button>
    </div>

    <form @submit.prevent="handleSubmit">
      <!-- Theme Section -->


      <section class="rounded border mb-3">
        <div class="section-header" @click="toggleSection('theme')">
          <h2>Theme Settings</h2>
          <span class="toggle-icon">
            <font-awesome-icon v-if="collapsed.theme" :icon="faChevronDown"/>
            <font-awesome-icon v-else :icon="faChevronUp"/>
          </span>
        </div>
        <ThemeEditor v-model:theme="form.theme" v-if="!collapsed.theme"/>
      </section>

      <!-- General Config Section -->
      <section class="hero-config-section rounded border mb-3">
        <div class="section-header" @click="toggleSection('heroConfig')">
          <h2>Landing Page (Hero) Settings</h2>
          <span class="toggle-icon" >
            <font-awesome-icon v-if="collapsed.heroConfig" :icon="faChevronDown"/>
            <font-awesome-icon v-else :icon="faChevronUp"/>
          </span>
        </div>
        <div class="hero-content-container" v-if="!collapsed.heroConfig">
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
              <img :src="homeImage" alt="hero image" />
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
              <input type="file" @change="handleImageUpload"/>
              <div v-if="form.config.hero.image.name">
                Current file: {{ form.config.hero.image.name }}
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Features Section -->
      <section class=" rounded border mb-3">
        <div class="section-header" @click="toggleSection('features')">
          <h2>Features Settings</h2>
          <span class="toggle-icon">
            <font-awesome-icon v-if="collapsed.features" :icon="faChevronDown"/>
            <font-awesome-icon v-else :icon="faChevronUp"/>
          </span>
        </div>
        <FeatureListEditor v-model:features="form.features" v-if="!collapsed.features"/>
      </section>

      <!-- How It Works Section -->
      <section class="rounded border mb-3">
        <div class="section-header" @click="toggleSection('howItWorks')">
          <h2>How It Works Settings</h2>
          <span class="toggle-icon">
            <font-awesome-icon v-if="collapsed.howItWorks" :icon="faChevronDown"/>
            <font-awesome-icon v-else :icon="faChevronUp"/>
          </span>
        </div>
        <HowItWorksEditor v-model:steps="form.howItWorks" v-if="!collapsed.howItWorks"/>
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
import { fas, faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons';
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
    active: '',
    active_bg: '',
    active_text: '',

    negative: '',
    negative_bg: '',
    negative_text: '',

    not_active: '',
    not_active_bg: '',
    not_active_text: '',

    notification_bg: '',
    notification_bg_hover: '',
    notification_text: '',
    notification_text_hover: '',

    positive: '',

    primary_bg: '',
    primary_bg_hover: '',

    primary_dark_bg: '',
    primary_dark_bg_hover: '',
    primary_dark_text: '',
    primary_dark_text_hover: '',

    primary_light_bg: '',
    primary_light_bg_hover: '',
    primary_light_text: '',
    primary_light_text_hover: '',

    primary_text: '',

    warning_bg: '',
    warning_bg_hover: '',
    warning_text: '',
    warning_text_hover: ''
    }

});

const collapsed = ref({
  theme: false,
  heroConfig: false,
  features: false,
  howItWorks: false
});

let homeImage = ref<string>("");
// Fetch current configuration from the backend on mount.
onMounted(async () => {
  try {
    const response = await axios.get('/api/assets-reader/home', { withCredentials: true });
    if (response.status === 200 && response.data) {
      form.value = response.data;
      processHomeImage();
    }
  } catch (error) {
    console.error('Error fetching configuration:', error);
  }
});

const heroIcon = computed(() => getHeroIcon(form.value.config.domain));

const processHomeImage = () => {
  if (form.value.config.hero.image.data && form.value.config.hero.image.name) {
    const imageType = form.value.config.hero.image.name.split('.').pop();
    homeImage.value = `data:image/${imageType};base64,${atob(form.value.config.hero.image.data) }`;
  } else {
    homeImage.value = "";
  }
};

// Handle image upload event.
function handleImageUpload(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length) {
    const file = target.files[0];
    form.value.config.hero.image.name = file.name;
    const reader = new FileReader();

    reader.onload = (e) => {
      const result = e.target?.result as string;
      // Extract base64 content
      const base64Data = result.split(',')[1];
      form.value.config.hero.image.data = base64Data;

      // Get file extension for MIME type
      const imageType = file.name.split('.').pop();

      // Update homeImage immediately for preview
      homeImage.value = `data:image/${imageType};base64,${base64Data}`;

      // Force reactivity update if necessary
      form.value = { ...form.value };

      console.log("Base64 Data Updated:", form.value.config.hero.image.data);
      console.log("Preview Updated:", homeImage.value);
    };

    reader.readAsDataURL(file);
  }
}

function toggleSection(sectionName: string) {
  collapsed.value[sectionName] = !collapsed.value[sectionName];
}

// Compute themeStyles so that children can use CSS variables.
const themeStyles = computed(() => ({
  '--home-active': form.value.theme.active,
  '--home-active-bg': form.value.theme.active_bg,
  '--home-active-text': form.value.theme.active_text,

  '--home-negative': form.value.theme.negative,
  '--home-negative-bg': form.value.theme.negative_bg,
  '--home-negative-text': form.value.theme.negative_text,

  '--home-not-active': form.value.theme.not_active,
  '--home-not-active-bg': form.value.theme.not_active_bg,
  '--home-not-active-text': form.value.theme.not_active_text,

  '--home-notification-bg': form.value.theme.notification_bg,
  '--home-notification-bg-hover': form.value.theme.notification_bg_hover,
  '--home-notification-text': form.value.theme.notification_text,
  '--home-notification-text-hover': form.value.theme.notification_text_hover,

  '--home-positive': form.value.theme.positive,

  '--home-primary-bg': form.value.theme.primary_bg,
  '--home-primary-bg-hover': form.value.theme.primary_bg_hover,

  '--home-primary-dark-bg': form.value.theme.primary_dark_bg,
  '--home-primary-dark-bg-hover': form.value.theme.primary_dark_bg_hover,
  '--home-primary-dark-text': form.value.theme.primary_dark_text,
  '--home-primary-dark-text-hover': form.value.theme.primary_dark_text_hover,

  '--home-primary-light-bg': form.value.theme.primary_light_bg,
  '--home-primary-light-bg-hover': form.value.theme.primary_light_bg_hover,
  '--home-primary-light-text': form.value.theme.primary_light_text,
  '--home-primary-light-text-hover': form.value.theme.primary_light_text_hover,

  '--home-primary-text': form.value.theme.primary_text,

  '--home-warning-bg': form.value.theme.warning_bg,
  '--home-warning-bg-hover': form.value.theme.warning_bg_hover,
  '--home-warning-text': form.value.theme.warning_text,
  '--home-warning-text-hover': form.value.theme.warning_text_hover,
}));


// Submit updated configuration to backend.
const handleSubmit = async () => {
  try {
    const response = await axios.patch('/api/editor/home', form.value, { withCredentials: true });
    if (response.status === 200) {
      console.log(form.value);
      alert('Configuration updated successfully.');
      // window.location.reload();
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--primary-light-bg);
  color: var(--primary-dark-text);
  font-weight: bold;
  padding: 0.75rem;
  cursor: pointer;
  margin-bottom: 0.5rem;
  font-size: 1.8rem;
  font-weight: bold;
}
.toggle-icon {
  font-size: 1.4rem;
  font-weight: bold;
  color: var(--primary-dark-text);
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
  color: var(--home-primary-light-text);
}
.hero-preview-content p {
  font-size: 0.75rem;
  margin-bottom: 0.75rem;
  color: var(--home-primary-light-text);
}
.cta-button-preview {
  display: inline-block;
  padding: 0.75rem 2rem;
  font-size: 1.2rem;
  background-color: var(--home-active);
  color: var(--home-primary-light-text);
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
