import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'
import StockDetail from '@/views/StockDetail.vue'
import AlertHistory from '@/views/AlertHistory.vue'
import Portfolio from '@/views/Portfolio.vue'
import Watchlist from '@/views/Watchlist.vue'
import PortfolioAnalyzer from '@/views/PortfolioAnalyzer.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/portfolio',
    name: 'Portfolio',
    component: Portfolio
  },
  {
    path: '/watchlist',
    name: 'Watchlist',
    component: Watchlist
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
  },
  {
    path: '/analyzer',
    name: 'PortfolioAnalyzer',
    component: PortfolioAnalyzer
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
