<template>
  <div
    class="modal fade"
    id="manageTimeframesModal"
    tabindex="-1"
    aria-labelledby="manageTimeframesModalLabel"
    aria-modal="true"
    role="dialog"
  >
    <div class="modal-dialog modal-lg modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="manageTimeframesModalLabel">Manage Investment Timeframes</h5>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body">
          <!-- Current Timeframes Section -->
          <div class="mb-4">
            <h6 class="mb-3">Current Timeframes</h6>
            <div v-if="currentTimeframes.length > 0" class="d-flex flex-wrap gap-2" role="list" aria-label="Current timeframes">
              <span
                v-for="timeframe in currentTimeframes"
                :key="timeframe.id"
                class="badge timeframe-badge d-flex align-items-center gap-2"
                :style="{ backgroundColor: timeframe.color || '#6c757d', fontSize: '0.9rem', padding: '0.5rem 0.75rem' }"
                role="listitem"
                :title="timeframe.description"
              >
                {{ timeframe.name }}
                <button
                  type="button"
                  class="btn-close btn-close-white"
                  style="font-size: 0.6rem;"
                  @click="removeTimeframe(timeframe.id)"
                  :aria-label="`Remove ${timeframe.name} timeframe`"
                ></button>
              </span>
            </div>
            <p v-else class="text-muted">No investment timeframes assigned to this stock</p>
          </div>

          <!-- Add Existing Timeframe Section -->
          <div class="mb-4">
            <h6 class="mb-3">Add Existing Timeframe</h6>
            <div class="d-flex gap-2 mb-3">
              <label for="selectTimeframe" class="visually-hidden">Select a timeframe to add</label>
              <select id="selectTimeframe" v-model="selectedTimeframeId" class="form-select" aria-label="Select timeframe to add">
                <option value="">Select a timeframe...</option>
                <option
                  v-for="timeframe in availableTimeframes"
                  :key="timeframe.id"
                  :value="timeframe.id"
                  :title="timeframe.description"
                >
                  {{ timeframe.name }} ({{ timeframe.stock_count }} stocks)
                </option>
              </select>
              <button
                class="btn btn-primary"
                @click="addExistingTimeframe"
                :disabled="!selectedTimeframeId"
                aria-label="Add selected timeframe to stock"
              >
                Add
              </button>
            </div>
            <p v-if="selectedTimeframeId && getSelectedTimeframeDescription" class="text-muted small">
              <i class="bi bi-info-circle me-1"></i>
              {{ getSelectedTimeframeDescription }}
            </p>
          </div>

          <hr>

          <!-- Create New Timeframe Section -->
          <div class="mb-4">
            <h6 class="mb-3">Create New Timeframe</h6>
            <form @submit.prevent="createNewTimeframe">
              <div class="row g-2 mb-2">
                <div class="col-md-5">
                  <label for="newTimeframeName" class="visually-hidden">New timeframe name</label>
                  <input
                    id="newTimeframeName"
                    v-model="newTimeframe.name"
                    type="text"
                    class="form-control"
                    placeholder="Timeframe name"
                    required
                    aria-label="New timeframe name"
                  >
                </div>
                <div class="col-md-5">
                  <label for="newTimeframeDescription" class="visually-hidden">Description</label>
                  <input
                    id="newTimeframeDescription"
                    v-model="newTimeframe.description"
                    type="text"
                    class="form-control"
                    placeholder="Description (optional)"
                    aria-label="Timeframe description"
                  >
                </div>
                <div class="col-md-2">
                  <label for="newTimeframeColor" class="visually-hidden">Timeframe color</label>
                  <input
                    id="newTimeframeColor"
                    v-model="newTimeframe.color"
                    type="color"
                    class="form-control form-control-color w-100"
                    title="Choose timeframe color"
                    aria-label="Choose timeframe color"
                  >
                </div>
              </div>
              <button type="submit" class="btn btn-success btn-sm">
                <i class="bi bi-plus" aria-hidden="true"></i> Create
              </button>
            </form>
          </div>

          <hr>

          <!-- Manage All Timeframes Section -->
          <div>
            <h6 class="mb-3">All Timeframes</h6>
            <div class="list-group" role="list" aria-label="All available timeframes">
              <div
                v-for="timeframe in allTimeframes"
                :key="timeframe.id"
                class="list-group-item d-flex justify-content-between align-items-center"
                role="listitem"
              >
                <div class="d-flex align-items-center gap-3 flex-grow-1">
                  <label v-if="editingTimeframeId === timeframe.id" :for="`editTimeframeName-${timeframe.id}`" class="visually-hidden">
                    Edit timeframe name
                  </label>
                  <input
                    v-if="editingTimeframeId === timeframe.id"
                    :id="`editTimeframeName-${timeframe.id}`"
                    v-model="editForm.name"
                    type="text"
                    class="form-control form-control-sm"
                    style="max-width: 150px;"
                    aria-label="Edit timeframe name"
                  >
                  <span v-else class="badge" :style="{ backgroundColor: timeframe.color || '#6c757d' }">
                    {{ timeframe.name }}
                  </span>

                  <label v-if="editingTimeframeId === timeframe.id" :for="`editTimeframeDescription-${timeframe.id}`" class="visually-hidden">
                    Edit timeframe description
                  </label>
                  <input
                    v-if="editingTimeframeId === timeframe.id"
                    :id="`editTimeframeDescription-${timeframe.id}`"
                    v-model="editForm.description"
                    type="text"
                    class="form-control form-control-sm"
                    style="max-width: 200px;"
                    placeholder="Description"
                    aria-label="Edit timeframe description"
                  >
                  <span v-else-if="timeframe.description" class="text-muted small">
                    {{ timeframe.description }}
                  </span>

                  <label v-if="editingTimeframeId === timeframe.id" :for="`editTimeframeColor-${timeframe.id}`" class="visually-hidden">
                    Edit timeframe color
                  </label>
                  <input
                    v-if="editingTimeframeId === timeframe.id"
                    :id="`editTimeframeColor-${timeframe.id}`"
                    v-model="editForm.color"
                    type="color"
                    class="form-control form-control-color form-control-sm"
                    style="max-width: 60px;"
                    aria-label="Edit timeframe color"
                  >

                  <small class="text-muted" :aria-label="`Used in ${timeframe.stock_count} stocks`">
                    {{ timeframe.stock_count }} stocks
                  </small>
                </div>

                <div class="btn-group btn-group-sm">
                  <button
                    v-if="editingTimeframeId === timeframe.id"
                    class="btn btn-success btn-sm"
                    @click="saveTimeframeEdit(timeframe.id)"
                    aria-label="Save timeframe changes"
                  >
                    <i class="bi bi-check" aria-hidden="true"></i>
                  </button>
                  <button
                    v-if="editingTimeframeId === timeframe.id"
                    class="btn btn-secondary btn-sm"
                    @click="cancelEdit"
                    aria-label="Cancel editing"
                  >
                    <i class="bi bi-x" aria-hidden="true"></i>
                  </button>
                  <button
                    v-else
                    class="btn btn-outline-primary btn-sm"
                    @click="startEdit(timeframe)"
                    :aria-label="`Edit ${timeframe.name} timeframe`"
                  >
                    <i class="bi bi-pencil" aria-hidden="true"></i>
                  </button>
                  <button
                    v-if="editingTimeframeId !== timeframe.id"
                    class="btn btn-outline-danger btn-sm"
                    @click="deleteTimeframe(timeframe.id)"
                    :aria-label="`Delete ${timeframe.name} timeframe`"
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
import { timeframesApi, stocksApi } from '@/api'
import { useConfirmStore } from '@/stores/confirm'
import { useToastStore } from '@/stores/toast'

