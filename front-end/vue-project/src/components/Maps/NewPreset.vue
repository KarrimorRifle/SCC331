<template>
  <div class="modal fade" id="newPresetModal" tabindex="-1" aria-labelledby="newPresetModalLabel" aria-hidden="true" @click="clearMessages">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title text-dark" id="newPresetModalLabel">{{ updateMode ? 'Update Preset' : 'Create New Preset' }}</h5>
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
          <button type="button" class="btn btn-success" @click="createPreset" :disabled="loading">{{ updateMode ? 'Update' : 'Create' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, nextTick, watch, defineEmits, defineProps, warn } from "vue";
import axios from "axios";
import type { preset, presetListType } from "@/utils/mapTypes";
import { Modal } from "bootstrap";
const emit = defineEmits(["newPreset"]);

const props = defineProps({
  presetData: {
    type: Object as () => preset,
    required: true
  },
  updateMode: {
    type: Boolean,
    required: true
  },
  presetList: {
    type: Object as () => presetListType,
    required: true,
  },
});

const updateMode = ref(props.updateMode);
watch([() => props.updateMode, () => props.presetData], ([newUpdateMode, newPresetData]) => {
  if (newUpdateMode === true) {
    name.value = newPresetData.name;
    selectedUsers.value = newPresetData.trusted.map(uid => {
      return allUsers.value.find(user => user.uid === uid);
    }).filter(user => user !== undefined) as Array<{ uid: number; email: string; name: string }>;
  } else {
    name.value = "";
    selectedUsers.value = [];
  }
  updateMode.value = newUpdateMode;
});

const name = ref<string>("");
const email = ref<string>("");
const searchResults = ref<Array<{ uid: number; email: string; name: string }>>([]);
const selectedUsers = ref<Array<{ uid: number; email: string; name: string }>>([]);
const allUsers = ref<Array<{ uid: number; email: string; name: string }>>([]);
const highlightedIndex = ref<number>(-1);
const warningMessage = ref<string>("");
const loading = ref<boolean>(false);
const successMessage = ref<string>("");
const currentUser = ref<{ uid: number; email: string; name: string } | null>(null);

const setWarning = (input: string) => {
  successMessage.value = "";
  setTimeout(() => {
    warningMessage.value = input;
  }, 10)
}

const setSuccess = (input: string) => {
  warningMessage.value = "";
  setTimeout(() => {
    successMessage.value = input;
  }, 10)
}

const searchUsers = () => {
  if (email.value.trim().length > 0) {
    const query = email.value.trim().toLowerCase();
    searchResults.value = allUsers.value.filter(user => {
      const userEmail = user.email.toLowerCase();
      const userName = user.name.toLowerCase();

      const matchesQuery = userEmail.includes(query) || userName.includes(query);
      const isNotSelected = !selectedUsers.value.some(selected => selected.uid === user.uid);
      const isNotCurrentUser = currentUser.value?.uid != user.uid;

      return matchesQuery && isNotSelected && isNotCurrentUser;
    });

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
    setWarning("Preset name cannot be empty.");
    return;
  }

  if (name.value.trim() == "\"No presets found!\"") {
    setWarning("Invalid preset name.");
    return;
  }

  if (props.presetList?.presets?.some(object =>
    object.name == name.value
  )) {
    setWarning("Name already in use.");
    return;
  }

  loading.value = true;
  try {
    const trusted = selectedUsers.value.map(user => user.uid);
    let response;
    if(updateMode.value){
      response = await axios.patch(`/api/editor/presets/${props.presetData.id}`, {
        name: name.value,
        trusted: trusted
      }, {
        withCredentials: true
      });
    } else {
      response = await axios.post('/api/editor/presets', {
        name: name.value,
        trusted: trusted
      }, {
        withCredentials: true
      });
    }
    if (response.status === 201){
      name.value = "";
      email.value = "";
      selectedUsers.value = [];
    }

    if (response.status === 201 || response.status === 200) {
      setSuccess(`Preset ${response.status == 201 ? 'created' : 'updated'} successfully`);
      closeModal();
    } else {
      setWarning(`ERR ${response.status}: something went wrong please try again later`);
    }
    emit("newPreset");
  } catch (error) {
    console.error("Error creating preset:", error);
    alert("Failed to create preset");
  } finally {
    loading.value = false;
  }
};

const closeModal = () => {
  const modalElement = document.getElementById("newPresetModal");
  if (modalElement) {
    const modalInstance = Modal.getInstance(modalElement); // Use Modal from Bootstrap
    if (modalInstance) {
      modalInstance.hide();
    }
  }
  document.querySelectorAll(".modal-backdrop").forEach(backdrop => backdrop.remove());
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
    const response = await axios.get('/api/login/get_users', {
      withCredentials: true
    });
    allUsers.value = response.data.users;
    const currentUserResponse = await axios.get('/api/login/validate_cookie', {
      withCredentials: true
    });
    currentUser.value = currentUserResponse.data;
  } catch (error) {
    console.error("Error fetching users or current user:", error);
  }
});
</script>
