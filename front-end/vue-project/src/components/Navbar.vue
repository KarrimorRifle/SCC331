<script setup lang="ts">
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faXmark, faBars} from '@fortawesome/free-solid-svg-icons';
import { RouterLink } from 'vue-router';
import { useCookies } from 'vue3-cookies';
import { ref } from 'vue';

const { cookies } = useCookies();
const sessionId = cookies.get('session-id');
</script>

<template>
  <nav class="navbar">
    <!-- Hamburger Menu Button (Visible on Mobile) -->
    <button class="hamburger" @click="toggleMenu">
      <font-awesome-icon :icon="faBars" />
    </button>

    <!-- Desktop Navigation -->
    <div class="nav-links">
      <RouterLink to="/" class="nav-link" exact-active-class="active">Airport View</RouterLink>
      <RouterLink to="/summary" class="nav-link" exact-active-class="active">Summary View</RouterLink>
      <RouterLink to="/login" class="nav-link" exact-active-class="active" v-if="!sessionId">Login</RouterLink>
    </div>

    <!-- Mobile Side Drawer -->
    <div class="mobile-menu" :class="{ open: isMenuOpen }">
      <button class="close-btn" @click="toggleMenu">
        <font-awesome-icon :icon="faXmark" />
      </button>
      <RouterLink to="/" class="mobile-link" @click="toggleMenu">Airport View</RouterLink>
      <RouterLink to="/summary" class="mobile-link" @click="toggleMenu">Summary View</RouterLink>
      <RouterLink to="/login" class="mobile-link" v-if="!sessionId" @click="toggleMenu">Login</RouterLink>
    </div>

    <!-- Overlay when menu is open -->
    <div class="overlay" v-if="isMenuOpen" @click="toggleMenu"></div>
  </nav>
</template>

<style scoped>
/* Navbar Layout */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #305f72;
  padding: 10px 20px;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 100%;
  position: relative;
}

/* Desktop Navigation */
.nav-links {
  display: flex;
}

.nav-link {
  margin: 0 15px;
  color: white;
  text-decoration: none;
  font-size: 16px;
  font-weight: bold;
}

.nav-link:hover {
  color: #f1d1b5;
}

.active {
  color: #a9a9a9;
}

/* Hamburger Button (Visible on Mobile) */
.hamburger {
  display: none;
  font-size: 24px;
  background: none;
  border: none;
  color: white;
  cursor: pointer;
}

/* Mobile Side Drawer */
.mobile-menu {
  position: fixed;
  top: 0;
  left: -250px; /* Initially hidden */
  width: 250px;
  height: 100vh;
  background: #305f72;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  padding: 20px;
  transition: left 0.3s ease-in-out;
}

/* When menu is open */
.mobile-menu.open {
  left: 0;
}

/* Mobile Menu Links */
.mobile-link {
  padding: 15px;
  color: white;
  text-decoration: none;
  font-size: 18px;
}

.mobile-link:hover {
  background: #568ea6;
}

/* Close Button */
.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 22px;
  text-align: right;
  cursor: pointer;
  margin-bottom: 20px;
}

/* Overlay Effect */
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  z-index: 10;
}

/* Responsive Design */
@media (max-width: 768px) {
  .nav-links {
    display: none; /* Hide default nav links */
  }

  .hamburger {
    display: block; /* Show hamburger button */
  }

  .mobile-menu {
    z-index: 15;
  }
}
</style>
