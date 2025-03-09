<template>
  <div class="container">
    <h1>Update Front Page Configuration</h1>
    <form @submit.prevent="handleSubmit">
      <!-- General Config Section -->
      <section>
        <h2>General Config</h2>
        <div class="form-group">
          <label>Domain:</label>
          <input type="text" v-model="form.config.domain" required />
        </div>
        <div class="form-group">
          <label>Login Text:</label>
          <input type="text" v-model="form.config.loginText" required />
        </div>
        <div class="form-group">
          <label>Hero Title:</label>
          <input type="text" v-model="form.config.hero.title" required />
        </div>
        <div class="form-group">
          <label>Hero Subtitle:</label>
          <input type="text" v-model="form.config.hero.subtitle" required />
        </div>
        <div class="form-group">
          <label>Hero Image Name:</label>
          <input type="text" v-model="form.config.hero.image.name" required />
        </div>
        <div class="form-group">
          <label>Hero Image Data (Base64):</label>
          <textarea v-model="form.config.hero.image.data" required></textarea>
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

      <!-- Theme Section -->
      <section>
        <ThemeEditor v-model:theme="form.theme" />
      </section>

      <button type="submit">Update Configuration</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import FeatureListEditor from '@/components/SuperAdmin/FeatureListEditor.vue';
import HowItWorksEditor from '@/components/SuperAdmin/HowItWorksEditor.vue';
import ThemeEditor from '@/components/SuperAdmin/ThemeEditor.vue';

// Our form is initialized with empty values. On mount we fetch the config from the backend
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

// Fetch current configuration from the backend on mount
onMounted(async () => {
  try {
    const response = await axios.get('http://localhost:5010/home', { withCredentials: true });
    if (response.status === 200 && response.data) {
      // Assuming the backend returns a complete object with keys: config, features, howItWorks, theme
      form.value = response.data;
    }
  } catch (error) {
    console.error('Error fetching configuration:', error);
  }
});

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
  max-width: 800px;
  margin: auto;
  padding: 1rem;
}
section {
  margin-bottom: 2rem;
  padding: 1rem;
  border: 1px solid #ccc;
}
.form-group {
  margin-bottom: 1rem;
}
label {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: bold;
}
input,
textarea {
  width: 100%;
  padding: 0.5rem;
  margin-bottom: 0.5rem;
}
button {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
}
</style>
