<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faBell, faXmark } from '@fortawesome/free-solid-svg-icons';
import { getCardBackgroundColor } from "@/utils/helper/warningUtils";

const props = defineProps({
  warnings: {
    type: Array as () => { Title: string; Location: string; Severity: string; Summary: string }[],
    required: true,
  },
  warningCount: Number,
  isWarningModalOpen: Boolean,
  isMobile: Boolean,
});

const emit = defineEmits(["toggleWarningModal"]);

const hasNewWarning = ref(false);

// Get the highest severity for notification color (affects bell icon)
const getHighestSeverity = computed(() => {
  const severityPriority = ["doomed", "danger", "warning", "notification"]; // Ordered by priority

  const highestSeverity = severityPriority.find(severity =>
    props.warnings.some(w => w.Severity === severity)
  );

  return highestSeverity ? getCardBackgroundColor(highestSeverity) : "#ccc"; // Default color
});

// Determine if there are active warnings for bell icon interaction
const hasActiveWarnings = computed(() => {
  return props.warnings.some(w => ["warning", "notification", "danger", "doomed"].includes(w.Severity));
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
  <div v-if="!isWarningModalOpen" class="notification-wrapper" :class="{ 'mobile-notification': isMobile }">
    <button
      class="notification-icon"
      :class="{ 'new-warning': hasNewWarning }"
      :style="{ backgroundColor: getHighestSeverity }"
      @click="emit('toggleWarningModal')"
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
/* Default (Desktop) - Bottom Right */
.notification-wrapper {
  position: absolute;
  bottom: 8px;
  right: 20px;
  z-index: 888;
}

/* Mobile Position - Inside Navbar */
.mobile-notification {
  position: static;
  margin-left: auto; /* Push it to the right inside the navbar */
}

.notification-icon {
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
