import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';
import { useCookies } from 'vue3-cookies';

export const useAuthStore = defineStore('auth', () => {
  const { cookies } = useCookies();
  const isLoggedIn = ref<boolean>(!!cookies.get("session_id"));
  const userAuthority = ref<string | null>(null);

  const checkUserAuthority = async () => {
    try {
      const response = await axios.get('/api/login/validate_cookie', { withCredentials: true });
      console.log(response)
      userAuthority.value = response.data.authority;
    } catch (error) {
      console.error('Failed to fetch user authority:', error);
      userAuthority.value = null;
    }
  };

  const login = () => {
    isLoggedIn.value = true;
    checkUserAuthority();
  };

  const logout = () => {
    isLoggedIn.value = false;
    userAuthority.value = null;
  };

  return {
    isLoggedIn,
    userAuthority,
    checkUserAuthority,
    login,
    logout,
  };
});
