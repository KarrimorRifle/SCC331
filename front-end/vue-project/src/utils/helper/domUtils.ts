export const updateTabHeight = (tabName: string, tabHeight: { value: number }) => {
    const tab = document.querySelector(tabName);
    if (tab) {
        console.log('height: ', tab.clientHeight);
        tabHeight.value = tab.clientHeight;
    }
};
  