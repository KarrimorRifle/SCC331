import { ref, onMounted, onUnmounted } from 'vue';
import axios from "axios";

export function useFetchData(picoIds) {
  // Reactive state
  const overlayAreasData = ref([]);
  const updates = ref({});
  const environmentHistory = ref({});
  const warnings = ref([]);
  let pollingInterval = null;
  let warningInterval = null;

  
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
      // const response = await axios.get("http://localhost:5003/warnings", { withCredentials: true });
      const response = await axios.get("/data.json");
      //warnings.value = response.data;

      
      if (JSON.stringify(warnings.value) !== JSON.stringify(response.data.warnings)) {
        warnings.value = response.data;
      }
      
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
        //console.log('Overlay areas updated:', summaryData);
        overlayAreasData.value = summaryData;
      }

      // Fetch updates from multiple Pico IDs
      for (const PICO_ID of picoIds) {
        const picoResponse = await axios.get(`/pico/${PICO_ID}`, {withCredentials: true});
        if (picoResponse.status != 200) {
          console.error(`Error fetching Pico updates for ${PICO_ID}: ${picoResponse.status}`);
          continue;
        }

        // Convert new API format to old format
        // New format: { type: "...", movement: { "timestamp": "RoomID", ... } }
        // Old format: [ { roomID: <number>, logged_at: <timestamp> }, ... ]
        const picoMovementData = picoResponse.data.movement;
        const picoData = Object.entries(picoMovementData).map(([timestamp, roomID]) => ({
          roomID,
          logged_at: timestamp,
        }));
        //console.log(`Pico ${PICO_ID} data:`, picoData);

        if (JSON.stringify(picoData) !== JSON.stringify(updates.value[PICO_ID])) {
          //console.log(`Updates updated for ${PICO_ID}:`, picoData);
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
    overlayAreasData,
    updates,
    environmentHistory,
    warnings,
  };
}
