<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue';
import axios from 'axios';

interface Message {
  message_id: number;
  sender_email: string;
  receiver_email: string;
  left_message: string;
  time_sent: string;
}

interface ChatUser {
  email: string;
  messages: Message[];
}

// State variables
const chatUsers = ref<ChatUser[]>([]);
const selectedUser = ref<string | null>(null);
const messages = ref<Message[]>([]);
const messagesContainer = ref<HTMLElement | null>(null);
const sessionId = document.cookie
  .split('; ')
  .find(row => row.startsWith('session_id='))
  ?.split('=')[1] || '';

// **1️⃣ Fetch all messages to populate the chat list**
const fetchAllMessages = async () => {
  try {
    const response = await axios.get('http://localhost:5007/get_messages', {
      headers: { 'session-id': sessionId },
      withCredentials: true
    });

    if (response.data.messages) {
      const allMessages: Message[] = response.data.messages;
      processChatUsers(allMessages);
    }
  } catch (error) {
    console.error('Error fetching messages:', error);
  }
};

// **2️⃣ Process messages to create a unique user list**
const processChatUsers = (allMessages: Message[]) => {
  const userMap = new Map<string, Message[]>();

  allMessages.forEach((msg) => {
    const otherUser = msg.sender_email === sessionId ? msg.receiver_email : msg.sender_email;
    
    if (!userMap.has(otherUser)) {
      userMap.set(otherUser, []);
    }
    userMap.get(otherUser)?.push(msg);
  });

  chatUsers.value = Array.from(userMap, ([email, messages]) => ({ email, messages }));
};

// **3️⃣ Fetch messages for a selected user**
const fetchChatMessages = async () => {
  if (!selectedUser.value) return;

  try {
    const response = await axios.get(`http://localhost:5007/get_chat_messages?user_email=${selectedUser.value}`, {
      headers: { 'session-id': sessionId },
      withCredentials: true
    });

    if (response.data.messages) {
      messages.value = response.data.messages;
    }
  } catch (error) {
    console.error('Error fetching messages:', error);
  } finally {
    scrollToBottom();
  }
};

// **4️⃣ Select a user and fetch messages**
const selectUser = (email: string) => {
  selectedUser.value = email;
  messages.value = [];
  fetchChatMessages();
};

// **5️⃣ Scroll to the bottom when messages update**
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

// **6️⃣ Watch for new messages and scroll down**
watch(() => messages.value, scrollToBottom, { deep: true });

// **7️⃣ Fetch all messages when the component mounts**
onMounted(() => {
  fetchAllMessages();
});
</script>


<template>
  <div class="messages-container">
    <!-- Sidebar with User List -->
    <div class="sidebar">
      <h2>Chats</h2>
      <ul v-if="chatUsers.length > 0">
        <li 
          v-for="user in chatUsers" 
          :key="user.email" 
          @click="selectUser(user.email)"
          :class="{ active: selectedUser === user.email }"
        >
          {{ user.email }}
        </li>
      </ul>
      <p v-else>No messages yet.</p>
    </div>

    <!-- Main Chat Panel -->
    <div class="chat-panel">
      <div v-if="selectedUser" class="chat-box">
        <h2>Chat with {{ selectedUser }}</h2>
        <div class="messages" ref="messagesContainer">
          <div 
            v-for="message in messages" 
            :key="message.message_id"
            class="message"
            :class="{ 'sent': message.sender_email !== selectedUser, 'received': message.sender_email === selectedUser }"
          >
            <p class="message-text">{{ message.left_message }}</p>
            <span class="message-time">{{ new Date(message.time_sent).toLocaleTimeString() }}</span>
          </div>
        </div>
      </div>
      <div v-else class="no-chat-selected">
        <p>Select a chat to view messages</p>
      </div>
    </div>
  </div>
</template>


<style scoped>
.messages-container {
  display: flex;
  height: 100vh;
  background: #f9f9f9;
}

/* Sidebar */
.sidebar {
  width: 30%;
  background: white;
  padding: 20px;
  border-right: 1px solid #ddd;
  overflow-y: auto;
}

.sidebar h2 {
  font-size: 1.5rem;
  margin-bottom: 15px;
}

.sidebar ul {
  list-style: none;
  padding: 0;
}

.sidebar li {
  padding: 10px;
  cursor: pointer;
  border-radius: 5px;
  transition: background 0.3s;
}

.sidebar li:hover, .sidebar .active {
  background: #007bff;
  color: white;
}

/* Chat Panel */
.chat-panel {
  width: 70%;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-box {
  width: 100%;
  max-width: 600px;
  background: white;
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  height: 80vh;
}

/* Chat Messages */
.messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: #f1f1f1;
  border-radius: 8px;
  height: 100%;
}

/* Message Styles */
.message {
  max-width: 70%;
  padding: 10px 15px;
  border-radius: 20px;
  font-size: 1rem;
  position: relative;
  word-wrap: break-word;
}

.sent {
  align-self: flex-end;
  background: #007bff;
  color: white;
}

.received {
  align-self: flex-start;
  background: #e4e6eb;
  color: black;
}

/* Message Timestamp */
.message-time {
  font-size: 0.75rem;
  color: gray;
  display: block;
  margin-top: 5px;
}
</style>
