export const updateTabHeight = (tabName: string, tabHeight: { value: number }) => {
    try {
    if (typeof tabName !== 'string') {
        return;
    }
    const tab = document.querySelector(tabName);
    if (tab) {
        tabHeight.value = tab.clientHeight;
    }} catch (error) {
    }
};
  