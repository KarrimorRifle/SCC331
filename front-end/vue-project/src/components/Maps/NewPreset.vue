<template>
  <div class="modal fade" id="newPresetModal" tabindex="-1" aria-labelledby="newPresetModalLabel" aria-hidden="true" @click="clearMessages">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title text-dark" id="newPresetModalLabel">Create New Preset</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body text-dark">
          <div class="mb-3">
            <label for="presetName" class="form-label">Preset Name</label>
            <input type="text" class="form-control" id="presetName" v-model="name" placeholder="Preset name">
          </div>
          <div class="mb-3">
            <label for="userEmail" class="form-label">Select Users</label>
            <input type="text" class="form-control" id="userEmail" v-model="email" placeholder="Name or Email: Case sensitive" @input="searchUsers" @keydown.down.prevent="highlightNext" @keydown.up.prevent="highlightPrev" @keydown.enter.prevent="selectHighlighted" autocomplete="off">
            <ul class="list-group mt-2" v-if="searchResults.length" style="max-height: 150px; overflow-y: auto;">
              <li class="list-group-item" v-for="(user, index) in searchResults" :key="user.uid" @click="addUser(user)" :class="{ 'active': index === highlightedIndex }" style="cursor: pointer;">
                <div>{{ user.name }}</div>
                <small :class="{ 'text-white': index === highlightedIndex, 'text-muted': index !== highlightedIndex }">{{ user.email }}</small>
              </li>
            </ul>
          </div>
          <div class="mb-3">
            <label class="form-label">Selected Users</label>
            <ul class="list-group" style="max-height: 150px; overflow-y: auto;">
              <li class="list-group-item d-flex justify-content-between align-items-center" v-for="user in selectedUsers" :key="user.uid">
                <div>
                  <div>{{ user.name }}</div>
                  <small class="text-muted">{{ user.email }}</small>
                </div>
                <button class="btn btn-danger btn-sm" @click="removeUser(user.uid)">Remove</button>
              </li>
            </ul>
          </div>
          <div v-if="loading" class="text-center">
            <div class="spinner-border" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
          <div v-if="successMessage" class="alert alert-success w-100 text-center">{{ successMessage }}</div>
          <div v-if="warningMessage" class="alert alert-danger w-100 text-center">{{ warningMessage }}</div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" :disabled="loading">Close</button>
          <button type="button" class="btn btn-success" @click="createPreset" :disabled="loading">Create</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, nextTick, watch } from "vue";
import axios from "axios";

const name = ref<string>("");
const email = ref<string>("");
const searchResults = ref<Array<{ uid: number; email: string; name: string }>>([]);
const selectedUsers = ref<Array<{ uid: number; email: string; name: string }>>([]);
const allUsers = ref<Array<{ uid: number; email: string; name: string }>>([]);
const highlightedIndex = ref<number>(-1);
const warningMessage = ref<string>("");
const loading = ref<boolean>(false);
const successMessage = ref<string>("");

const searchUsers = () => {
  if (email.value.length > 1) {
    searchResults.value = allUsers.value.filter(user => 
      (user.email.includes(email.value) || user.name.includes(email.value)) && !selectedUsers.value.some(selected => selected.uid === user.uid)
    );
    highlightedIndex.value = -1;
  } else {
    searchResults.value = [];
  }
};

const addUser = (user: { uid: number; email: string; name: string }) => {
  if (!selectedUsers.value.find(u => u.uid === user.uid)) {
    selectedUsers.value.push(user);
  }
  email.value = "";
  searchResults.value = [];
  highlightedIndex.value = -1;
};

const removeUser = (uid: number) => {
  selectedUsers.value = selectedUsers.value.filter(user => user.uid !== uid);
};

const highlightNext = async () => {
  if (highlightedIndex.value < searchResults.value.length - 1) {
    highlightedIndex.value++;
    await nextTick();
    scrollToHighlighted();
  }
};

const highlightPrev = async () => {
  if (highlightedIndex.value > 0) {
    highlightedIndex.value--;
    await nextTick();
    scrollToHighlighted();
  }
};

const selectHighlighted = () => {
  if (highlightedIndex.value >= 0 && highlightedIndex.value < searchResults.value.length) {
    addUser(searchResults.value[highlightedIndex.value]);
  }
};

const scrollToHighlighted = () => {
  const list = document.querySelector('.list-group');
  const item = list?.children[highlightedIndex.value] as HTMLElement;
  if (item) {
    item.scrollIntoView({ block: 'nearest' });
  }
};

const createPreset = async () => {
  if (!name.value.trim()) {
    warningMessage.value = "Preset name cannot be empty.";
    return;
  }
  loading.value = true;
  try {
    const trusted = selectedUsers.value.map(user => user.uid);
    const response = await axios.post('http://localhost:5011/presets', {
      name: name.value,
      trusted: trusted
    }, {
      withCredentials: true
    });
    if (response.status === 201) {
      warningMessage.value = "";
      name.value = "";
      email.value = "";
      selectedUsers.value = [];
      setTimeout(() => {
        successMessage.value = "Preset created successfully";
      }, 10);
    }
  } catch (error) {
    console.error("Error creating preset:", error);
    alert('Failed to create preset');
  } finally {
    loading.value = false;
  }
};

const clearMessages = () => {
  successMessage.value = "";
  warningMessage.value = "";
};

// Watch for changes in input values to clear messages
watch([name, email, selectedUsers], () => {
  warningMessage.value = "";
  successMessage.value = "";
});

onMounted(async () => {
  try {
    const response = await axios.get('http://localhost:5002/get_users', {
      withCredentials: true
    });
    allUsers.value = response.data.users;
  } catch (error) {
    console.error("Error fetching users:", error);
  }
});
</script>