export default {
  name: 'ManageTimeframesModal',
  props: {
    stockId: {
      type: Number,
      required: true
    },
    currentTimeframes: {
      type: Array,
      default: () => []
    }
  },
  emits: ['timeframes-updated'],
  setup(props, { emit }) {
    const confirm = useConfirmStore()
    const toast = useToastStore()
    const allTimeframes = ref([])
    const selectedTimeframeId = ref('')
    const newTimeframe = ref({ name: '', color: '#6366F1', description: '' })
    const editingTimeframeId = ref(null)
    const editForm = ref({ name: '', color: '', description: '' })

    const availableTimeframes = computed(() => {
      const currentTimeframeIds = props.currentTimeframes.map(t => t.id)
      return allTimeframes.value.filter(timeframe => !currentTimeframeIds.includes(timeframe.id))
    })

    const getSelectedTimeframeDescription = computed(() => {
      if (!selectedTimeframeId.value) return ''
      const timeframe = availableTimeframes.value.find(t => t.id === parseInt(selectedTimeframeId.value))
      return timeframe?.description || ''
    })

    const loadTimeframes = async () => {
      try {
        const response = await timeframesApi.getAll()
        allTimeframes.value = response.data.timeframes
      } catch (error) {
        console.error('Failed to load timeframes:', error)
      }
    }

    onMounted(() => {
      loadTimeframes()
    })

    const addExistingTimeframe = async () => {
      if (!selectedTimeframeId.value) return

      try {
        await stocksApi.addTimeframe(props.stockId, selectedTimeframeId.value)
        selectedTimeframeId.value = ''
        emit('timeframes-updated')
        loadTimeframes()
        toast.success('Timeframe added successfully')
      } catch (error) {
        toast.error('Failed to add timeframe: ' + (error.response?.data?.error || error.message))
      }
    }

    const removeTimeframe = async (timeframeId) => {
      const isConfirmed = await confirm.show({
        title: 'Remove Timeframe?',
        message: 'Remove this timeframe from the stock?',
        variant: 'warning',
        confirmText: 'Remove',
        cancelText: 'Cancel'
      })

      if (!isConfirmed) return

      try {
        await stocksApi.removeTimeframe(props.stockId, timeframeId)
        emit('timeframes-updated')
        loadTimeframes()
        toast.success('Timeframe removed successfully')
      } catch (error) {
        toast.error('Failed to remove timeframe: ' + (error.response?.data?.error || error.message))
      }
    }

    const createNewTimeframe = async () => {
      if (!newTimeframe.value.name.trim()) return

      try {
        await timeframesApi.create({
          name: newTimeframe.value.name.trim(),
          color: newTimeframe.value.color,
          description: newTimeframe.value.description.trim() || null
        })
        newTimeframe.value = { name: '', color: '#6366F1', description: '' }
        loadTimeframes()
        toast.success('Timeframe created successfully')
      } catch (error) {
        toast.error('Failed to create timeframe: ' + (error.response?.data?.error || error.message))
      }
    }

    const startEdit = (timeframe) => {
      editingTimeframeId.value = timeframe.id
      editForm.value = {
        name: timeframe.name,
        color: timeframe.color,
        description: timeframe.description || ''
      }
    }

    const cancelEdit = () => {
      editingTimeframeId.value = null
      editForm.value = { name: '', color: '', description: '' }
    }

    const saveTimeframeEdit = async (timeframeId) => {
      try {
        await timeframesApi.update(timeframeId, {
          name: editForm.value.name,
          color: editForm.value.color,
          description: editForm.value.description.trim() || null
        })
        editingTimeframeId.value = null
        emit('timeframes-updated')
        loadTimeframes()
        toast.success('Timeframe updated successfully')
      } catch (error) {
        toast.error('Failed to update timeframe: ' + (error.response?.data?.error || error.message))
      }
    }

    const deleteTimeframe = async (timeframeId) => {
      const isConfirmed = await confirm.show({
        title: 'Delete Timeframe?',
        message: 'Delete this timeframe? It will be removed from all stocks.',
        variant: 'danger',
        confirmText: 'Delete',
        cancelText: 'Cancel'
      })

      if (!isConfirmed) return

      try {
        await timeframesApi.delete(timeframeId)
        emit('timeframes-updated')
        loadTimeframes()
        toast.success('Timeframe deleted successfully')
      } catch (error) {
        toast.error('Failed to delete timeframe: ' + (error.response?.data?.error || error.message))
      }
    }

    return {
      allTimeframes,
      availableTimeframes,
      selectedTimeframeId,
      newTimeframe,
      editingTimeframeId,
      editForm,
      getSelectedTimeframeDescription,
      addExistingTimeframe,
      removeTimeframe,
      createNewTimeframe,
      startEdit,
      cancelEdit,
      saveTimeframeEdit,
      deleteTimeframe
    }
  }
}
</script>

<style scoped>
.timeframe-badge .btn-close-white {
  filter: brightness(0) invert(1);
  opacity: 0.7;
}

.timeframe-badge .btn-close-white:hover {
  opacity: 1;
}
</style>
