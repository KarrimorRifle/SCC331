import { ref } from 'vue';

const notificationSet = new Set<string>();

export const notificationQueue = ref<{ Title: string; Location?: string; Severity: string; Summary: string }[]>([]);

export const addNotification = (notification: { Title: string; Location?: string; Severity: string; Summary: string }) => {
  const notificationKey = JSON.stringify(notification);

  if (!notificationSet.has(notificationKey)) {
    notificationSet.add(notificationKey);
    notificationQueue.value.push(notification);
  }
};

export const dismissNotification = (index: number) => {
  if (index >= 0 && index < notificationQueue.value.length) {
    const removedNotification = notificationQueue.value[index];
    notificationSet.delete(JSON.stringify(removedNotification));
    notificationQueue.value.splice(index, 1);
  }
};
