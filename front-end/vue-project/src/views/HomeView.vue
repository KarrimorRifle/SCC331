<template>
  <div :style="themeStyles">
    <!-- Hero Section -->
    <header class="hero">
      <div class="overlay"></div>
      <div class="hero-content-container">
        <div class="hero-content">
          <h1>
            <!-- Use computed heroIcon to select the correct icon based on domain -->
            <FontAwesomeIcon :icon="heroIcon" class="icon" />
            {{ configTexts.heroTitle }}
          </h1>
          <p>{{ configTexts.heroSubtitle }}</p>
          <RouterLink v-if="!loggedIn" to="/login" class="cta-button">
            <FontAwesomeIcon :icon="faSignInAlt" class="btn-icon" />
            {{ configTexts.loginText }}
          </RouterLink>
        </div>
        <div class="hero-image">
          <!-- The image source is set dynamically via the URL provided by the backend -->
          <img :src="configTexts.heroImage" alt="hero image" />
        </div>
      </div>
      <!-- Scroll Indicator -->
      <div class="scroll-indicator" @click="scrollToSection('features')">
        <FontAwesomeIcon :icon="faChevronDown" class="scroll-icon" />
      </div>
    </header>

    <!-- Features Section -->
    <section id="features" class="features">
      <h2>Key Features</h2>
      <div class="feature-cards">
        <div class="feature-card" v-for="(feature, index) in features" :key="index">
          <FontAwesomeIcon :icon="feature.icon" class="feature-icon" />
          <h3>{{ feature.title }}</h3>
          <p>{{ feature.description }}</p>
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section class="how-it-works">
      <h2>How It Works</h2>
      <div class="steps">
        <div class="step" v-for="(step, index) in howItWorks" :key="index">
          <span class="step-number">{{ step.step }}</span>
          <h3>{{ step.title }}</h3>
          <p>{{ step.description }}</p>
        </div>
      </div>
    </section>

    <!-- Message Modal -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <button class="close-btn" @click="closeModal">
          <FontAwesomeIcon :icon="faTimes" />
        </button>
        <h2>New Messages</h2>
        <ul>
          <li v-for="message in messages" :key="message.message_id">
            <strong>{{ message.sender_email }}</strong>: {{ message.left_message }}
            <br />
            <small>{{ new Date(message.time_sent).toLocaleString() }}</small>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faSignInAlt, faChevronDown, faTimes } from '@fortawesome/free-solid-svg-icons';
import { onMounted, computed } from 'vue';
import {
  domainConfig,
  fetchDomainConfig,
  fetchMessages,
  messages,
  showModal,
  getHeroIcon,
  defaultDomainConfig
} from '../constants/HomeConfig';
import { library } from '@fortawesome/fontawesome-svg-core';
import { fas } from '@fortawesome/free-solid-svg-icons';
library.add(fas);


// In this component, use the global domainConfig defined in HomeConfig.ts.
// If a prop is not provided, we use the backend-configured one.
const props = defineProps({
  loggedIn: Boolean,
  // Optionally allow overriding the configuration
  domainConfig: {
    type: Object,
    required: false,
    default: () => defaultDomainConfig
  }
});

// Use the configuration from the backend if available.
const homeConfig = computed(() => {
  // If the backend has updated our global domainConfig, use it;
  // otherwise, fall back to the prop.
  return domainConfig.value || props.domainConfig;
});

const themeStyles = computed(() => ({
  '--home-primary-dark-bg': homeConfig.value.theme.primaryDarkBg,
  '--home-primary-dark-text': homeConfig.value.theme.primaryDarkText,
  '--home-secondary-bg': homeConfig.value.theme.primarySecondaryBg,
  '--home-secondary-text': homeConfig.value.theme.primarySecondaryText,
  '--home-primary-light-bg': homeConfig.value.theme.primaryLightBg,
  '--home-primary-light-text': homeConfig.value.theme.primaryLightText,
  '--home-accent': homeConfig.value.theme.accent,
  '--home-accent-hover': homeConfig.value.theme.accentHover,
}));

const configTexts = computed(() => {
  const imageName = homeConfig.value.config.hero.image.name;
  let base64Data = homeConfig.value.config.hero.image.data;

  if (base64Data) {
    base64Data = base64Data.replace(/\s/g, ''); // Remove extra spaces/newlines
  }

  return {
    heroTitle: homeConfig.value.config.hero.title,
    heroSubtitle: homeConfig.value.config.hero.subtitle,
    loginText: homeConfig.value.config.loginText,
    heroImage: base64Data && imageName.includes('.') 
      ? `data:image/${imageName.split('.').pop()};base64,${base64Data}` 
      : '/newcastle-airport-image.webp', // Fallback image
  };
});

