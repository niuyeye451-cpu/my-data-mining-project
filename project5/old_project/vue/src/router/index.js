import { createRouter, createWebHistory } from 'vue-router'
import search from '../components/search.vue'
import login from '../components/login.vue'
import register from '../components/register.vue'

const routes = [
  { path: '', name: 'home', redirect:'/search' },
  { path: '/search', name: 'search', component: search },
  { path: '/login', name: 'login', component: login },
  { path: '/register', name: 'register', component: register },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
