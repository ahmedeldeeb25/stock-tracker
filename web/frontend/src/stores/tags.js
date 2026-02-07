import { defineStore } from 'pinia'
import { tagsApi } from '@/api'

export const useTagsStore = defineStore('tags', {
  state: () => ({
    tags: [],
    loading: false,
    error: null
  }),

  actions: {
    async fetchTags() {
      this.loading = true
      this.error = null

      try {
        const response = await tagsApi.getAll()
        this.tags = response.data.tags
      } catch (error) {
        this.error = error.response?.data?.error || error.message
        console.error('Error fetching tags:', error)
      } finally {
        this.loading = false
      }
    },

    async createTag(tagData) {
      this.loading = true
      this.error = null

      try {
        const response = await tagsApi.create(tagData)
        await this.fetchTags()
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.message
        console.error('Error creating tag:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteTag(tagId) {
      this.loading = true
      this.error = null

      try {
        await tagsApi.delete(tagId)
        this.tags = this.tags.filter(t => t.id !== tagId)
      } catch (error) {
        this.error = error.response?.data?.error || error.message
        console.error('Error deleting tag:', error)
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})
