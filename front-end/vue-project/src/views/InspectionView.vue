<template>
  <div class="inspection bg-light text-dark">
    <!-- <user-movement-modal :show-modal="true"/> -->
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import UserMovementModal from '@/components/Summary/LiveUpdates/UserMovementModal.vue';

const showModal = ref(false);
</script>

<style>
@media (min-width: 1024px) {
  .inspection {
    min-height: 100vh;
    display: flex;
    align-items: center;
    flex-direction: column;
  }
}
</style>
