export const updateTabHeight = (tabName: string, tabHeight: { value: number }) => {
    if (typeof tabName !== 'string') {
        console.error("updateTabHeight: Invalid tabName, expected string but got", tabName);
        return;
    }
    const tab = document.querySelector(tabName);
    if (tab) {
        console.log('height: ', tab.clientHeight);
        tabHeight.value = tab.clientHeight;
    }
};
  