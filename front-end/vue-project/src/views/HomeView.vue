<script setup lang="ts">
import { RouterLink } from 'vue-router';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faSignInAlt, faPlaneDeparture, faShieldAlt, faMapMarkedAlt, faBell, faClock, faChevronDown } from '@fortawesome/free-solid-svg-icons';

defineProps({
  loggedIn: Boolean,
});

// Smooth scroll function
const scrollToSection = (id: string) => {
  const section = document.getElementById(id);
  if (section) {
    section.scrollIntoView({ behavior: 'smooth' });
  }
};
</script>

<template>
  <div class="home-page-container">
    <!-- Hero Section -->
    <header class="hero">
      <div class="overlay"></div>
      <div class="hero-content-container">
        <div class="hero-content">
          <h1>
            <FontAwesomeIcon :icon="faPlaneDeparture" class="icon" /> Newcastle Airport Monitoring
          </h1>
          <p>Ensuring seamless airport operations with real-time monitoring of security, occupancy, and environmental conditions.</p>
          <RouterLink v-if="!loggedIn" to="/login" class="cta-button">
            <FontAwesomeIcon :icon="faSignInAlt" class="btn-icon" /> Login to Monitor
          </RouterLink>
        </div>

        <div class="hero-image">
          <img src="@/assets/newcastle-airport-image.webp" alt="airport-image">
        </div>
      </div>

      <!-- Scroll Indicator -->
      <div class="scroll-indicator" @click="scrollToSection('features')">
        <FontAwesomeIcon :icon="faChevronDown" class="scroll-icon" />
      </div>
    </header>

    <section id="features" class="features">
      <h2>Key Features</h2>
      <div class="feature-cards">
        <div class="feature-card">
          <FontAwesomeIcon :icon="faShieldAlt" class="feature-icon" />
          <h3>Security Alerts</h3>
          <p>Get notified of any security breaches in real-time.</p>
        </div>
        <div class="feature-card">
          <FontAwesomeIcon :icon="faMapMarkedAlt" class="feature-icon" />
          <h3>Live Airport Map</h3>
          <p>Monitor passenger flow and track luggage locations.</p>
        </div>
        <div class="feature-card">
          <FontAwesomeIcon :icon="faBell" class="feature-icon" />
          <h3>Instant Notifications</h3>
          <p>Receive alerts for emergency and unusual activities.</p>
        </div>
        <div class="feature-card">
          <FontAwesomeIcon :icon="faClock" class="feature-icon" />
          <h3>24/7 Monitoring</h3>
          <p>Track airport conditions anytime, anywhere.</p>
        </div>
      </div>
    </section>

    <section class="how-it-works">
      <h2>How It Works</h2>
      <div class="steps">
        <div class="step">
          <span class="step-number">1</span>
          <h3>Login</h3>
          <p>Access the system securely.</p>
        </div>
        <div class="step">
          <span class="step-number">2</span>
          <h3>Monitor</h3>
          <p>Track security, environmental data, and passenger flow in real-time.</p>
        </div>
        <div class="step">
          <span class="step-number">3</span>
          <h3>Receive Alerts</h3>
          <p>Get instant updates on critical situations.</p>
        </div>
      </div>
    </section>
  </div>
</template>

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
  padding: 2rem;
  scroll-snap-align: start;
}

.hero .overlay {
  position: absolute;
  width: 100%;
  height: 100%;
  background: rgba(0, 56, 101, 0.85);
}

.hero-content-container {
  display: flex;
  flex-direction: row;
  justify-content: space-between;

}
.hero-content{
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
  box-shadow: 0px 6px 16px rgba(0, 0, 0, 0.2);
}


.hero h1 {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 1rem;
  color: #FFD700; /* Gold */
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
  color: white;
  background-color: #FFD700; /* Gold */
  border-radius: 10px;
  text-decoration: none;
  transition: all 0.3s ease-in-out;
  gap: 10px;
  font-weight: bold;
}

.cta-button:hover {
  background-color: #E6C200; /* Darker Gold */
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
  color: white;
  opacity: 0.8;
  transition: opacity 0.3s;
}

.scroll-indicator:hover .scroll-icon {
  opacity: 1;
}

/* Bouncing Animation */
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(10px); }
}

/* Features Section */
.features {
  text-align: center;
  padding: 5rem 2rem;
  color: #003865; /* Dark Blue */
  background: #E3E3E3; /* Light Gray */
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
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0px 6px 16px rgba(0, 0, 0, 0.2);
  width: 280px;
  text-align: center;
}

.feature-icon {
  font-size: 2.8rem;
  color: #003865;
  margin-bottom: 10px;
}

/* How It Works */
.how-it-works {
  text-align: center;
  padding: 5rem 2rem;
  background: #003865; /* Dark Blue */
  color: white;
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
  background: #FFD700; /* Gold */
  color: #003865;
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
  background: white;
  color: #003865;
  width: 40px;
  height: 40px;
  line-height: 40px;
  border-radius: 50%;
  font-size: 1.2rem;
}

@media (max-width: 768px) {
  .hero-image{
    display: none;
  }
}
</style>
