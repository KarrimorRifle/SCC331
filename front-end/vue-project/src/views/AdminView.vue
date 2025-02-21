<script>
import axios from 'axios';

export default {
	name: "UserListPage",
	data() {
		return {
			users: [],
			newUser: { fullName: "", email: "", lastActive: "Just now", isAdmin: false },
			editingIndex: null,
			editedName: "",
			showResetPasswordModal: false,
			resetPasswordUserIndex: null,
			newPassword: "",
			confirmPassword: "",
			showMessageModal: false,
			messageUserIndex: null,
			userMessage: "",
			userIsAdmin: false,
			loading: true
		};
	},
	methods: {
		async checkAdmin() {
			try {
				const response = await axios.get('http://localhost:5007/check_admin', { withCredentials: true });
				if (response.status === 200) {
					this.userIsAdmin = true;
					this.fetchUsers(); // Load users only if authorized
				}
			} catch (error) {
				console.error("Authorization check failed:", error);
				this.userIsAdmin = false;
			} finally {
				this.loading = false;
			}
		},
		fetchUsers() {
			axios.get('http://localhost:5007/get_users_admin', { withCredentials: true })
				.then(response => {
					this.users = response.data.users.map(user => ({
						fullName: user.name,
						email: user.email,
						lastActive: user.last_login,
						isAdmin: user.authority === "Admin"
					}));
				})
				.catch(error => {
					console.error("Error fetching users:", error);
				});
		},
		addUser() {
			if (this.newUser.fullName && this.newUser.email) {
				axios.post('http://localhost:5007/add_user', {
					full_name: this.newUser.fullName,
					email: this.newUser.email,
					is_admin: this.newUser.isAdmin
				}, { withCredentials: true })
					.then(() => {
						alert("User added successfully!");
						this.fetchUsers();
						this.newUser = { fullName: "", email: "", lastActive: "Just now", isAdmin: false };
					})
					.catch(error => {
						console.error("Error adding user:", error);
						alert("Failed to add user.");
					});
			} else {
				alert("Full Name and Email are required.");
			}
		},
		deleteUser(index) {
			const userEmail = this.users[index].email;
			axios.post('http://localhost:5007/delete_user', { email: userEmail }, { withCredentials: true })
				.then(() => {
					this.users.splice(index, 1);
				})
				.catch(error => {
					console.error("Error deleting user:", error);
				});
		},
		openResetPasswordModal(index) {
			this.resetPasswordUserIndex = index;
			this.showResetPasswordModal = true;
			this.newPassword = "";
			this.confirmPassword = "";
		},
		resetPassword() {
			if (this.newPassword === this.confirmPassword && this.newPassword.trim()) {
				const userEmail = this.users[this.resetPasswordUserIndex].email;
				axios.post('http://localhost:5007/reset_password', { email: userEmail, new_password: this.newPassword }, { withCredentials: true })
					.then(() => {
						alert(`Password for ${this.users[this.resetPasswordUserIndex].fullName} has been reset.`);
						this.showResetPasswordModal = false;
					})
					.catch(error => {
						console.error("Error resetting password:", error);
					});
			} else {
				alert("Passwords do not match or are empty.");
			}
		},
		openMessageModal(index) {
			this.messageUserIndex = index;
			this.showMessageModal = true;
			this.userMessage = "";
		},
		sendMessage() {
			const receiverEmail = this.users[this.messageUserIndex].email;
			axios.post('http://localhost:5007/send_message', { receiver_email: receiverEmail, message: this.userMessage }, { withCredentials: true })
				.then(() => {
					alert(`Message sent to ${this.users[this.messageUserIndex].fullName}`);
					this.showMessageModal = false;
				})
				.catch(error => {
					console.error("Error sending message:", error);
				});
		}
	},
	mounted() {
		this.checkAdmin();
	}
};
</script>

