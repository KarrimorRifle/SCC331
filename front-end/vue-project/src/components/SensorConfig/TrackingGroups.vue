<template>
  <div>
    <!-- Add new group -->
    <div class="d-flex">
        <div class="new-group input-group mt-0 me-2" style="max-width: 20rem;">
          <input
            type="text"
            v-model="newGroupName"
            placeholder="Group name"
            class="form-control border"
          />
          <button @click="addGroup" class="input-group-text btn btn-success">Add Group</button>
        </div>
      <button @click="updateAllGroups" class="btn btn-primary d-inline block">Update</button>
      <button @click="cancelUpdate" class="btn btn-secondary d-inline block ms-1">Cancel</button>
    </div>
    <ul>
      <li
        v-for="group in groups"
        :key="group.groupID"
        class="new-group input-group mb-3"
        style="max-width: 30rem;"
      >
        <!-- Editable group name with change detection -->
        <input type="text" v-model="group.groupName" @input="markDirty(group)" class="form-control me-4 rounded"/>
        <!-- Delete button -->
        <button class="btn btn-danger rounded" @click="deleteGroup(group)">
          <font-awesome-icon :icon="faTrash" />
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faTrash } from '@fortawesome/free-solid-svg-icons';

// Reactive array for groups loaded from backend, now with an optional dirty flag.
const groups = ref<Array<{ groupID: number; groupName: string; dirty?: boolean }>>([]);

// For creating a new group
const newGroupName = ref("");

// Fetch all tracking groups from /get/tracking/groups
const loadTrackingGroups = async () => {
  try {
    const res = await axios.get("/api/hardware/get/tracking/groups", {
      withCredentials: true, // important for sending session_id cookie
    });
    groups.value = res.data.groups; // e.g. [{ groupID: 1, groupName: "Group A" }, ...]
  } catch (error) {
    console.error("Failed to load tracking groups:", error);
  }
};

// Add a new group via POST /add/tracking/group
const addGroup = async () => {
  const trimmedName = newGroupName.value.trim();
  if (!trimmedName) return; // skip empty
  try {
    // POST { groupName: "xxx" }
    const res = await axios.post(
      "/api/hardware/add/tracking/group",
      { groupName: trimmedName },
      { withCredentials: true }
    );
    // The server returns { "message" : "success", "groupID" : new_id }
    const newID = res.data.groupID;
    // Add to our local array
    groups.value.push({ groupID: newID, groupName: trimmedName });
    // Clear input
    newGroupName.value = "";
  } catch (error) {
    console.error("Failed to add group:", error);
  }
};

// Mark group as modified
const markDirty = (group: { groupID: number; groupName: string; dirty?: boolean }) => {
  group.dirty = true;
};

// Global update for all modified groups
const updateAllGroups = async () => {
  const dirtyGroups = groups.value.filter((group) => group.dirty);
  for (const group of dirtyGroups) {
    try {
      await axios.patch(
        `/api/hardware/patch/tracking/group/${group.groupID}`,
        { groupName: group.groupName },
        { withCredentials: true }
      );
      group.dirty = false;
    } catch (error) {
      console.error("Failed to update group:", error);
    }
  }
};

// New cancelUpdate function to revert unsaved changes by reloading groups
const cancelUpdate = async () => {
  await loadTrackingGroups();
};

// Delete a group via POST /delete/tracking/group/<groupID>
const deleteGroup = async (group: { groupID: number; groupName: string }) => {
  try {
    await axios.post(
      `/api/hardware/delete/tracking/group/${group.groupID}`,
      {},
      { withCredentials: true }
    );
    // Remove it locally
    groups.value = groups.value.filter((g) => g.groupID !== group.groupID);
    alert(`Group ${group.groupID} deleted!`);
  } catch (error) {
    console.error("Failed to delete group:", error);
  }
};

// Load groups on mount
onMounted(() => {
  loadTrackingGroups();
});
</script>

<style scoped>
ul {
  list-style: none;
  padding: 0;
  margin-bottom: 1rem;
}

li {
  margin-bottom: 0.5rem;
}

input[type="text"] {
  padding: 0.25rem;
}

.new-group {
  margin-top: 1rem;
}

button {
  margin-right: 0.5rem;
  padding: 0.3rem 0.5rem;
  cursor: pointer;
}
</style>
