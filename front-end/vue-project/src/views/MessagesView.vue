<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faTimes } from '@fortawesome/free-solid-svg-icons';

const messages = ref<{ message_id: number; sender_email: string; left_message: string; time_sent: string }[]>([]);
const loading = ref(true);
const errorMessage = ref<string | null>(null);

// Fetch all messages for the user
const fetchMessages = async () => {
  try {
    const response = await axios.get('http://localhost:5007/get_messages', {
      headers: {
        'session-id': document.cookie.split('; ').find(row => row.startsWith('session_id='))?.split('=')[1] || ''
      },
      withCredentials: true // Ensures cookies are sent with the request
    });

    if (response.data.messages) {
      messages.value = response.data.messages;
    } else {
      errorMessage.value = 'No messages available.';
    }
  } catch (error) {
    console.error('Error fetching messages:', error.response?.data || error.message);
    errorMessage.value = 'Failed to load messages. Please try again later.';
  } finally {
    loading.value = false;
  }
};

// Fetch messages when the component is mounted
onMounted(() => {
  fetchMessages();
});
</script>

<template>
  <div class="messages-page">
    <h1>All Messages</h1>

    <div v-if="loading" class="loading">
      <p>Loading your messages...</p>
    </div>

    <div v-if="errorMessage" class="error-message">
      <p>{{ errorMessage }}</p>
    </div>

    <div v-if="messages.length > 0" class="messages-list">
      <ul>
        <li v-for="message in messages" :key="message.message_id" class="message-item">
          <div class="message-header">
            <strong>{{ message.sender_email }}</strong>
            <span class="message-time">{{ new Date(message.time_sent).toLocaleString() }}</span>
          </div>
          <div class="message-content">
            <p>{{ message.left_message }}</p>
          </div>
        </li>
      </ul>
    </div>

    <div v-else-if="!loading" class="no-messages">
      <p>No messages to display.</p>
    </div>
  </div>
</template>

<style scoped>
.messages-page {
  padding: 2rem;
  background-color: #f5f5f5;
  color: #333;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 1.5rem;
}

.loading,
.error-message,
.no-messages {
  text-align: center;
  font-size: 1.2rem;
}

.messages-list {
  list-style: none;
  padding: 0;
}

.message-item {
  background-color: white;
  padding: 1.5rem;
  margin: 1rem 0;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.message-header {
  display: flex;
  justify-content: space-between;
  font-weight: bold;
}

.message-time {
  font-size: 0.9rem;
  color: #888;
}

.message-content {
  margin-top: 0.5rem;
  font-size: 1rem;
}

.message-content p {
  margin: 0;
}

/* Error and loading state */
.error-message,
.loading {
  color: #ff4d4d;
  font-weight: bold;
}

/* No messages state */
.no-messages {
  color: #777;
}
</style>
