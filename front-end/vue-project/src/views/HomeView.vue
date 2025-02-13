<script setup lang="ts">
import { RouterLink } from 'vue-router';
import { ref, onMounted, onUnmounted } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faSignInAlt } from '@fortawesome/free-solid-svg-icons';
import { guidanceItems } from '@/constants/index'; 

defineProps({
  loggedIn: Boolean, // Prop to check if user is logged in
});

const activeIndex = ref(0);
const totalSlides = guidanceItems.length;
const guidanceContainer = ref<HTMLElement | null>(null);

const scrollToSlide = (index: number) => {
  activeIndex.value = index;
  if (guidanceContainer.value) {
    guidanceContainer.value.scrollTo({
      left: guidanceContainer.value.clientWidth * index,
      behavior: "smooth"
    });
  }
};

const updateActiveIndex = () => {
  if (guidanceContainer.value) {
    const scrollLeft = guidanceContainer.value.scrollLeft;
    const slideWidth = guidanceContainer.value.clientWidth;
    activeIndex.value = Math.round(scrollLeft / slideWidth);
  }
};

const handleTouch = (() => {
  let startX = 0;
  return {
    start: (event: TouchEvent) => {
      startX = event.touches[0].clientX;
    },
    end: (event: TouchEvent) => {
      const deltaX = event.changedTouches[0].clientX - startX;
      if (guidanceContainer.value) {
        if (deltaX > 50) {
          guidanceContainer.value.scrollBy({ left: -guidanceContainer.value.clientWidth, behavior: "smooth" });
        } else if (deltaX < -50) {
          guidanceContainer.value.scrollBy({ left: guidanceContainer.value.clientWidth, behavior: "smooth" });
        }
      }
    }
  };
})();

onMounted(() => {
  if (guidanceContainer.value) {
    guidanceContainer.value.addEventListener("touchstart", handleTouch.start);
    guidanceContainer.value.addEventListener("touchend", handleTouch.end);
    guidanceContainer.value.addEventListener("scroll", updateActiveIndex);
  }
});

onUnmounted(() => {
  if (guidanceContainer.value) {
    guidanceContainer.value.removeEventListener("touchstart", handleTouch.start);
    guidanceContainer.value.removeEventListener("touchend", handleTouch.end);
    guidanceContainer.value.removeEventListener("scroll", updateActiveIndex);
  }
});
</script>

<template>
  <div class="welcome-container">
    <div class="content">
      <h1 class="fade-in">
        <FontAwesomeIcon :icon="faMapMarkedAlt" class="icon" /> Welcome to the Airport Monitoring System
      </h1>
      <p class="fade-in delay-1">
        Stay updated with real-time airport data, including occupancy, luggage tracking, environmental conditions, and safety alerts.
      </p>
    </div>

    <div class="guidance-wrapper">
      <div ref="guidanceContainer" class="guidance-container">
        <div v-for="(item, index) in guidanceItems" :key="index" class="slide">
          <FontAwesomeIcon :icon="item.icon" class="list-icon" />
          <h2>{{ item.title }}</h2>
          <p>{{ item.description }}</p>
        </div>
      </div>

      <div class="navigation">
        <span 
          v-for="(dot, index) in totalSlides" 
          :key="index" 
          :class="{ active: activeIndex === index }" 
          @click="scrollToSlide(index)"
        ></span>
      </div>
    </div>

    <div v-if="!loggedIn" class="button-container fade-in delay-2">
      <RouterLink to="/login" class="login-button">
        <FontAwesomeIcon :icon="faSignInAlt" class="btn-icon" /> Login to Monitor
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
/* General Styling */
.welcome-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  text-align: center;
  background: linear-gradient(to bottom, #F8F9FA, #E3F2FD);
  color: #305F72;
  overflow-y: auto;
  padding: 2rem;
}

/* Content Styling */
.content {
  z-index: 1;
  max-width: 600px;
}

/* Headings */
h1 {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

h2 {
  font-size: 1.8rem;
  margin: 1rem 0;
}

/* Icons */
.icon {
  color: #568EA6;
  margin-right: 10px;
}

.list-icon {
  color: #F18C8E;
  margin-bottom: 10px;
  font-size: 2rem;
}

/* Login Button */
.button-container {
  margin-top: 1.5rem;
}

.login-button {
  padding: 0.8rem 2rem;
  font-size: 1.2rem;
  color: white;
  background-color: #568EA6;
  border-radius: 8px;
  text-decoration: none;
  transition: all 0.3s ease-in-out;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.login-button:hover {
  background-color: #305F72;
  transform: scale(1.05);
}

/* Guidance Container */
.guidance-wrapper {
  position: relative;
  width: 50%;
}

.guidance-container {
  display: flex;
  width: 100%;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.guidance-container::-webkit-scrollbar {
  display: none;
}

.slide {
  flex: 0 0 100%;
  scroll-snap-align: center;
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* Navigation Dots */
.navigation {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 1rem;
  align-items: center;
}

.navigation span {
  width: 10px;
  height: 10px;
  background: #ccc;
  border-radius: 50%;
  transition: 0.3s;
  cursor: pointer;
}

.navigation span:hover {
  background: #305F72;
}

.navigation .active {
  background: #305F72;
  transform: scale(1.2);
}

/* Mobile View - Max Width 768px */
@media (max-width: 768px) {
  .welcome-container {
    padding: 1.5rem;
  }

  .content {
    max-width: 100%;
  }

  h1 {
    font-size: 2rem;
    text-align: center;
  }

  h2 {
    font-size: 1.5rem;
  }

  p {
    font-size: 1rem;
    padding: 0 1rem;
  }

  .guidance-wrapper {
    width: 90%;
  }

  .slide {
    padding: 1.5rem;
    border-radius: 8px;
  }

  .navigation {
    gap: 5px;
  }

  .navigation span {
    width: 8px;
    height: 8px;
  }

  .login-button {
    font-size: 1rem;
    padding: 0.6rem 1.5rem;
  }
}

</style>
