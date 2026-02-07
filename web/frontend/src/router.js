import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'
import StockDetail from '@/views/StockDetail.vue'
import AlertHistory from '@/views/AlertHistory.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/stock/:symbol',
    name: 'StockDetail',
    component: StockDetail,
    props: true
  },
  {
    path: '/alerts',
    name: 'AlertHistory',
    component: AlertHistory
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
