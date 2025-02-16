import { ref } from 'vue';

export const notificationQueue = ref<{ Title: string; Location?: string; Severity: string; Summary: string }[]>([]);

export const addNotification = (notification: { Title: string; Location?: string; Severity: string; Summary: string }) => {
  notificationQueue.value.push(notification);
};

export const dismissNotification = (index: number) => {
  notificationQueue.value.splice(index, 1);
};
