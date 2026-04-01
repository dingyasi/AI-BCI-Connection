import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '../views/Home.vue'
import BrainGame from '../views/BrainGame.vue'

const routes = [
  {
    path: '/',
    component: Home
  },
  {
    path: '/brain-game',
    component: BrainGame
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
