import { defineStore } from "pinia";
import {onMounted, onUnmounted, ref, watch, computed }from "vue"
import axios from "axios";
import { addNotification } from "@/stores/notificationStore";
import type { Timeout } from "node:timers";
import type { presetListType, preset, summaryType, boxAndData, boxType, dataObject, environmentData } from "../utils/mapTypes";

export const usePresetStore = defineStore("presetStore", () => {
    const overlayAreasConstant = ref<any[]>([]);
    let updateOverlayAreasCallback: (data: any) => void = () => {};
    let updateOverlayAreaColorCallback: (data: any) => void = () => {};

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
    let boxes_and_data = ref<boxAndData>(<boxAndData>{});
    let editMode = ref<boolean>(false);
    const isLoading = ref(true);
    const settable = computed(() => {
      return canCreate.value && presetList.value.default + "" !== currentPreset.value + "";
    });
    let fetchSummaryRetry:number = 3;
    
    function setOverlayAreasConstant(data: any) {
        overlayAreasConstant.value = data;
    }
    function setUpdateOverlayAreasCallback(callback: (data: any) => void) {
      updateOverlayAreasCallback = callback;
    }

    function setUpdateOverlayAreaColorCallback(callback: (data: any) => void) {
      updateOverlayAreaColorCallback = callback;
  }

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
        addNotification({
          Title: "Validation Error",
          Severity: "system",
          Summary: "Unable to validate user, server may be down, try again later."
        });
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
    
    const fetchSummary = async() => {
      if (fetchSummaryRetry == 0){
        if (pollingInterval) clearInterval(pollingInterval);
        addNotification({
          Title: "Fetch Error",
          Severity: "system",
          Summary: "Unable to fetch summary data, server may be down, try again later."
        });
        return;
      }
      try {
        let request = await axios.get("http://localhost:5003/summary", { withCredentials: true });
        summary.value = request.data;
        fetchSummaryRetry = 3;
      } catch (error) {
        fetchSummaryRetry--;
        console.error("Error fetching summary:", error);
      }
    }
    
    const fetchPresets = async() => {
      try {
        isLoading.value = true;
        let request = await axios.get("http://localhost:5010/presets", { withCredentials: true });
        presetList.value = request.data;
        // Set the default preset ID
        defaultPresetId.value = presetList.value.default;
        if(currentPreset.value == -1 && presetList.value.presets.length > 0)
          currentPreset.value = presetList.value.presets[0].id;
      } catch (error) {
        console.error("Error fetching presets:", error);
        addNotification({
          Title: "Fetch Error",
          Severity: "system",
          Summary: "Unable to fetch presets, server may be down, try again later."
        });
      } finally {
        isLoading.value = false;
      }
    }
    
    const fetchPreset = async() => {
      try {
        isLoading.value = true;
        let request = await axios.get(`http://localhost:5010/presets/${currentPreset.value}`, { withCredentials: true });
        //console.log(request.data);
        presetData.value = request.data;
        processPresetImage();
      } catch (error) {
        console.error("Error fetching preset:", error);
        addNotification({
          Title: "Fetch Error",
          Severity: "system",
          Summary: "Unable to fetch preset data, server may be down, try again later."
        });
      }finally{
        isLoading.value = false;
      }
    }
    
    const create_data = () => {
      boxes_and_data.value = {};
      // Add box data per room
      presetData.value.boxes?.forEach((box: boxType) => {
        if(boxes_and_data.value[box.roomID]){
          boxes_and_data.value[box.roomID].box = {
            top: box.top,
            left: box.left,
            width: box.width,
            height: box.height,
            colour: box.colour
          };
          boxes_and_data.value[box.roomID].label = box.label;
        }else {
          boxes_and_data.value[box.roomID] = <dataObject>{};
          boxes_and_data.value[box.roomID].box = {
            top: box.top,
            left: box.left,
            width: box.width,
            height: box.height,
            colour: box.colour
          }
          boxes_and_data.value[box.roomID].label = box.label;
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
    
      //console.log("boxes and data", boxes_and_data.value)
    }
    
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
    
        if (presetData.value.boxes) {
          console.log("Updating overlay areas with preset colors...");
  
          console.log(overlayAreasConstant);
          // Update overlayAreasConstant with new colors from the preset
          const updatedOverlayAreas = overlayAreasConstant.value.map(area => {
            const matchingBox = presetData.value.boxes.find(box => box.roomID === area.label.replace("Area ", ""));
            return matchingBox ? { ...area, color: matchingBox.colour } : area;
          });
    
          console.log("Updated overlayAreasConstant:", updatedOverlayAreas);
    
          // Emit event to App.vue to update global state & localStorage
          if (typeof updateOverlayAreasCallback === "function") {
            updateOverlayAreasCallback(updatedOverlayAreas);
          }
        }
    
      } catch (error) {
        console.error("Error setting default preset:", error);
        alert("Failed to set default preset");
        addNotification({
          Title: "Set Default Error",
          Severity: "system",
          Summary: "Unable to set default preset, server may be down, try again later."
        });
      }
    };
    
    const deletePreset = async () => {
      if(presetList.value.default == currentPreset.value){
        alert("Cannot delete default preset");
        return;
      }
    
      try {
        await axios.delete(`http://localhost:5011/presets/${currentPreset.value}`, {
          withCredentials: true
        });
      } catch (error) {
        console.error("Error deleting preset:", error);
        alert("Failed to delete preset");
        addNotification({
          Title: "Delete Error",
          Severity: "system",
          Summary: "Unable to delete preset, server may be down, try again later."
        });
      }
    
      try {
        currentPreset.value = -1;
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
        addNotification({
          Title: "Fetch Error",
          Severity: "system",
          Summary: "Unable to fetch presets, server may be down, try again later."
        });
      }
    };
    
    const createNewBox = (roomID: number | string) => {
      const randomColor = '#' + Math.floor(Math.random() * 16777215).toString(16);
      boxes_and_data.value[roomID].box = {
        top: 10,
        left: 10,
        width: 100,
        height: 100,
        colour: randomColor,
      };
      if (typeof updateOverlayAreaColorCallback === "function") {
        updateOverlayAreaColorCallback({ roomID, colour: randomColor });
      }
    }
    
    const changeBoxColour =  (roomID: number | string, colour: string) => {
      if(boxes_and_data.value[roomID].box)
        boxes_and_data.value[roomID].box.colour = colour;
    }
    
    const removeBox = (roomID: number | string) => {
      boxes_and_data.value[roomID].box = null;
    }
    
    const uploadBoxes = async () => {
      const boxesToUpload = Object.entries(boxes_and_data.value)
        .filter(([_, data]) => data.box) // Filter out entries where data.box does not exist
        .map(([roomID, data]) => ({
          roomID: roomID,
          ...data.box,
          label: data.label || ""
        }));
    
      // Validation check
      for (const box of boxesToUpload) {
        console.log(box.label.trim().length);
        if (!box.label || box.label.trim().length === 0) {
          alert('Cannot save. All boxes must have a label.');
          return;
        }
      }
    
      console.log("Uploading boxes:", boxesToUpload); // Log the boxes being uploaded
    
      try {
        await axios.patch(`http://localhost:5011/presets/${currentPreset.value}/boxes`, {
          boxes: boxesToUpload
        }, {
          withCredentials: true
        });
        alert("Boxes uploaded successfully");
        editMode.value = false;
      } catch (error) {
        console.error("Error uploading boxes:", error);
        alert("Failed to upload boxes");
        addNotification({
          Title: "Upload Error",
          Severity: "system",
          Summary: "Unable to upload boxes, server may be down, try again later."
        });
      }
      editMode.value = false;
    };
    
    const cancelBoxEdit = () => {
      fetchPreset();
      create_data();
      editMode.value = false;
    }

    const reloadPresets = async () => {
      try {
        await fetchPresets(); // Fetch the updated list of presets
        if (presetList.value.presets.length > 0) {
          // Ensure current preset is valid
          if (!presetList.value.presets.some(p => p.id === currentPreset.value)) {
            currentPreset.value = presetList.value.default || presetList.value.presets[0].id;
          }
        }
        await fetchPreset();
      } catch (error) {
        console.error("Error reloading presets:", error);
      }
    };
    
    const updateOverlayAreaColor = (roomID: string, newColor: string) => {
      const area = overlayAreasConstant.value.find(area => area.label === `Area ${roomID}`);
      if (area) {
        area.color = newColor; 
      }
    };
    
    const handleColourChange = (roomID: string, newColor: string) => {
      console.log(`Colour change detected for Area ${roomID}: ${newColor}`);
    
      // Update box color logic
      changeBoxColour(roomID, newColor);
    
      console.log("current preset: ", currentPreset.value);
      console.log("default preset: ", defaultPresetId.value);
    
      if (currentPreset.value == defaultPresetId.value) {
        // Update overlay areas constant (this is to updates globally);
        updateOverlayAreaColor(roomID, newColor);
        if (typeof updateOverlayAreaColorCallback === "function") {
          updateOverlayAreaColorCallback({ roomID, colour: newColor });
        }
      }else{
        console.log("doesn't match");
    
      }
    };
    
    watch(currentPreset, async () => {
      console.log("Preset changed to: ", currentPreset.value);
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
          await setDefaultPreset();
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
    
    return {
        isLoading,
        presetList,
        presetData,
        defaultPresetId,
        currentPreset,
        presetImage,
        boxes_and_data,
        summary,
        canEdit,
        canCreate,
        canDelete,
        settable,
        editMode, 
        reloadPresets,
        fetchPresets,
        fetchPreset,
        processPresetImage,
        create_data,
        createNewBox, 
        removeBox, 
        uploadBoxes, 
        cancelBoxEdit, 
        handleColourChange,
        setDefaultPreset,
        deletePreset,
        handleSelectPreset, 
        setOverlayAreasConstant,
        setUpdateOverlayAreasCallback,
        setUpdateOverlayAreaColorCallback,
    };
});
