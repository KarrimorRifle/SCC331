<script setup lang="ts">
import { computed } from "vue";
import { isWarningModalOpen, warningModalData } from "@/utils/helper/warningUtils";
import { getCardBackgroundColor } from "@/utils/helper/warningUtils"; // Import background color function

const props = defineProps({
  overlayAreasConstant: {
    type: Array,
    required: true,
  },
});

const closeModal = () => {
  isWarningModalOpen.value = false;
};

// **Get Area Color Based on `overlayAreasConstant`**
const getAreaColor = computed(() => {
  const area = props.overlayAreasConstant.find(area => area.label === warningModalData.value.areaLabel);
  return area ? area.color : "#ccc"; // Default gray if not found
});
</script>

<template>
  <!-- Bootstrap Modal -->
  <div 
    class="modal fade show d-block" 
    v-if="isWarningModalOpen" 
    tabindex="-1" 
    role="dialog"
  >
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <!-- Sticky Modal Header -->
        <div 
          class="modal-header text-white sticky-top"
          :style="{ backgroundColor: getAreaColor }"
        >
          <h5 class="modal-title"> Warnings in {{ warningModalData.areaLabel }}</h5>
          <button type="button" class="btn-close" @click="closeModal"></button>
        </div>

        <!-- Scrollable Modal Body -->
        <div class="modal-body">
          <div v-if="warningModalData.warnings.length">
            <div 
              v-for="(warning, index) in warningModalData.warnings" 
              :key="index"
              class="alert text-white"
              :style="{ backgroundColor: getCardBackgroundColor(warning.Severity) }"
            >
              <h5 class="alert-heading">{{ warning.Title }}</h5>
              <p><strong>Severity:</strong> {{ warning.Severity.toUpperCase() }}</p>
              <p><strong>Summary:</strong> {{ warning.Summary }}</p>
            </div>
          </div>
          <div v-else class="alert alert-success text-center">
            ✅ No active warnings.
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeModal">Close</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Backdrop -->
  <div v-if="isWarningModalOpen" class="modal-backdrop fade show"></div>
</template>

<style scoped>
/* Ensures Bootstrap modal positioning */
.modal {
  display: block;
  background: rgba(0, 0, 0, 0.5);
}

/* Sticky Header */
.modal-header {
  font-weight: bold;
  position: sticky;
  top: 0;
  z-index: 1050;
}

/* Scrollable Modal Body */
.modal-body {
  max-height: 400px; /* Adjust as needed */
  overflow-y: auto;
  padding: 15px;
}

/* Styled warning cards with better contrast */
.alert {
  margin-bottom: 10px;
  border-radius: 8px;
}
</style>
