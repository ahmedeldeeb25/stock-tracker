<template>
  <div
    class="modal fade"
    id="manageTagsModal"
    tabindex="-1"
    aria-labelledby="manageTagsModalLabel"
    aria-modal="true"
    role="dialog"
  >
    <div class="modal-dialog modal-lg modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="manageTagsModalLabel">Manage Tags</h5>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body">
          <!-- Current Tags Section -->
          <div class="mb-4">
            <h6 class="mb-3">Current Tags</h6>
            <div v-if="currentTags.length > 0" class="d-flex flex-wrap gap-2" role="list" aria-label="Current tags">
              <span
                v-for="tag in currentTags"
                :key="tag.id"
                class="badge tag-badge d-flex align-items-center gap-2"
                :style="{ backgroundColor: tag.color || '#6c757d', fontSize: '0.9rem', padding: '0.5rem 0.75rem' }"
                role="listitem"
              >
                {{ tag.name }}
                <button
                  type="button"
                  class="btn-close btn-close-white"
                  style="font-size: 0.6rem;"
                  @click="removeTag(tag.id)"
                  :aria-label="`Remove ${tag.name} tag`"
                ></button>
              </span>
            </div>
            <p v-else class="text-muted">No tags assigned to this stock</p>
          </div>

          <!-- Add Existing Tag Section -->
          <div class="mb-4">
            <h6 class="mb-3">Add Existing Tag</h6>
            <div class="d-flex gap-2 mb-3">
              <label for="selectTag" class="visually-hidden">Select a tag to add</label>
              <select id="selectTag" v-model="selectedTagId" class="form-select" aria-label="Select tag to add">
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
                aria-label="Add selected tag to stock"
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
                  <label for="newTagName" class="visually-hidden">New tag name</label>
                  <input
                    id="newTagName"
                    v-model="newTag.name"
                    type="text"
                    class="form-control"
                    placeholder="Tag name"
                    required
                    aria-label="New tag name"
                  >
                </div>
                <div class="col-md-4">
                  <label for="newTagColor" class="visually-hidden">Tag color</label>
                  <input
                    id="newTagColor"
                    v-model="newTag.color"
                    type="color"
                    class="form-control form-control-color w-100"
                    title="Choose tag color"
                    aria-label="Choose tag color"
                  >
                </div>
                <div class="col-md-2">
                  <button type="submit" class="btn btn-success w-100" aria-label="Create new tag">
                    <i class="bi bi-plus" aria-hidden="true"></i> Create
                  </button>
                </div>
              </div>
            </form>
          </div>

          <hr>

          <!-- Manage All Tags Section -->
          <div>
            <h6 class="mb-3">All Tags</h6>
            <div class="list-group" role="list" aria-label="All available tags">
              <div
                v-for="tag in allTags"
                :key="tag.id"
                class="list-group-item d-flex justify-content-between align-items-center"
                role="listitem"
              >
                <div class="d-flex align-items-center gap-3 flex-grow-1">
                  <label v-if="editingTagId === tag.id" :for="`editTagName-${tag.id}`" class="visually-hidden">
                    Edit tag name
                  </label>
                  <input
                    v-if="editingTagId === tag.id"
                    :id="`editTagName-${tag.id}`"
                    v-model="editForm.name"
                    type="text"
                    class="form-control form-control-sm"
                    style="max-width: 200px;"
                    aria-label="Edit tag name"
                  >
                  <span v-else class="badge" :style="{ backgroundColor: tag.color || '#6c757d' }">
                    {{ tag.name }}
                  </span>

                  <label v-if="editingTagId === tag.id" :for="`editTagColor-${tag.id}`" class="visually-hidden">
                    Edit tag color
                  </label>
                  <input
                    v-if="editingTagId === tag.id"
                    :id="`editTagColor-${tag.id}`"
                    v-model="editForm.color"
                    type="color"
                    class="form-control form-control-color form-control-sm"
                    style="max-width: 60px;"
                    aria-label="Edit tag color"
                  >

                  <small class="text-muted" :aria-label="`Used in ${tag.stock_count} stocks`">
                    {{ tag.stock_count }} stocks
                  </small>
                </div>

                <div class="btn-group btn-group-sm">
                  <button
                    v-if="editingTagId === tag.id"
                    class="btn btn-success btn-sm"
                    @click="saveTagEdit(tag.id)"
                    aria-label="Save tag changes"
                  >
                    <i class="bi bi-check" aria-hidden="true"></i>
                  </button>
                  <button
                    v-if="editingTagId === tag.id"
                    class="btn btn-secondary btn-sm"
                    @click="cancelEdit"
                    aria-label="Cancel editing"
                  >
                    <i class="bi bi-x" aria-hidden="true"></i>
                  </button>
                  <button
                    v-else
                    class="btn btn-outline-primary btn-sm"
                    @click="startEdit(tag)"
                    :aria-label="`Edit ${tag.name} tag`"
                  >
                    <i class="bi bi-pencil" aria-hidden="true"></i>
                  </button>
                  <button
                    v-if="editingTagId !== tag.id"
                    class="btn btn-outline-danger btn-sm"
                    @click="deleteTag(tag.id)"
                    :aria-label="`Delete ${tag.name} tag`"
                  >
                    <i class="bi bi-trash" aria-hidden="true"></i>
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
import { useConfirmStore } from '@/stores/confirm'
import { useToastStore } from '@/stores/toast'

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
    const confirm = useConfirmStore()
    const toast = useToastStore()
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
        toast.error('Failed to add tag: ' + (error.response?.data?.error || error.message))
      }
    }

    const removeTag = async (tagId) => {
      const isConfirmed = await confirm.show({
        title: 'Remove Tag?',
        message: 'Remove this tag from the stock?',
        variant: 'warning',
        confirmText: 'Remove',
        cancelText: 'Cancel'
      })

      if (!isConfirmed) return

      try {
        await stocksApi.removeTag(props.stockId, tagId)
        emit('tags-updated')
        loadTags()
      } catch (error) {
        toast.error('Failed to remove tag: ' + (error.response?.data?.error || error.message))
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
        toast.error('Failed to create tag: ' + (error.response?.data?.error || error.message))
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
        toast.error('Failed to update tag: ' + (error.response?.data?.error || error.message))
      }
    }

    const deleteTag = async (tagId) => {
      const isConfirmed = await confirm.show({
        title: 'Delete Tag?',
        message: 'Delete this tag? It will be removed from all stocks.',
        variant: 'danger',
        confirmText: 'Delete',
        cancelText: 'Cancel'
      })

      if (!isConfirmed) return

      try {
        await tagsApi.delete(tagId)
        emit('tags-updated')
        loadTags()
      } catch (error) {
        toast.error('Failed to delete tag: ' + (error.response?.data?.error || error.message))
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
