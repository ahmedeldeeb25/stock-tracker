<template>
  <div class="modal fade" id="viewNoteModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ note?.title }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <small class="text-muted">
              <i class="bi bi-calendar me-1"></i>
              {{ formatDate(note?.note_date) }}
            </small>
          </div>
          <div class="note-content" v-html="note?.content"></div>
        </div>
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-outline-primary"
            @click="$emit('edit', note)"
          >
            <i class="bi bi-pencil me-1"></i>
            Edit
          </button>
          <button
            type="button"
            class="btn btn-outline-danger"
            @click="handleDelete"
            :disabled="deleting"
          >
            <span v-if="deleting" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="bi bi-trash me-1"></i>
            Delete
          </button>
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { notesApi } from '@/api'
import { formatDate } from '@/utils/formatters'

export default {
  name: 'ViewNoteModal',
  props: {
    note: {
      type: Object,
      default: null
    }
  },
  emits: ['note-deleted', 'edit'],
  setup(props, { emit }) {
    const deleting = ref(false)

    const handleDelete = async () => {
      if (!confirm('Are you sure you want to delete this note?')) {
        return
      }

      deleting.value = true

      try {
        await notesApi.delete(props.note.id)

        // Close modal
        const modal = document.getElementById('viewNoteModal')
        const modalInstance = window.bootstrap.Modal.getInstance(modal)
        modalInstance.hide()

        emit('note-deleted')
      } catch (error) {
        alert('Failed to delete note: ' + (error.response?.data?.error || error.message))
      } finally {
        deleting.value = false
      }
    }

    return {
      deleting,
      handleDelete,
      formatDate
    }
  }
}
</script>

<style scoped>
.note-content {
  word-wrap: break-word;
  overflow-wrap: break-word;
  line-height: 1.6;
}

.note-content :deep(h1) {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.note-content :deep(h2) {
  font-size: 1.3rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.note-content :deep(h3) {
  font-size: 1.1rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.note-content :deep(p) {
  margin-bottom: 0.5rem;
}

.note-content :deep(ul),
.note-content :deep(ol) {
  margin-left: 1.5rem;
  margin-bottom: 0.5rem;
}

.note-content :deep(blockquote) {
  border-left: 3px solid #ccc;
  padding-left: 1rem;
  margin-left: 0;
  color: #666;
}

.note-content :deep(pre) {
  background-color: #f5f5f5;
  padding: 0.5rem;
  border-radius: 0.25rem;
  overflow-x: auto;
}

.note-content :deep(code) {
  background-color: #f5f5f5;
  padding: 0.1rem 0.3rem;
  border-radius: 0.2rem;
  font-family: monospace;
}

.note-content :deep(a) {
  color: #0d6efd;
  text-decoration: underline;
}
</style>
