<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faBell, faXmark } from '@fortawesome/free-solid-svg-icons';

const props = defineProps({
  warnings: {
    type: Array as () => { Title: string; Location: string; Severity: string; Summary: string }[],
    required: true,
  },
  isWarningModalOpen: Boolean,
});

const emit = defineEmits(["toggleWarningModal"]);

const hasNewWarning = ref(false);

// Get the highest severity for notification color (affects bell icon)
const getHighestSeverity = computed(() => {
  if (props.warnings.some(w => w.Severity === "doomed")) return "#FF0000";
  if (props.warnings.some(w => w.Severity === "danger")) return "#FF4500";
  if (props.warnings.some(w => w.Severity === "warning")) return "#FFA500";
  if (props.warnings.some(w => w.Severity === "notification")) return "#4682B4";
  return "#ccc"; // Default color
});

// Determine if there are active warnings for bell icon interaction
const hasActiveWarnings = computed(() => {
  return props.warnings.some(w => ["warning", "notification"].includes(w.Severity));
});

// Watch for new warnings and trigger bell animation
watch(
  () => props.warnings,
  (newWarnings) => {
    if (newWarnings.some(w => ["warning", "notification"].includes(w.Severity))) {
      hasNewWarning.value = true;
      setTimeout(() => {
        hasNewWarning.value = false;
      }, 1000);
    }
  },
  { deep: true, immediate: true }
);
</script>

<template>
  <div class="notification-wrapper">
    <button
      class="notification-icon"
      :class="{ 'new-warning': hasNewWarning }"
      :style="{ backgroundColor: getHighestSeverity }"
      @click="hasActiveWarnings ? emit('toggleWarningModal') : null"
      :disabled="!hasActiveWarnings"
    >
      <font-awesome-icon :icon="isWarningModalOpen ? faXmark : faBell" class="bell-icon" />
    </button>

    <!-- Tooltip for "No Active Warnings" -->
    <div v-if="!hasActiveWarnings && !isWarningModalOpen" class="tooltip">
      No Active Warnings
    </div>
  </div>
</template>

<style scoped>
/* Floating Notification Icon */
.notification-icon {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: none;
  color: white;
  cursor: pointer;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
  transition: background-color 0.1s ease-in-out, transform 0.1s ease-in-out;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 888;
}

@media (max-width: 768px) {
    .notification-icon{
        bottom: 80px;
    }
}

.notification-icon:disabled {
  cursor: not-allowed;
  background-color: #ccc;
}

.new-warning {
  animation: pulse 0.8s infinite alternate;
}

@keyframes pulse {
  0% { transform: scale(1); }
  100% { transform: scale(1.1); }
}

.bell-icon {
  font-size: 22px;
}

.tooltip {
  position: absolute;
  bottom: 60px;
  right: 0;
  background-color: #fff;
  color: #333;
  padding: 5px 10px;
  font-size: 12px;
  border-radius: 5px;
  box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2);
}
</style>
