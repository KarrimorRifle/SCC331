import { ref } from "vue";
export const isWarningModalOpen = ref(false);
export const warningModalData = ref<{ areaLabel: string; warnings: any[] }>({
  areaLabel: "",
  warnings: [],
});
export const handleWarningButtonPressed = (areaLabel: string, warningsForArea: any[]) => {
  warningModalData.value = { areaLabel, warnings: warningsForArea };
  isWarningModalOpen.value = true;
};

export const getCardBackgroundColor = (severity: string): string => {
  const severityColors: Record<string, string> = {
    doomed: "#FF0000",
    danger: "#FF4500",
    warning: "#FFA500",
    notification: "#4682B4",
    system: "#787878"
  };
  return severityColors[severity] || "#ccc";
};