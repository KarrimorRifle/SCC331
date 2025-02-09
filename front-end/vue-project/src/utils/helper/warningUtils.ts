export const handleWarningButtonPressed = (areaLabel: string, warningsForArea: any[]) => {
  console.log(`⚠️ Warnings for ${areaLabel}:`, warningsForArea);
};

export const getCardBackgroundColor = (severity: string): string => {
  const severityColors: Record<string, string> = {
    doomed: "#FF0000",
    danger: "#FF4500",
    warning: "#FFA500",
    notification: "#4682B4",
  };
  return severityColors[severity] || "#ccc";
};