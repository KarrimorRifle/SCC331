<script setup lang="ts">
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faXmark } from '@fortawesome/free-solid-svg-icons';
import { ref, watch, PropType } from "vue";

const props = defineProps({
  warnings: {
    type: Array as PropType<{ Title: string; Location: string; Severity: string; Summary: string }[]>,
    required: true,
  },
  warningCount: Number, 
  isMobile: Boolean, 
});

const emit = defineEmits(["close"]);

// Notification state (now always reflects `props.warnings`)
const notificationQueue = ref<{ Title: string; Location: string; Summary: string; Severity: string }[]>([]);

// Background color based on severity
const getCardBackgroundColor = (severity: string): string => {
  const severityColors: Record<string, string> = {
    doomed: "#FF0000",
    danger: "#FF4500",
    warning: "#FFA500",
    notification: "#4682B4",
  };
  return severityColors[severity] || "#ccc";
};

// Remove notification manually
const dismissNotification = (index: number) => {
  notificationQueue.value.splice(index, 1);
};

// Always sync modal warnings list with `props.warnings`
watch(
  () => props.warnings,
  (newWarnings) => {
    if (!newWarnings) return;
    notificationQueue.value = [...newWarnings]; // ✅ Always updates instantly
  },
  { deep: true, immediate: true }
);
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

        <div class="modal-body">
          <div v-if="notificationQueue.length > 0">
            <div
              v-for="(notification, index) in notificationQueue"
              :key="index"
              class="warning-card"
              :style="{ backgroundColor: getCardBackgroundColor(notification.Severity) }"
            >
              <h4>
                {{ notification.Title }} - <span class="severity-text">{{ notification.Severity.toUpperCase() }}</span>
              </h4>
              <p><strong>📍 Location:</strong> {{ notification.Location }}</p>
              <p><strong>📢 {{ notification.Summary }}</strong></p>
              <button class="dismiss-btn" @click="dismissNotification(index)">Dismiss</button>
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
  bottom: 80px;
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
  background: white;
  color: #333;
  width: 100%;
  border-radius: 10px;
  border-left: 6px solid #305f72;
  max-height: 40vh;
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
  background: white;
}

.modal-header h3 {
  font-size: 18px;
  color: #305f72;
  font-weight: bold;
}

.close-btn {
  border: none;
  background: none;
  font-size: 18px;
  cursor: pointer;
  color: #333;
  transition: color 0.2s ease-in-out;
}

.close-btn:hover {
  color: #ff4d4d;
}

/* Warning Cards */
.warning-card {
  border-left: 5px solid;
  padding: 12px;
  margin: 20px;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  color: white;
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
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  background-color: #305f72;
  align-self: flex-end;
  transition: background 0.3s ease-in-out;
}

.dismiss-btn:hover {
  background-color: #568ea6;
}

.no-warnings {
  text-align: center;
  font-size: 14px;
  color: #666;
  padding: 10px 0;
}

/* Adjustments for Text Contrast */
.warning-card p {
  color: #f9f9f9;
}

.warning-card strong {
  color: #ffffff;
}
</style>
