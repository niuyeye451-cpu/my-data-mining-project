import { createApp } from 'vue'
//import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
//import { Vue } from '@vueuse/core/node_modules/vue-demi'

//Vue.use(router)
//Vue.use(store)

const app = createApp(App)
app.use(store).use(router).use(ElementPlus).mount('#app')
app.config.globalProperties.$http = axios
axios.defaults.baseURL = 'http://localhost:8082'
axios.defaults.headers.post['Content-Type'] = 'application/json'
//Vue.createApp(App).mount('#app')
