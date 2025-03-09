<script setup lang="ts">
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faXmark } from '@fortawesome/free-solid-svg-icons';
import { getCardBackgroundColor } from "@/utils/helper/warningUtils"; // Import the function
import { ref, PropType, computed } from "vue";

const props = defineProps({
  warnings: {
    type: Array as PropType<{ Title: string; Location?: string; Severity: string; Summary: string }[]>,
    required: true,
  },
  warningCount: Number, 
  isMobile: Boolean, 
});

const emit = defineEmits(["close", "dismiss"]);

const mode = ref<string>("warnings");

const filteredWarnings = computed(() => props.warnings.filter(warning => {
  if (mode.value !== 'system') return warning.Severity !== 'system';
  return warning.Severity === 'system';
}));

const switchMode = (newMode: string) => {
  mode.value = newMode;
};

</script>

<template>
  <transition name="fade">
    <div class="notification-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>⚠️ Warning Notifications</h3>
          <button class="close-btn" @click="emit('close')">
            <font-awesome-icon :icon="faXmark" />
          </button>
        </div>

        <div class="modal-tabs">
          <button :class="{ active: mode === 'warnings' }" @click="switchMode('warnings')">
            Warnings <span class="count">{{ props.warnings.filter(w => w.Severity !== 'system').length }}</span>
          </button>
          <button :class="{ active: mode === 'system' }" @click="switchMode('system')">
            System <span class="count">{{ props.warnings.filter(w => w.Severity === 'system').length }}</span>
          </button>
        </div>

        <div class="modal-body">
          <div v-if="filteredWarnings.length > 0">
            <div
              v-for="(notification, index) in filteredWarnings"
              :key="index"
              class="warning-card"
              :style="{ backgroundColor: getCardBackgroundColor(notification.Severity) }"
            >
              <h4>
                {{ notification.Title }} - <span class="severity-text">{{ notification.Severity.toUpperCase() }}</span>
              </h4>
              <p v-if="notification.Location"><strong>📍 Location:</strong> {{ notification.Location }}</p>
              <p><strong>📢 {{ notification.Summary }}</strong></p>
              <button class="dismiss-btn" @click="emit('dismiss', index)">Dismiss</button>
            </div>
          </div>
          <div v-else class="no-warnings">✅ No active warnings.</div>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
/* Notification Modal */
.notification-modal {
  position: fixed;
  bottom: 8px;
  right: 20px;
  width: 340px;
  z-index: 888;
  display: flex;
  justify-content: flex-end;
  border-radius: 8px;
  box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.3);
}

/* Modal Content */
.modal-content {
  background: var(--primary-light-bg);
  color: var(--primary-dark-text);
  width: 100%;
  border-radius: 10px;
  border-left: 6px solid #305f72;
  height: 40vh;
  overflow-y: auto;
}
@media (max-width: 768px) {
  .notification-modal {
    width: 100%;
    right: 0px;
    bottom: 0px;
    border-radius: 0px;
  }
  .modal-content{
    border-radius: 0px;
    max-height: 100vh;
    min-height: 100vh;
  }
}
/* Modal Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  position: sticky;
  top: 0;
  z-index: 888;
  padding: 10px 20px;
  background: var(--primary-light-bg);
}

.modal-header h3 {
  font-size: 18px;
  color: var(--primary-dark-text);
  font-weight: bold;
}

.close-btn {
  border: none;
  background: none;
  font-size: 18px;
  cursor: pointer;
  color: var(--primary-dark-text);
  transition: color 0.2s ease-in-out;
}

.close-btn:hover {
  color: var(--warning-text-hover);
}

/* Modal Tabs */
.modal-tabs {
  display: flex;
  justify-content: space-around;
  margin-bottom: 10px;
}

.modal-tabs button {
  flex: 1;
  padding: 10px;
  border: none;
  background: var(--primary-light-bg);
  cursor: pointer;
  transition: background 0.3s ease-in-out;
  position: relative;
}

.modal-tabs button.active {
  background: var(--primary-dark-bg);
  color: var(--primary-light-text);
}

.modal-tabs button:hover:not(.active) {
  background: #e1e1e1;
}

.modal-tabs .count {
  background: var(--notification-bg);
  color: var(--primary-light-text);
  border-radius: 50%;
  padding: 2px 6px;
  font-size: 12px;
  position: absolute;
  top: 5px;
  right: 8px;
  min-width: 1.5rem;
}

/* Warning Cards */
.warning-card {
  border-left: 5px solid;
  padding: 12px;
  margin: 20px;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  color: var(--primary-light-text);
}

/* Severity-Based Title Colors */
h4 {
  font-size: 16px;
  margin-bottom: 5px;
  font-weight: bold;
}

.severity-text {
  font-weight: bold;
  font-size: 14px;
}

/* Dismiss Button */
.dismiss-btn {
  margin-top: 8px;
  padding: 8px 12px;
  font-size: 14px;
  color: var(--primary-light-text);
  border: none;
  border-radius: 6px;
  cursor: pointer;
  background-color: var(--primary-dark-bg);
  align-self: flex-end;
  transition: background 0.3s ease-in-out;
}

.dismiss-btn:hover {
  background-color: var(--primary-dark-bg-hover);
}

.no-warnings {
  text-align: center;
  font-size: 14px;
  color: var(--negative-text);
  padding: 10px 0;
}

/* Adjustments for Text Contrast */
.warning-card p {
  color: var(--primary-light-text);
}

.warning-card strong {
  color: var(--primary-light-text);
}
</style>
