import { defineStore } from 'pinia'
import { alertsApi } from '@/api'

export const useAlertsStore = defineStore('alerts', {
  state: () => ({
    alerts: [],
    loading: false,
    error: null,
    total: 0,
    limit: 50,
    offset: 0
  }),

  actions: {
    async fetchAlerts(params = {}) {
      this.loading = true
      this.error = null

      try {
        const response = await alertsApi.getAll({
          limit: params.limit || this.limit,
          offset: params.offset || this.offset,
          ...params
        })
        this.alerts = response.data.alerts
        this.total = response.data.total
      } catch (error) {
        this.error = error.response?.data?.error || error.message
        console.error('Error fetching alerts:', error)
      } finally {
        this.loading = false
      }
    },

    async deleteAlert(alertId) {
      this.loading = true
      this.error = null

      try {
        await alertsApi.delete(alertId)
        this.alerts = this.alerts.filter(a => a.id !== alertId)
        this.total -= 1
      } catch (error) {
        this.error = error.response?.data?.error || error.message
        console.error('Error deleting alert:', error)
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})
