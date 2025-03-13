import { ref } from "vue";
import axios from "axios";

const API_BASE_URL = "/api/warning"; // Ensure the correct backend URL

// Warning Store State
export const warningsList = ref<any[]>([]);
export const selectedWarningId = ref<number | null>(null);
export const selectedWarning = ref<any>(null);
export const newWarningName = ref<string>("");
export const warningConditions = ref<Record<string, any>>({});
export const fullWarningConditions = ref<Record<string, any>>({});

export const warningMessages = ref<any[]>([]);
export const isRoomSelectionVisible = ref(false);
export const activeSection = ref("warnings");

// **Fetch All Warnings from Backend**
export const fetchWarnings = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/warnings`, { withCredentials: true });
    warningsList.value = response.data;
  } catch (error) {
    console.error("Error fetching warnings:", error);
  }
};

// **Fetch a Specific Warning**
export const fetchWarningById = async (warningId: number) => {
  if (selectedWarningId.value === warningId) {
    resetWarningSelection();
    return;
  }
  try {
    const response = await axios.get(`${API_BASE_URL}/warnings/${warningId}`, { withCredentials: true });
    selectedWarningId.value = response.data.id;
    selectedWarning.value = response.data;

    warningConditions.value = response.data.conditions.reduce((acc, item) => {
      acc[item.roomID] = {
        conditions: [...item.conditions],
        messages: response.data.messages.filter(msg => msg.Location === item.roomID),
      };
      return acc;
    }, {});

    isRoomSelectionVisible.value = true;
    activeSection.value = "rooms";
  } catch (error) {
    console.error("Error fetching warning details:", error);
  }
};

export const fetchFullWarningConditions = async () => {
  fullWarningConditions.value = {};

  for (const warning of warningsList.value) {
    const warningId = warning.id;
    if (warningId) {
      await fetchWarningById(warningId);
      fullWarningConditions.value[warningId] = {
        name: selectedWarning.value?.name,
        conditions: selectedWarning.value?.conditions || [],
        messages: selectedWarning.value?.messages || [],
      };
    }
  }
};

// **Create a New Warning**
export const createWarning = async () => {
  if (!newWarningName.value.trim()) {
    alert("Warning name is required.");
    return;
  }

  const payload = { name: newWarningName.value };

  try {
    await axios.post(`${API_BASE_URL}/warnings`, payload, { withCredentials: true });
    await fetchWarnings();
  } catch (error) {
    console.error("Error creating warning:", error);
  }
};

// **Update an Existing Warning**
export const updateWarning = async () => {
  if (!selectedWarningId.value) {
    console.error("No warning selected for update.");
    return;
  }

  const formattedConditions = Object.entries(warningConditions.value).reduce((acc, [roomID, data]) => {
    const validConditions = data.conditions.filter(
      cond => cond.variable !== null && cond.lower_bound !== null && cond.upper_bound !== null
    );

    if (validConditions.length > 0) {
      const uniqueConditions = validConditions.reduce((unique, cond) => {
        if (!unique.some(existing => existing.variable === cond.variable)) {
          unique.push(cond);
        }
        return unique;
      }, []);

      acc.push({
        roomID,
        conditions: uniqueConditions.map(cond => ({
          variable: cond.variable,
          lower_bound: cond.lower_bound,
          upper_bound: cond.upper_bound,
        })),
      });
    }

    return acc;
  }, []);

  const formattedMessages = [];
  Object.entries(warningConditions.value).forEach(([roomID, data]) => {
    const seenTitles = new Set();

    data.messages.forEach(msg => {
      if (!msg.Summary || msg.Summary.trim() === "") return;
      const normalizedTitle = msg.Title ? msg.Title.trim().toLowerCase() : "untitled";

      if (!seenTitles.has(normalizedTitle) || normalizedTitle !== "untitled") {
        seenTitles.add(normalizedTitle);
        formattedMessages.push({
          Authority: msg.Authority || "users",
          Title: msg.Title,
          Location: msg.Location || roomID,
          Severity: msg.Severity || "notification",
          Summary: msg.Summary,
        });
      }
    });
  });

  const payload = {
    name: selectedWarning.value?.name || `Updated Warning ${selectedWarningId.value}`,
    id: selectedWarningId.value,
    conditions: formattedConditions,
    messages: formattedMessages,
  };

  try {
    await axios.patch(`${API_BASE_URL}/warnings/${selectedWarningId.value}`, payload, { withCredentials: true });
    await fetchWarnings();
  } catch (error) {
    console.error("Error updating warning:", error);
  }
};

// **Delete a Warning**
export const deleteWarning = async (warningId: number) => {
  try {
    await axios.delete(`${API_BASE_URL}/warnings/${warningId}`, { withCredentials: true });
    warningsList.value = warningsList.value.filter(w => w.id !== warningId);
  } catch (error) {
    console.error("Error deleting warning:", error);
  }
};

// **Reset Warning Selection**
export const resetWarningSelection = () => {
  selectedWarningId.value = null;
  selectedWarning.value = null;
  warningConditions.value = {};
  isRoomSelectionVisible.value = false;
};
