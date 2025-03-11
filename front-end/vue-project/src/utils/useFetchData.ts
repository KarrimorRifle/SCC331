import { ref, onMounted, onUnmounted } from 'vue';
import axios from "axios";

export function useFetchData(picoIds: any) {
  // Reactive state
  const updates = ref({});
  const warnings = ref([]);
  let pollingInterval: number | null | undefined = null;
  let warningInterval: number | null | undefined = null;

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
    updates,
    warnings,
  };
}
