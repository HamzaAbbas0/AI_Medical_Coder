import { createApp } from 'vue'

import App from './App.vue'

import router from './router' 

import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css'

import '@fortawesome/fontawesome-free/css/all.css'
import '@fortawesome/fontawesome-free/js/all.js'   

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'
import './style.css'

const app = createApp(App);

app.component('VueDatePicker', VueDatePicker);
app.use(router)
app.mount('#app');
