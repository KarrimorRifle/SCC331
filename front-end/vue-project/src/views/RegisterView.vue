<template>
  <div id="login" class="d-flex justify-content-center align-items-center">
    <div style="color: #000; width:30rem; min-height: 20rem; background-color: #305f72;" class="card d-flex align-content-center justify-content-center px-4 py-4">
      <div class="text-warning fw-medium mb-2">{{ errorMessage }}</div>
      <form @submit.prevent="handleSubmit">
        <div class="mb-3">
          <label for="name" class="form-label text-light fw-bold mb-0">Full name</label>
          <input type="name" class="form-control" id="name" v-model="name" aria-describedby="nameHelp">
        </div>
        <div class="mb-3">
          <label for="email" class="form-label text-light fw-bold mb-0">Email address</label>
          <input type="email" class="form-control" id="email" v-model="email" aria-describedby="emailHelp">
          <div v-if="!email_compliance" id="emailHelp" class="form-text text-warning">Your email must end with @fakecompany.co.uk</div>
        </div>
        <div class="mb-3">
          <label for="password" class="form-label mb-0 fw-bold text-light">Password</label>
          <input type="password" class="form-control" id="password" v-model="password">
        </div>
        <!-- <div class="mb-3 form-check">
          <input type="checkbox" class="form-check-input" id="admin" v-model="isAdmin">
          <label class="form-check-label" for="admin">Admin</label>
        </div> -->
        <button type="submit" class="btn btn-primary">Submit</button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink, useRouter } from 'vue-router';
import { ref, computed } from 'vue';
import axios from 'axios';

const router = useRouter();

const name = ref('');
const email = ref('');
const password = ref('');
// const isAdmin = ref(false);
const errorMessage = ref<string | null>(null);

const email_compliance = computed(() => email.value.toLowerCase().endsWith('@fakecompany.co.uk'));

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
      const response = await axios.post("http://localhost:5001/register", {}, {
        headers: {
          "name": name.value,
          "email": email.value,
          "password": password.value
        }
      })

      if (response.status === 201) {
        router.push("/login");
      } else {
        errorMessage.value = 'Registry failed. You might already exist.';
      }
  } catch (error) {
    errorMessage.value = 'An error occurred during Registry. Please try again later.';
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