<script setup lang="ts">
import { ref, onMounted, watch, nextTick, onBeforeUnmount } from 'vue';
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
  unreadCount: number;
}

const chatUsers = ref<ChatUser[]>([]);
const selectedUser = ref<string | null>(null);
const messages = ref<Message[]>([]);
const newMessage = ref(''); 
const messagesContainer = ref<HTMLElement | null>(null);
const sessionId = document.cookie
  .split('; ')
  .find(row => row.startsWith('session_id='))
  ?.split('=')[1] || '';
const allUsers = ref<string[]>([]);
const showNewChat = ref(false);
const newChatUser = ref<string | null>(null);

// This user's email, used for hiding the 'ghost chat' between the user and themselves
const fetchUserEmail = async () => {
  try {
    const response = await axios.get('http://localhost:5007/get_user_email', {
      headers: { 'session-id': sessionId },
      withCredentials: true
    });

    if (response.data.email) {
      return response.data.email;
    }
  } catch (error) {
    console.error('Error fetching user email:', error);
  }
  return null;
};

// Fetches all of the messages in the database that involve this user, and displays them on the chat list
const fetchAllMessages = async () => {
  const userEmail = await fetchUserEmail();
  if (!userEmail) return;

  try {
    const response = await axios.get('http://localhost:5007/get_messages', {
      headers: { 'session-id': sessionId },
      withCredentials: true
    });

    if (response.data.messages) {
      const allMessages: Message[] = response.data.messages;
      const unreadCounts = response.data.unreadCounts || {};
      processChatUsers(allMessages, unreadCounts, userEmail);
    }
  } catch (error) {
    console.error('Error fetching messages:', error);
  }
};

// Helper function to remove this user from the chatlist
const processChatUsers = (allMessages: Message[], unreadCounts: Record<string, number>, userEmail: string) => {
  const userMap = new Map<string, Message[]>();

  allMessages.forEach((msg) => {
    const otherUser = msg.sender_email === userEmail ? msg.receiver_email : msg.sender_email;

    if (!userMap.has(otherUser)) {
      userMap.set(otherUser, []);
    }
    userMap.get(otherUser)?.push(msg);
  });

  // Add unread message count to the user object 
  chatUsers.value = Array.from(userMap, ([email, messages]) => ({
    email,
    messages,
    unreadCount: unreadCounts[email] || 0 // Add unread count if exists
  }));
};

// Fetch the messages from the chat that is open
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

// Select the user from the message bar
const selectUser = (email: string) => {
  selectedUser.value = email;
  messages.value = [];
  fetchChatMessages();
};

// Scroll to the latest message if needed
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

// Watch for if it is necessary to scroll down
watch(() => messages.value, scrollToBottom, { deep: true });

// Fetch all messages and users when the component mounts
onMounted(() => {
  fetchAllMessages();
  fetchAllUsers();
  const intervalId = setInterval(() => {
    fetchAllMessages();
    if (selectedUser.value) {
      fetchChatMessages();
    }
  }, 5000); // Refresh every 5 seconds

  // Clean up the interval when the component is unmounted
  onBeforeUnmount(() => {
    clearInterval(intervalId);
  });
});

// Fetch all of the users except this one to make a new chat
const fetchAllUsers = async () => {
  try {
    const response = await axios.get('http://localhost:5007/get_users_messages_page', {
      headers: { 'session-id': sessionId },
      withCredentials: true
    });

    if (response.data.users) {
      allUsers.value = response.data.users.map((user: { email: string }) => user.email);
    }
  } catch (error) {
    console.error('Error fetching users:', error);
  }
};

// Start a new chat
const startNewChat = () => {
  if (!newChatUser.value) return;
  
  selectedUser.value = newChatUser.value;
  messages.value = [];
  showNewChat.value = false;
  fetchChatMessages();
};

// Send a message
const sendMessage = async () => {
  if (!newMessage.value.trim() || !selectedUser.value) return;

  try {
    await axios.post('http://localhost:5007/send_message', {
      receiver_email: selectedUser.value,
      message: newMessage.value
    }, {
      headers: { 'session-id': sessionId },
      withCredentials: true
    });

    // Add message to local state
    messages.value.push({
      message_id: Date.now(),
      sender_email: sessionId,
      receiver_email: selectedUser.value,
      left_message: newMessage.value,
      time_sent: new Date().toISOString()
    });

    newMessage.value = '';
    scrollToBottom();

    // Refresh chat user list to update sidebar
    fetchAllMessages();
    fetchAllUsers();
  } catch (error) {
    console.error('Error sending message:', error);
  }
};
</script>

<template>
  <div class="messages-container">
    <!-- Sidebar with User List -->
    <div class="sidebar">
      <h2>Chats</h2>
      
      <button @click="showNewChat = !showNewChat" class="new-chat-btn">New Chat</button>
      
      <!-- Dropdown for Selecting New Chat -->
      <div v-if="showNewChat" class="new-chat-dropdown">
        <select v-model="newChatUser">
          <option v-for="user in allUsers" :key="user" :value="user">
            {{ user }}
          </option>
        </select>
        <button @click="startNewChat">Start</button>
      </div>

      <ul v-if="chatUsers.length > 0">
        <li 
          v-for="user in chatUsers" 
          :key="user.email" 
          @click="selectUser(user.email)"
          :class="{ active: selectedUser === user.email }"
        >
          <div class="user-info">
            <span>{{ user.email }}</span>
            <span v-if="user.unreadCount > 0" class="unread-count"> <!-- Doesn't really work at the moment -->
              {{ user.unreadCount }}
            </span>
          </div>
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

        <!-- Message Input -->
        <div class="message-input">
          <input v-model="newMessage" type="text" placeholder="Type a message..." @keyup.enter="sendMessage" />
          <button @click="sendMessage">Send</button>
        </div>
      </div>
      <div v-else class="no-chat-selected">
        <p>Select a chat to view messages</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.new-chat-btn {
  width: 100%;
  padding: 10px;
  background: #007bff;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 5px;
  margin-bottom: 10px;
}

.new-chat-dropdown {
  display: flex;
  gap: 10px;
}

.new-chat-dropdown select {
  flex-grow: 1;
  padding: 5px;
}

.new-chat-dropdown button {
  padding: 5px;
  background: #28a745;
  color: white;
  border: none;
  cursor: pointer;
}

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
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar li:hover, .sidebar .active {
  background: #007bff;
  color: white;
}

/* User Info inside Sidebar */
.user-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

/* Unread count badge */
.sidebar .unread-count {
  background-color: #007bff;
  color: white;
  font-size: 0.9rem;
  padding: 4px 8px;
  border-radius: 50%;
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
  background: #e1e1e1;
  color: #333;
}

/* Message Time */
.message-time {
  font-size: 0.8rem;
  color: #aaa;
  position: absolute;
  bottom: 5px;
  right: 10px;
}

.message-input {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.message-input input {
  flex-grow: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.message-input button {
  padding: 10px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.no-chat-selected {
  text-align: center;
  font-size: 1.2rem;
  color: #aaa;
}
</style>