<template>
	<div v-if="loading" class="loading-container">Checking authorization...</div>
	<div v-else-if="!userIsAdmin" class="not-authorized">Not Authorized</div>
	<div v-else class="container">
		<h1 class="title">User List</h1>
		<div class="input-section">
			<input v-model="newUser.fullName" type="text" placeholder="Full Name" class="input">
			<input v-model="newUser.email" type="email" placeholder="Email" class="input">
			<label class="checkbox-label">
				<input v-model="newUser.isAdmin" type="checkbox" class="checkbox">
				<span>Admin</span>
			</label>
			<button @click="addUser" class="button add">Add User</button>
		</div>
		<div class="table-container">
			<table class="user-table">
				<thead>
					<tr>
						<th>Full Name</th>
						<th>Email</th>
						<th>Last Active</th>
						<th>Admin</th>
						<th>Actions</th>
					</tr>
				</thead>
				<tbody>
					<tr v-for="(user, index) in users" :key="index">
						<td>{{ user.fullName }}</td>
						<td>{{ user.email }}</td>
						<td>{{ user.lastActive }}</td>
						<td>{{ user.isAdmin ? 'Yes' : 'No' }}</td>
						<td>
							<button @click="openMessageModal(index)" class="btn-secondary btn btn-sm me-2">Message</button>
							<button @click="deleteUser(index)" class="btn-danger btn btn-sm ">Delete</button>
							<button @click="openResetPasswordModal(index)" class="btn-primary btn btn-sm mt-2" title="Reset user's password">Reset</button>
						</td>
					</tr>
				</tbody>
			</table>
		</div>
	</div>
	
			<!-- ✅ Reset Password Modal -->
			<div v-if="showResetPasswordModal" class="modal">
			<div class="modal-content">
				<h2>Reset Password</h2>
				<p>Reset password for {{ users[resetPasswordUserIndex]?.fullName }}</p>
				<input 
					v-model="newPassword" 
					type="password" 
					placeholder="New Password" 
					class="input password-input" 
				/>
				<input 
					v-model="confirmPassword" 
					type="password" 
					placeholder="Confirm Password" 
					class="input password-input" 
				/>
				<div class="modal-actions">
					<button @click="resetPassword" class="button send">Reset</button>
					<button @click="showResetPasswordModal = false" class="button cancel">Cancel</button>
				</div>
			</div>
		</div>

		<!-- ✅ Send Message Modal -->
		<div v-if="showMessageModal" class="modal">
			<div class="modal-content">
				<h2>Send Message</h2>
				<p>Send a message to {{ users[messageUserIndex]?.fullName }}</p>
				<textarea v-model="userMessage" class="textarea" placeholder="Type your message..."></textarea>
				<div class="modal-actions">
					<button @click="sendMessage" class="button send">Send</button>
					<button @click="showMessageModal = false" class="button cancel">Cancel</button>
				</div>
			</div>
		</div>
</template>


<style scoped>
.loading-container,
.not-authorized {
	display: flex;
	justify-content: center;
	align-items: center;
	height: 100vh;
	font-size: 32px;
	font-weight: bold;
	color: #e53e3e;
	text-align: center;
}
.container {
	max-width: 900px;
	margin: 0 auto;
	padding: 20px;
	background: linear-gradient(to right, #ebf8ff, #90cdf4);
	border-radius: 10px;
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.title {
	text-align: center;
	font-size: 24px;
	font-weight: bold;
	color: #2d3748;
	margin-bottom: 20px;
}
.input-section {
	display: flex;
	gap: 10px;
	background: white;
	padding: 10px;
	border-radius: 10px;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.input {
	border: 1px solid #ccc;
	padding: 8px;
	border-radius: 5px;
	width: 20%;
}
.button {
	padding: 8px 12px;
	border-radius: 5px;
	color: white;
	cursor: pointer;
}
.add { background: #38a169; }
.message { background: #c4bad9; }
.delete { background: #e53e3e; }
.reset { background: #3182ce; }
.cancel { background: #718096; }
.send { background: #38a169; }
.table-container {
	background: white;
	padding: 10px;
	border-radius: 10px;
}
.user-table {
	width: 100%;
	border-collapse: collapse;
}
.user-table th, .user-table td {
	padding: 10px;
	text-align: left;
	border-bottom: 1px solid #ddd;
}
/* Modal Background */
.modal {
	position: fixed;
	inset: 0;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	justify-content: center;
	align-items: center;
	z-index: 1000;
}

/* Modal Title */
.modal-title {
	font-size: 24px;
	font-weight: 600;
	color: #333;
	margin-bottom: 10px;
}

/* Modal Description */
.modal-description {
	font-size: 16px;
	color: #555;
	margin-bottom: 20px;
}

/* Modal Input Fields */
.password-input {
  width: 90%;            /* Make the input fields take up 90% of the available space */
  max-width: 350px;      /* Limiting the maximum width of the input fields */
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #ddd;
  margin-bottom: 15px;
  font-size: 16px;
  box-sizing: border-box;
  display: block;
  margin: 0 auto;        /* Center the inputs */
}

/* Adjusting the modal content for better alignment */
.modal-content {
  padding: 20px;
  background: #fff;
  border-radius: 10px;
  width: 350px;          /* Modal width set to 350px */
  text-align: center;
  max-width: 100%;
  box-sizing: border-box;
}

/* Modal Action Buttons */
.modal-actions {
	display: flex;
	justify-content: space-between;
	gap: 10px;
}

/* Buttons */
.button {
	padding: 10px 15px;
	border-radius: 5px;
	font-size: 16px;
	cursor: pointer;
	transition: background-color 0.3s;
}

.send {
	background-color: #38a169;
	color: white;
}

.cancel {
	background-color: #e53e3e;
	color: white;
}

.send:hover {
	background-color: #2f855a;
}

.cancel:hover {
	background-color: #c53030;
}

/* Animation for the modal */
@keyframes fadeIn {
	from {
		opacity: 0;
		transform: scale(0.9);
	}
	to {
		opacity: 1;
		transform: scale(1);
	}
}

.textarea {
	width: 100%;
	padding: 8px;
	border: 1px solid #ccc;
	border-radius: 5px;
}
</style>
