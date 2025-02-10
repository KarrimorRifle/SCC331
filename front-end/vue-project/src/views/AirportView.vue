<script setup lang="ts">
import AirportMap from '@/components/AirportMap.vue';
import DashBoard from "@/components/Dashboard.vue";
import {onMounted, onUnmounted, ref, watch, computed }from "vue"
import axios from "axios";
import OverlayArea from '@/components/OverlayArea.vue';
import type { Timeout } from "node:timers";
import type {preset, presetListType, boxAndData, boxType, summaryType, environmentData, dataObject} from "../utils/mapTypes";

let pollingInterval: Timeout;
let summary = ref<summaryType>(<summaryType>{});
let presetList = ref<presetListType>(<presetListType>{});
let canEdit = ref<boolean>(false);
let canCreate = ref<boolean>(false);
let canDelete = ref<boolean>(false);
let currentPreset = ref<number|string>(-1);
let presetData = ref<preset>(<preset>{});
const defaultPresetId = ref<number|string>(-1);
let presetImage = ref<string>("");
  //Data used by the App
let boxes_and_data = ref<boxAndData>(<boxAndData>{});

async function validateUser() {
  try {
    let userValidationRequest = await axios.get("http://localhost:5002/validate_cookie", {
      withCredentials: true,
    });

    let uid = userValidationRequest.data.uid;
    canDelete.value = presetData.value?.owner_id == uid;
    canEdit.value = presetData.value?.trusted?.includes(uid) || canDelete.value;
    canCreate.value = userValidationRequest.data.authority == "Admin";
  } catch (error) {
    console.error("Error validating user:", error);
    canEdit.value = false;
  }
}

const processPresetImage = () => {
  if (presetData.value.image?.data && presetData.value.image?.name) {
    const imageType = presetData.value.image.name.split('.').pop();
    presetImage.value = `data:image/${imageType};base64,${presetData.value.image.data}`;
  } else {
    presetImage.value = "";
  }
};

watch(currentPreset, async () => {
  await fetchPreset();
  create_data();
  validateUser();
});


watch(summary, () => {
  update_data();
});

onMounted(async() => {
  // Make sure data is always being updated
  pollingInterval = setInterval(fetchSummary, 5000);
  // Grab the list of presets
  try {
    await fetchPresets();
    // Grab default preset and set it to the current one
    if (presetList.value?.default) {
      currentPreset.value = presetList.value.default;
    } else if (presetList.value.presets.length > 0) {
      currentPreset.value = presetList.value.presets[0].id;
    }
    await fetchPreset();
  } catch (error) {
    console.error("Error on mount fetching:", error);
  }
  validateUser();
  create_data();
});

onUnmounted(() => {
  if (pollingInterval) clearInterval(pollingInterval);
});

const fetchSummary = async() => {
  let request = await axios.get("http://localhost:5003/summary",
    { withCredentials: true});
  summary.value = request.data;
}

const fetchPresets = async() => {
  let request = await axios.get("http://localhost:5010/presets",
    {withCredentials: true});
  presetList.value = request.data;
  // Set the default preset ID
  defaultPresetId.value = presetList.value.default;
}

const fetchPreset = async() => {
  let request = await axios.get(`http://localhost:5010/presets/${currentPreset.value}`,
    {withCredentials: true});
  presetData.value = request.data;
  processPresetImage();
}

const props = defineProps({
  overlayAreasConstant: {
    type: Array,
    required: true,
  },
  overlayAreasData: {
    type: Object,
    required: true,
  },
});

// I need to create a function to construct the object i want to v model on mount
const create_data = () => {
  // Add box data per room
  presetData.value.boxes?.forEach((box: boxType) => {
    if(boxes_and_data.value[box.roomID]){
      boxes_and_data.value[box.roomID].box = {
        top: box.top,
        left: box.left,
        width: box.width,
        height: box.height,
        colour: box.colour
      }
    }else {
      boxes_and_data.value[box.roomID] = <dataObject>{};
    }
  })

  Object.entries(summary.value).forEach(([roomID, environment]: [string, environmentData]) => {
    if (boxes_and_data.value[roomID]) {
      boxes_and_data.value[roomID].tracker = environment;
    }else {
      boxes_and_data.value[roomID] = <dataObject>{};
      boxes_and_data.value[roomID].tracker = environment;
    }
  });
}

// Create function to update data
const update_data = () => {
  Object.entries(summary.value).forEach(([roomID, environment]: [string, environmentData]) => {
    if (boxes_and_data.value[roomID]) {
      boxes_and_data.value[roomID].tracker = environment;
    }else {
      boxes_and_data.value[roomID] = <dataObject>{}
      boxes_and_data.value[roomID].tracker = environment;
    }
  });
}

// I need to create a function to save the object i want to v-model on save
// const save_data = async() => {
//   Object.entries(boxes_and_data.value)
// }

// New function to grab image

const handleSelectPreset = (id: number) => {
  currentPreset.value = id;
}

const setDefaultPreset = async () => {
  try {
    await axios.patch("http://localhost:5011/presets/default", {
      preset_id: currentPreset.value
    }, {
      withCredentials: true
    });
    alert("Default preset set successfully");
    await fetchPresets();
  } catch (error) {
    console.error("Error setting default preset:", error);
    alert("Failed to set default preset");
  }
};

const settable = computed(() => {
  return canCreate.value && presetList.value.default + "" !== currentPreset.value + "";
});

const deletePreset = async () => {
  try {
    await axios.delete(`http://localhost:5011/presets/${currentPreset.value}`, {
      withCredentials: true
    });
  } catch (error) {
    console.error("Error deleting preset:", error);
    alert("Failed to delete preset");
  }

  try {
    await fetchPresets();
    if (presetList.value.presets.length === 0) {
      return;
    }
    if (presetList.value?.default) {
      currentPreset.value = presetList.value.default;
    } else {
      currentPreset.value = presetList.value.presets[0].id;
    }
    await fetchPreset();
  } catch (error) {
    console.error("Error fetching presets:", error);
    alert("Failed to fetch presets");
  }
};

</script>

<template>
  <div class="airport-view-container d-flex flex-row" id="map">
    <AirportMap
      class="flex-grow-1"
      v-model="boxes_and_data"
      :presetList="presetList"
      :canCreate="canCreate"
      :settable="settable"
      :defaultPresetId="defaultPresetId"
      :currentPreset="currentPreset"
      :backgroundImage="presetImage"
      :canDelete="canDelete"
      :canEdit="canEdit"
      :presetData="presetData"
      @selectPreset="handleSelectPreset"
      @setDefault="setDefaultPreset"
      @newPreset="fetchPresets"
      @newImage="fetchPreset"
      @delete="deletePreset"
    />
    <DashBoard
      v-model="boxes_and_data"
    />
  </div>
</template>

<!-- <style scoped>
  .airport-view-container{
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }
  @media (max-width: 600px) {
  .airport-view-container{
    flex-direction: column;
  }
}
</style> -->