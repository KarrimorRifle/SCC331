<template>
  <div class="modal fade" id="imageUploadModal" tabindex="-1" aria-labelledby="imageUploadModalLabel" aria-hidden="true" @click="clearMessages">
    <div class="modal-dialog text-black">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="imageUploadModalLabel">Upload Image</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label for="imageFile" class="form-label">Choose Image</label>
            <input type="file" class="form-control" id="imageFile" ref="fileInput" @change="handleFileChange">
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
          <button type="button" class="btn btn-primary" @click="uploadImage" :disabled="loading">Upload</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineEmits } from 'vue';
import { Modal } from 'bootstrap';
import axios from 'axios';

const emit = defineEmits(["newImage"]);

const props = defineProps({
  currentPresetId: {
    type: [Number, String],
    required: true,
  }
});

const imageName = ref('');
const imageData = ref('');
const loading = ref(false);
const successMessage = ref('');
const warningMessage = ref('');
const confirmReset = ref(false);
const fileInput = ref<HTMLInputElement>(<HTMLInputElement>{});

// Function to handle image upload
const uploadImage = async () => {
  if (!imageData.value) {
    if (!confirmReset.value) {
      setTimeout(() => {
        warningMessage.value = "This will reset the image to default, are you sure?";
      }, 10);
      confirmReset.value = true;
      return;
    } else {
      warningMessage.value = "";
      confirmReset.value = false;
    }
  }
  loading.value = true;

  try {
    const response = await axios.post(`http://localhost:5011/presets/${props.currentPresetId}/image`, {
      name: imageName.value,
      data: imageData.value,
    }, {
      withCredentials: true,
    });

    if (response.status === 200) {
      warningMessage.value = "";
      imageName.value = "";
      imageData.value = "";
      fileInput.value.value = ""; // Clear the file input
      setTimeout(() => {
        successMessage.value = "Image uploaded successfully";
      }, 10);
      closeModal();
    }
    emit("newImage");
  } catch (error) {
    warningMessage.value = 'Failed to upload image';
  } finally {
    loading.value = false;
  }
};

// Function to handle file input change
const handleFileChange = (event) => {
  const file = event.target.files[0];
  const reader = new FileReader();
  reader.onload = (e) => {
    imageData.value = e.target.result.split(',')[1]; // Get base64 encoded string
    imageName.value = file.name; // Automatically set the image name to the file name
  };
  reader.readAsDataURL(file);
};

const closeModal = () => {
  const modalElement = document.getElementById("imageUploadModal");
  if (modalElement) {
    const modalInstance = Modal.getInstance(modalElement);
    if (modalInstance) {
      modalInstance.hide();
    }
  }
  document.querySelectorAll(".modal-backdrop").forEach(backdrop => backdrop.remove());
};

const clearMessages = () => {
  if (!confirmReset.value) {
    successMessage.value = "";
    warningMessage.value = "";
  }
};
</script>

<style scoped>
.modal-content {
  background-color: #f8f8ff;
}
</style>
