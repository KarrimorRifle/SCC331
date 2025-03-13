<template>
  <div>
    <ul>
      <li v-for="group in groups" :key="group.groupID">
        <!-- Editable group name -->
        <input type="text" v-model="group.groupName" />
        <!-- Update button -->
        <button @click="updateGroup(group)">Update</button>
        <!-- Delete button -->
        <button @click="deleteGroup(group)">Delete</button>
      </li>
    </ul>

    <!-- Add new group -->
    <div class="new-group">
      <input
        type="text"
        v-model="newGroupName"
        placeholder="New group name"
      />
      <button @click="addGroup">Add Group</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

// Reactive array for groups loaded from backend
const groups = ref<Array<{ groupID: number; groupName: string }>>([]);

// For creating a new group
const newGroupName = ref("");

// Fetch all tracking groups from /get/tracking/groups
const loadTrackingGroups = async () => {
  try {
    const res = await axios.get("http://localhost:5006/get/tracking/groups", {
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
      "http://localhost:5006/add/tracking/group",
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

// Update a group name via PATCH /patch/tracking/group/<groupID>
const updateGroup = async (group: { groupID: number; groupName: string }) => {
  try {
    await axios.patch(
      `http://localhost:5006/patch/tracking/group/${group.groupID}`,
      { groupName: group.groupName },
      { withCredentials: true }
    );
    alert(`Group ${group.groupID} updated!`);
  } catch (error) {
    console.error("Failed to update group:", error);
  }
};

// Delete a group via POST /delete/tracking/group/<groupID>
const deleteGroup = async (group: { groupID: number; groupName: string }) => {
  try {
    await axios.post(
      `http://localhost:5006/delete/tracking/group/${group.groupID}`,
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
  margin-right: 0.5rem;
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
