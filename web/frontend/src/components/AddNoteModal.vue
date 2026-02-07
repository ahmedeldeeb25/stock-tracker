<template>
  <div class="modal fade" id="addNoteModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ editMode ? 'Edit' : 'Add' }} Analysis Note</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <!-- Title -->
            <div class="mb-3">
              <label class="form-label">Title *</label>
              <input
                type="text"
                class="form-control"
                v-model="formData.title"
                placeholder="e.g., Q4 Earnings Analysis"
                required
              >
            </div>

            <!-- Note Date -->
            <div class="mb-3">
              <label class="form-label">Date *</label>
              <input
                type="date"
                class="form-control"
                v-model="formData.note_date"
                required
              >
            </div>

            <!-- Content -->
            <div class="mb-3">
              <label class="form-label">Content *</label>
              <QuillEditor
                v-model:content="formData.content"
                content-type="html"
                theme="snow"
                :toolbar="toolbarOptions"
                style="min-height: 200px;"
              />
            </div>

            <!-- Error Message -->
            <div v-if="errorMessage" class="alert alert-danger">
              {{ errorMessage }}
            </div>

            <!-- Submit Button -->
            <div class="d-grid">
              <button type="submit" class="btn btn-primary" :disabled="submitting">
                <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
                {{ submitting ? (editMode ? 'Updating...' : 'Adding...') : (editMode ? 'Update Note' : 'Add Note') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, computed } from 'vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import { stocksApi, notesApi } from '@/api'

export default {
  name: 'AddNoteModal',
  components: {
    QuillEditor
  },
  props: {
    stockId: {
      type: Number,
      required: true
    },
    note: {
      type: Object,
      default: null
    }
  },
  emits: ['note-added', 'note-updated'],
  setup(props, { emit }) {
    const formData = ref({
      title: '',
      content: '',
      note_date: new Date().toISOString().split('T')[0] // Today's date
    })

    const submitting = ref(false)
    const errorMessage = ref('')

    const editMode = computed(() => !!props.note)

    // Toolbar configuration with common formatting options
    const toolbarOptions = [
      [{ 'header': [1, 2, 3, false] }],
      [{ 'size': ['small', false, 'large', 'huge'] }],
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'color': [] }, { 'background': [] }],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      [{ 'align': [] }],
      ['blockquote', 'code-block'],
      ['link'],
      ['clean']
    ]

    // Watch for note changes and populate form
    watch(() => props.note, (newNote) => {
      if (newNote) {
        formData.value = {
          title: newNote.title,
          content: newNote.content,
          note_date: newNote.note_date
        }
      }
    }, { immediate: true })

    const resetForm = () => {
      formData.value = {
        title: '',
        content: '',
        note_date: new Date().toISOString().split('T')[0]
      }
      errorMessage.value = ''
    }

    const handleSubmit = async () => {
      submitting.value = true
      errorMessage.value = ''

      // Validate content is not empty
      const tempDiv = document.createElement('div')
      tempDiv.innerHTML = formData.value.content
      const textContent = tempDiv.textContent || tempDiv.innerText || ''

      if (!textContent.trim()) {
        errorMessage.value = 'Content is required'
        submitting.value = false
        return
      }

      try {
        if (editMode.value) {
          // Update existing note
          await notesApi.update(props.note.id, formData.value)
          emit('note-updated')
        } else {
          // Add new note
          await stocksApi.addNote(props.stockId, formData.value)
          emit('note-added')
        }

        // Close modal
        const modal = document.getElementById('addNoteModal')
        const modalInstance = window.bootstrap.Modal.getInstance(modal)
        modalInstance.hide()

        if (!editMode.value) {
          resetForm()
        }
      } catch (error) {
        errorMessage.value = error.response?.data?.error || `Failed to ${editMode.value ? 'update' : 'add'} note`
      } finally {
        submitting.value = false
      }
    }

    return {
      formData,
      submitting,
      errorMessage,
      editMode,
      toolbarOptions,
      handleSubmit
    }
  }
}
</script>

<style scoped>
:deep(.ql-container) {
  min-height: 200px;
  font-size: 14px;
}

:deep(.ql-editor) {
  min-height: 200px;
}

:deep(.ql-toolbar) {
  background-color: #f8f9fa;
  border-radius: 0.25rem 0.25rem 0 0;
}
</style>
