import { ref, reactive, watch, onMounted, onUnmounted } from 'vue';
import axios from "axios";

const LOCAL_STORAGE_KEY = 'overlayAreas';

// Function to load overlay areas from local storage or default values
const loadOverlayAreas = () => {
  const storedData = localStorage.getItem(LOCAL_STORAGE_KEY);
  return storedData ? JSON.parse(storedData) : [
    { label: "Area 1", color: "#F18C8E", position: { top: 50, left: 50, width: 150, height: 150 } },
    { label: "Area 2", color: "#F0B7A4", position: { top: 200, left: 100, width: 150, height: 150 } },
    { label: "Area 3", color: "#F1D1B5", position: { top: 400, left: 50, width: 150, height: 150 } },
    { label: "Area 4", color: "#568EA6", position: { top: 300, left: 300, width: 150, height: 150 } }
  ];
};

export function useFetchData(picoIds) {
  // Reactive state
  const overlayAreasConstant = reactive(loadOverlayAreas());
  const overlayAreasData = ref([]);
  const updates = ref({});
  const environmentHistory = ref({});
  const warnings = ref([]);
  let pollingInterval = null;
  let warningInterval = null;

  // Watch for overlay area changes and save to localStorage
  watch(overlayAreasConstant, (newValue) => {
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(newValue));
  }, { deep: true });

  // Function to track environment data
  const trackEnvironmentData = (label, data) => {
    if (!data) return;
    const timestamp = Date.now();
    if (!environmentHistory.value[label]) {
      environmentHistory.value[label] = [];
    }
    environmentHistory.value[label].push({
      timestamp,
      temperature: data.temperature,
      sound: data.sound,
      light: data.light,
    });
    if (environmentHistory.value[label].length > 20) {
      environmentHistory.value[label].shift();
    }
  };

  const fetchWarnings = async () => {
    try {
      const response = await axios.get("http://localhost:5003/warnings", { withCredentials: true });
      warnings.value = response.data;
    } catch (error) {
      console.error("Error fetching warnings:", error);
    }
  };


  // Function to fetch data
  const fetchData = async () => {
        try {
      // Fetch overlay data
      const summaryResponse = await axios.get("/summary", {withCredentials: true});
      const summaryData = summaryResponse.data;

      // Track environment data
      Object.entries(summaryData).forEach(([key, area]) => {
        if (area.environment && Object.keys(area.environment).length > 0) {
          trackEnvironmentData(key, area.environment);
        } else {
          console.warn(`Empty or missing environment data for Key: ${key}`);
        }
      });

      if (JSON.stringify(summaryData) !== JSON.stringify(overlayAreasData.value)) {
        console.log('Overlay areas updated:', summaryData);
        overlayAreasData.value = summaryData;
      }

      // Fetch updates from multiple Pico IDs
      for (const PICO_ID of picoIds) {
        const picoResponse = await axios.get(`/pico/${PICO_ID}`, {withCredentials: true});
        if (picoResponse.status != 200) {
          console.error(`Error fetching Pico updates for ${PICO_ID}: ${picoResponse.status}`);
          continue;
        }

        const picoData = await picoResponse.data;
        console.log(`Pico ${PICO_ID} data:`, picoData);

        if (JSON.stringify(picoData) !== JSON.stringify(updates.value[PICO_ID])) {
          console.log(`Updates updated for ${PICO_ID}:`, picoData);
          updates.value = { ...updates.value, [PICO_ID]: picoData };
        }
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  // Lifecycle hooks
  onMounted(() => {
    fetchData();
    fetchWarnings();
    //5000 = fetch the data every 5 seconds
    pollingInterval = setInterval(fetchData, 5000);
    warningInterval = setInterval(fetchWarnings, 5000);
  });

  onUnmounted(() => {
    if (pollingInterval) clearInterval(pollingInterval);
    if (warningInterval) clearInterval(warningInterval);
  });

  return {
    overlayAreasConstant,
    overlayAreasData,
    updates,
    environmentHistory,
    warnings,
  };
}
