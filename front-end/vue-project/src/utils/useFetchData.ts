import { ref, onMounted, onUnmounted } from 'vue';
import axios from "axios";
// import { usePresetStore } from './useFetchPresets';

export function useFetchData(picoIds: any) {
  // Reactive state
  const updates = ref({});
  const warnings = ref([]);
  // const compiledPicoIDs = ref([]);
  // const presetData = usePresetStore();
  let pollingInterval: number | null | undefined = null;
  let warningInterval: number | null | undefined = null;

  const fetchWarnings = async () => {
    try {
      // const response = await axios.get("/api/reader/warnings", { withCredentials: true });
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
    return [];
    // try {
    //   const summaryResponse = await axios.get(`/api/reader/summary`, {withCredentials: true});
    //   // Flatten all IDs from every pico into a single array (ignoring "environment")
    //   compiledPicoIDs.value = Object.values(summaryResponse.data).reduce((acc: any[], info: any) => {
    //     for (const key in info) {
    //       if (key !== "environment") {
    //         acc = acc.concat(info[key].id);
    //       }
    //     }
    //     return acc;
    //   }, []);



    //   console.log(compiledPicoIDs.value);

    //   for (const PICO_ID of compiledPicoIDs.value) {
    //     const picoResponse = await axios.get(`/api/reader/pico/${PICO_ID}`, {withCredentials: true});
    //     if (picoResponse.status != 200) {
    //       console.error(`Error fetching Pico updates for ${PICO_ID}: ${picoResponse.status}`);
    //       continue;
    //     }

    //     // Convert new API format to old format
    //     // New format: { type: "...", movement: { "timestamp": "RoomID", ... } }
    //     // Old format: [ { roomID: <number>, logged_at: <timestamp> }, ... ]
    //     const picoMovementData = picoResponse.data.movement;
    //     const picoData = Object.entries(picoMovementData).map(([timestamp, roomID]) => ({
    //       roomID: presetData.boxes_and_data[roomID].label,
    //       logged_at: timestamp,
    //     }));
    //     //console.log(`Pico ${PICO_ID} data:`, picoData);

    //     if (JSON.stringify(picoData) !== JSON.stringify(updates.value[PICO_ID])) {
    //       //console.log(`Updates updated for ${PICO_ID}:`, picoData);
    //       updates.value = { ...updates.value, [PICO_ID]: picoData };
    //     }
    //   }
    // } catch (error) {
    //   console.error('Error fetching data:', error);
    // }
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
