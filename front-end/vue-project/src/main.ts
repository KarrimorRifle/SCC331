import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import './assets/main.css';
import '@fortawesome/fontawesome-free/css/all.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';

const app = createApp(App);
const pinia = createPinia();

app.use(router);

app.use(pinia);

app.mount('#app');