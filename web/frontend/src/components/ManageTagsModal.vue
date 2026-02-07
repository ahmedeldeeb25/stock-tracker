<template>
  <div class="modal fade" id="manageTagsModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Manage Tags</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <!-- Current Tags Section -->
          <div class="mb-4">
            <h6 class="mb-3">Current Tags</h6>
            <div v-if="currentTags.length > 0" class="d-flex flex-wrap gap-2">
              <span
                v-for="tag in currentTags"
                :key="tag.id"
                class="badge tag-badge d-flex align-items-center gap-2"
                :style="{ backgroundColor: tag.color || '#6c757d', fontSize: '0.9rem', padding: '0.5rem 0.75rem' }"
              >
                {{ tag.name }}
                <button
                  type="button"
                  class="btn-close btn-close-white"
                  style="font-size: 0.6rem;"
                  @click="removeTag(tag.id)"
                  title="Remove tag"
                ></button>
              </span>
            </div>
            <p v-else class="text-muted">No tags assigned to this stock</p>
          </div>

          <!-- Add Existing Tag Section -->
          <div class="mb-4">
            <h6 class="mb-3">Add Existing Tag</h6>
            <div class="d-flex gap-2 mb-3">
              <select v-model="selectedTagId" class="form-select">
                <option value="">Select a tag...</option>
                <option
                  v-for="tag in availableTags"
                  :key="tag.id"
                  :value="tag.id"
                >
                  {{ tag.name }} ({{ tag.stock_count }} stocks)
                </option>
              </select>
              <button
                class="btn btn-primary"
                @click="addExistingTag"
                :disabled="!selectedTagId"
              >
                Add
              </button>
            </div>
          </div>

          <hr>

          <!-- Create New Tag Section -->
          <div class="mb-4">
            <h6 class="mb-3">Create New Tag</h6>
            <form @submit.prevent="createNewTag">
              <div class="row g-2 mb-2">
                <div class="col-md-6">
                  <input
                    v-model="newTag.name"
                    type="text"
                    class="form-control"
                    placeholder="Tag name"
                    required
                  >
                </div>
                <div class="col-md-4">
                  <input
                    v-model="newTag.color"
                    type="color"
                    class="form-control form-control-color w-100"
                    title="Choose tag color"
                  >
                </div>
                <div class="col-md-2">
                  <button type="submit" class="btn btn-success w-100">
                    <i class="bi bi-plus"></i> Create
                  </button>
                </div>
              </div>
            </form>
          </div>

          <hr>

          <!-- Manage All Tags Section -->
          <div>
            <h6 class="mb-3">All Tags</h6>
            <div class="list-group">
              <div
                v-for="tag in allTags"
                :key="tag.id"
                class="list-group-item d-flex justify-content-between align-items-center"
              >
                <div class="d-flex align-items-center gap-3 flex-grow-1">
                  <input
                    v-if="editingTagId === tag.id"
                    v-model="editForm.name"
                    type="text"
                    class="form-control form-control-sm"
                    style="max-width: 200px;"
                  >
                  <span v-else class="badge" :style="{ backgroundColor: tag.color || '#6c757d' }">
                    {{ tag.name }}
                  </span>

                  <input
                    v-if="editingTagId === tag.id"
                    v-model="editForm.color"
                    type="color"
                    class="form-control form-control-color form-control-sm"
                    style="max-width: 60px;"
                  >

                  <small class="text-muted">{{ tag.stock_count }} stocks</small>
                </div>

                <div class="btn-group btn-group-sm">
                  <button
                    v-if="editingTagId === tag.id"
                    class="btn btn-success btn-sm"
                    @click="saveTagEdit(tag.id)"
                  >
                    <i class="bi bi-check"></i>
                  </button>
                  <button
                    v-if="editingTagId === tag.id"
                    class="btn btn-secondary btn-sm"
                    @click="cancelEdit"
                  >
                    <i class="bi bi-x"></i>
                  </button>
                  <button
                    v-else
                    class="btn btn-outline-primary btn-sm"
                    @click="startEdit(tag)"
                  >
                    <i class="bi bi-pencil"></i>
                  </button>
                  <button
                    v-if="editingTagId !== tag.id"
                    class="btn btn-outline-danger btn-sm"
                    @click="deleteTag(tag.id)"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { tagsApi, stocksApi } from '@/api'

export default {
  name: 'ManageTagsModal',
  props: {
    stockId: {
      type: Number,
      required: true
    },
    currentTags: {
      type: Array,
      default: () => []
    }
  },
  emits: ['tags-updated'],
  setup(props, { emit }) {
    const allTags = ref([])
    const selectedTagId = ref('')
    const newTag = ref({ name: '', color: '#6366F1' })
    const editingTagId = ref(null)
    const editForm = ref({ name: '', color: '' })

    const availableTags = computed(() => {
      const currentTagIds = props.currentTags.map(t => t.id)
      return allTags.value.filter(tag => !currentTagIds.includes(tag.id))
    })

    const loadTags = async () => {
      try {
        const response = await tagsApi.getAll()
        allTags.value = response.data.tags
      } catch (error) {
        console.error('Failed to load tags:', error)
      }
    }

    onMounted(() => {
      loadTags()
    })

    const addExistingTag = async () => {
      if (!selectedTagId.value) return

      try {
        await stocksApi.addTag(props.stockId, selectedTagId.value)
        selectedTagId.value = ''
        emit('tags-updated')
        loadTags()
      } catch (error) {
        alert('Failed to add tag: ' + (error.response?.data?.error || error.message))
      }
    }

    const removeTag = async (tagId) => {
      if (!confirm('Remove this tag from the stock?')) return

      try {
        await stocksApi.removeTag(props.stockId, tagId)
        emit('tags-updated')
        loadTags()
      } catch (error) {
        alert('Failed to remove tag: ' + (error.response?.data?.error || error.message))
      }
    }

    const createNewTag = async () => {
      if (!newTag.value.name.trim()) return

      try {
        await tagsApi.create({
          name: newTag.value.name.trim(),
          color: newTag.value.color
        })
        newTag.value = { name: '', color: '#6366F1' }
        loadTags()
      } catch (error) {
        alert('Failed to create tag: ' + (error.response?.data?.error || error.message))
      }
    }

    const startEdit = (tag) => {
      editingTagId.value = tag.id
      editForm.value = { name: tag.name, color: tag.color }
    }

    const cancelEdit = () => {
      editingTagId.value = null
      editForm.value = { name: '', color: '' }
    }

    const saveTagEdit = async (tagId) => {
      try {
        await tagsApi.update(tagId, {
          name: editForm.value.name,
          color: editForm.value.color
        })
        editingTagId.value = null
        emit('tags-updated')
        loadTags()
      } catch (error) {
        alert('Failed to update tag: ' + (error.response?.data?.error || error.message))
      }
    }

    const deleteTag = async (tagId) => {
      if (!confirm('Delete this tag? It will be removed from all stocks.')) return

      try {
        await tagsApi.delete(tagId)
        emit('tags-updated')
        loadTags()
      } catch (error) {
        alert('Failed to delete tag: ' + (error.response?.data?.error || error.message))
      }
    }

    return {
      allTags,
      availableTags,
      selectedTagId,
      newTag,
      editingTagId,
      editForm,
      addExistingTag,
      removeTag,
      createNewTag,
      startEdit,
      cancelEdit,
      saveTagEdit,
      deleteTag
    }
  }
}
</script>

<style scoped>
.tag-badge .btn-close-white {
  filter: brightness(0) invert(1);
  opacity: 0.7;
}

.tag-badge .btn-close-white:hover {
  opacity: 1;
}
</style>
