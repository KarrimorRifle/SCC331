<script setup lang="ts">
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faXmark, faBars} from '@fortawesome/free-solid-svg-icons';
import { RouterLink } from 'vue-router';
import { useCookies } from 'vue3-cookies';
import { ref, defineProps, defineEmits, onMounted, watch } from 'vue';
import NotificationIcon from './Notifications/NotificationIcon.vue';
import axios from "axios"
import router from '@/router';
import { useAuthStore } from '@/stores/authStore';

const props = defineProps({
	isMobile: Boolean,
	isWarningModalOpen: Boolean,
	warnings: Array,
	warningCount: Number, 
	loggedIn: {
		type: Boolean,
		default: null
	}, 
	isAdmin: Boolean,
});

const { cookies } = useCookies();
const sessionId = cookies.get('session_id');
const isMenuOpen = ref(false);
const emit = defineEmits(["logout", "toggleWarningModal"]);

const authStore = useAuthStore();

const handleLogout = async() => {
	try {
		await axios.post("http://localhost:5002/logout", {}, {
			withCredentials: true
		})
		cookies.remove('session_id');
		authStore.logout();
		emit("logout");
		router.push("/");
	}catch(err) {
		console.log("Error encountered logging out:", err)
	}
}

// Toggle menu function
const toggleMenu = () => {
	isMenuOpen.value = !isMenuOpen.value;
};

const closeMenu = () =>{
  isMenuOpen.value = false;
}

onMounted(async() => {
	await authStore.checkUserAuthority();
	console.log(authStore.userAuthority)
});

watch(() => authStore.userAuthority, (newVal) => {
	console.log("User authority changed:", newVal);
});
</script>

<template>
	<nav class="navbar">
		<!-- Hamburger Menu Button (Visible on Mobile) -->
		<div class="navbar-header">
			<button class="hamburger" @click="toggleMenu">
				<font-awesome-icon :icon="faBars" />
			</button>

      <NotificationIcon 
        v-if="props.isMobile && loggedIn" 
        :warnings="props.warnings" 
        :warningCount="props.warningCount"
        :isWarningModalOpen="props.isWarningModalOpen" 
        @toggleWarningModal="emit('toggleWarningModal')"
      />
    </div>

    <!-- Desktop Navigation -->
    <div class="nav-links">
			<!-- normal links -->
      <RouterLink to="/" class="nav-link" exact-active-class="active" v-if="props.loggedIn">Home</RouterLink>
      <RouterLink to="/map" class="nav-link" exact-active-class="active" v-if="props.loggedIn">Map</RouterLink>
      <RouterLink to="/summaries" class="nav-link me-1 pe-5 border-end border-white" exact-active-class="active" v-if="props.loggedIn">Summary</RouterLink>

			<!-- Admins -->
			<template v-if="authStore.userAuthority === 'Admin' || authStore.userAuthority === 'Super Admin'">
				<RouterLink to="/create-warning" class="nav-link ms-4" exact-active-class="active" >Warnings</RouterLink>
				<RouterLink to="/admin" class="nav-link" exact-active-class="active" >Users</RouterLink>
				<RouterLink to="/inspection" class="nav-link me-1 pe-5 border-end border-white" exact-active-class="active" >Inspection</RouterLink>
			</template>
			<template v-if="authStore.userAuthority === 'Super Admin'">
				<RouterLink to="/change-domain" class="nav-link me-1 pe-5 border-end border-white" exact-active-class="active" >Change Domain</RouterLink>
			</template>
      <RouterLink to="/login" class="nav-link" exact-active-class="active" v-if="!props.loggedIn">Login</RouterLink>
      <RouterLink to="#" class="nav-link ms-4" v-if="props.loggedIn" @click.prevent="handleLogout">
        Log out
      </RouterLink>
    </div>

    <!-- Mobile Side Drawer -->
    <div class="mobile-menu" :class="{ open: isMenuOpen }">
      <button class="close-btn" @click="toggleMenu">
        <font-awesome-icon :icon="faXmark" />
      </button>
			<!-- normal links -->
      <RouterLink to="/" class="mobile-link" exact-active-class="active" v-if="props.loggedIn" @click="closeMenu">Home</RouterLink>
      <RouterLink to="/map" class="mobile-link" exact-active-class="active" v-if="props.loggedIn" @click="closeMenu">Map</RouterLink>
      <RouterLink to="/summaries" class="mobile-link" exact-active-class="active" v-if="props.loggedIn" @click="closeMenu">Summary</RouterLink>

			<!-- Admin links -->
			<template v-if="authStore.userAuthority === 'Admin' || authStore.userAuthority === 'Super Admin'">
				<RouterLink to="/create-warning" class="mobile-link" exact-active-class="active" @click="closeMenu">Create Warning</RouterLink>
				<RouterLink to="/admin" class="mobile-link" exact-active-class="active" @click="closeMenu">Admin</RouterLink>
				<RouterLink to="/inspection" class="mobile-link" exact-active-class="active" @click="closeMenu">Inspection</RouterLink>
			</template>

			<template v-if="authStore.userAuthority === 'Super Admin'">
				<RouterLink to="/change-domain" class="mobile-link" exact-active-class="active" @click="closeMenu">Change Domain</RouterLink>
			</template>
      <RouterLink to="/login" class="mobile-link" exact-active-class="active" v-if="!props.loggedIn" @click="closeMenu">Login</RouterLink>
      <RouterLink to="#" class="mobile-link" v-if="props.loggedIn" @click.prevent="handleLogout" @click="closeMenu">
        Log out
      </RouterLink>
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
	background-color: var(--primary-dark-bg);
	padding: 10px 20px;
	color: var(--primary-light-text);
	width: 100%;
	position: relative;
}

/* Desktop Navigation */
.nav-links {
	display: flex;
}

.nav-link {
	margin: 0 15px;
	color: var(--primary-light-text);
	text-decoration: none;
	font-size: 16px;
	font-weight: bold;
}

.active {
	color: var(--active);
}

/* Hamburger Button (Visible on Mobile) */
.hamburger {
	display: none;
	font-size: 24px;
	background: none;
	border: none;
	color: var(--primary-light-text);
	cursor: pointer;
}

/* Mobile Side Drawer */
.mobile-menu {
	position: fixed;
	top: 0;
	left: -250px; /* Initially hidden */
	width: 250px;
	height: 100vh;
	background: var(--primary-dark-bg);
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
	color: var(--primary-light-text);
	text-decoration: none;
	font-size: 18px;
}

/* Close Button */
.close-btn {
	background: none;
	border: none;
	color: var(--primary-light-text);
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
	height: 100%;
	background: rgba(0, 0, 0, 0.5);
	z-index: 999;
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
		z-index: 1000;
	}
}

/* Hamburger Button (Visible on Mobile) */
.hamburger {
	display: none;
	font-size: 24px;
	background: none;
	border: none;
	color: var(--primary-light-text);
	cursor: pointer;
}

/* Mobile Side Drawer */
.mobile-menu {
	position: fixed;
	top: 0;
	left: -250px; /* Initially hidden */
	width: 250px;
	height: 100vh;
	background: var(--primary-dark-bg);
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
	color: var(--primary-light-text);
	text-decoration: none;
	font-size: 18px;
}

/* Close Button */
.close-btn {
	background: none;
	border: none;
	color: var(--primary-light-text);
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
	height: 100%;
	background: rgba(0, 0, 0, 0.5);
	z-index: 999;
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
		z-index: 1000;
	}
}
</style>
