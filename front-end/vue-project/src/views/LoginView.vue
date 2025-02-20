<template>
  <div id="login" class="d-flex justify-content-center align-items-center">
    <div style="color: #000; width:30rem; min-height: 20rem; background-color: #305f72;" class="card d-flex align-content-center justify-content-center px-4 py-4">
      <div class="text-warning fw-medium mb-2">{{ errorMessage }}</div>
      <form @submit.prevent="handleSubmit">
        <div class="mb-3">
          <label for="email" class="form-label text-light fw-bold mb-0">Email address</label>
          <input type="email" class="form-control" id="email" v-model="email" aria-describedby="emailHelp">
          <div v-if="!email_compliance" id="emailHelp" class="form-text text-warning">Your email must end with @fakecompany.co.uk</div>
        </div>
        <div class="mb-3">
          <label for="password" class="form-label mb-0 fw-bold text-light">Password</label>
          <input type="password" class="form-control" id="password" v-model="password">
        </div>
        <button type="submit" class="btn btn-primary">Submit</button>
      </form>
      <div class="d-flex justify-content-center align-items-center mt-3">
        <p class="mb-0">Not registered?</p>
        <RouterLink to="/register" class="ms-1 text-decoration-underline text-light">Register</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink, useRouter } from 'vue-router';
import { ref, computed, defineEmits } from 'vue';
import axios from 'axios';

const router = useRouter();

const email = ref('');
const password = ref('');
const errorMessage = ref<string | null>(null);

const email_compliance = computed(() => email.value.toLowerCase().endsWith('@fakecompany.co.uk'));

const emit = defineEmits(["login"])

const handleSubmit = async () => {
  if (!email_compliance.value) {
    alert('Your email must end with @fakecompany.co.uk');
    return;
  }

  console.log('Email:', email.value);
  console.log('Password:', password.value);
  // console.log('Is Admin:', isAdmin.value);
  // Add your form submission logic here

  try {
    const response = await axios.post("http://localhost:5002/login", {}, {
      withCredentials: true,
      headers: {
        "Access-Control-Allow-Credentials": true,
        "email": email.value,
        "password": password.value
      }
    });

    if (response.status === 200) {
      // Save the expiration date (if present)
      if (response.data && response.data.expires) {
        localStorage.setItem("session_expiry", response.data.expires);
      }
      router.push("/");
      emit("login");
    } else {
      errorMessage.value = 'Login failed. Please check your credentials and try again.';
    }
  } catch (error) {
    errorMessage.value = 'Wrong username or password. Try again.';
    console.error('Error:', error);
  }
};
</script>

<style scoped>
#login {
  height: 90vh;
  background: rgb(235, 235, 235);
}
</style>