console.log(configTexts.value.heroImage)

const features = computed(() => homeConfig.value.features);
const howItWorks = computed(() => homeConfig.value.howItWorks);

// Computed property to choose the hero icon based on the domain.
const heroIcon = computed(() => getHeroIcon(homeConfig.value.config.domain));


// Smooth scroll function
const scrollToSection = (id: string) => {
  const section = document.getElementById(id);
  if (section) {
    section.scrollIntoView({ behavior: 'smooth' });
  }
};

onMounted(() => {
  // First, fetch the configuration from the backend.
  fetchDomainConfig();
  // Then, fetch messages.
  fetchMessages();
});

const closeModal = () => {
  showModal.value = false;
};
</script>

<style scoped>
.home-page-container {
  height: 100vh;
  overflow-y: scroll;
  scroll-snap-type: y mandatory;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.page-container::-webkit-scrollbar {
  display: none;
}

/* Hero Section */
.hero {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  color: white;
  background: var(--home-primary-dark-bg);
  padding: 2rem;
}

.hero .overlay {
  position: absolute;
  width: 100%;
  height: 100%;
}

.hero-content-container {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.hero-content {
  position: relative;
  z-index: 2;
  max-width: 700px;
}

.hero-image {
  position: relative;
  z-index: 2;
  max-width: 500px;
}

.hero-image img {
  width: 100%;
  height: auto;
  border-radius: 10px;
}

.hero h1 {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 1rem;
  color: var(--home-accent);
}

.hero p {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
}

section {
  height: 100vh !important;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  scroll-snap-align: start;
}

.cta-button {
  display: inline-flex;
  align-items: center;
  padding: 1rem 2.5rem;
  font-size: 1.4rem;
  color: var(--home-primary-light-text);
  background-color: var(--home-accent);
  border-radius: 10px;
  text-decoration: none;
  transition: all 0.3s ease-in-out;
  gap: 10px;
  font-weight: bold;
}

.cta-button:hover {
  background-color: var(--home-accent-hover);
  transform: scale(1.05);
}

/* Scroll Indicator */
.scroll-indicator {
  position: absolute;
  bottom: 100px;
  left: 50%;
  cursor: pointer;
  animation: bounce 2s infinite;
}

.scroll-icon {
  font-size: 2rem;
  color: var(--home-primary-light-text);
  opacity: 0.8;
  transition: opacity 0.3s;
}

.scroll-indicator:hover .scroll-icon {
  opacity: 1;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(10px); }
}

/* Features Section */
.features {
  text-align: center;
  padding: 5rem 2rem;
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
  border-radius: 10px;
  box-shadow: 0px 6px 16px rgba(0, 0, 0, 0.2);
  width: 280px;
  text-align: center;
}

.feature-icon {
  font-size: 2.8rem;
  color: var(--home-primary-dark-text);
  margin-bottom: 10px;
}

/* Message Modal */
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
  max-width: 400px;
  position: relative;
}

.modal-content h2 {
  margin-bottom: 1rem;
}

.modal-content ul {
  list-style-type: none;
  padding: 0;
}

.modal-content li {
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #003865;
}

.close-btn:hover {
  color: red;
}

/* How It Works */
.how-it-works {
  text-align: center;
  padding: 5rem 2rem;
  color: var(--home-primary-light-text);
  background: var(--home-primary-dark-bg);

}

.how-it-works h2 {
  font-size: 2.5rem;
  margin-bottom: 2.5rem;
}

.steps {
  display: flex;
  justify-content: center;
  gap: 2.5rem;
  flex-wrap: wrap;
}

.step {
  background: var(--home-accent);
  color: var(--home-primary-dark-text);
  padding: 2rem;
  border-radius: 10px;
  width: 250px;
  text-align: center;
  position: relative;
  font-weight: bold;
}

.step-number {
  position: absolute;
  top: -15px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--home-primary-light-bg);
  color: var(--home-primary-dark-text);
  width: 40px;
  height: 40px;
  line-height: 40px;
  border-radius: 50%;
  font-size: 1.2rem;
}

@media (max-width: 768px) {
  .hero-image {
    display: none;
  }
}
</style>
