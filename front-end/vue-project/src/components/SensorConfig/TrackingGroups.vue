<template>
  <div>
    <ul>
      <li v-for="group in groups" :key="group.groupID">
        <input type="text" v-model="group.groupName" />
        <button @click="updateGroup(group)">Update</button>
        <button @click="deleteGroup(group)">Delete</button>
      </li>
    </ul>
    <div class="new-group">
      <input type="text" v-model="newGroupName" placeholder="New group name" />
      <button @click="addGroup">Add Group</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

// Dummy tracking groups data (simulate GET /get/tracking/groups)
const groups = ref([
  { groupID: 1, groupName: 'Group A' },
  { groupID: 2, groupName: 'Group B' },
]);

const newGroupName = ref("");

const addGroup = () => {
  if (newGroupName.value.trim() === "") return;
  // Simulate POST /add/tracking/group
  const newGroup = { groupID: Date.now(), groupName: newGroupName.value.trim() };
  groups.value.push(newGroup);
  newGroupName.value = "";
  alert("Tracking group added (dummy)");
};

const updateGroup = (group: any) => {
  // Simulate PATCH /patch/tracking/group/<groupID>
  console.log("Updating group:", group);
  alert(`Group ${group.groupID} updated (dummy)`);
};

const deleteGroup = (group: any) => {
  // Simulate DELETE /delete/tracking/group/<groupID>
  groups.value = groups.value.filter(g => g.groupID !== group.groupID);
  alert(`Group ${group.groupID} deleted (dummy)`);
};
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
.new-group input[type="text"] {
  margin-right: 0.5rem;
}
button {
  padding: 0.3rem 0.5rem;
}
</style>
