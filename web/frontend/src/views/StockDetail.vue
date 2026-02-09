<template>
  <div>
    <!-- Loading State -->
    <div v-if="loading">
      <StockDetailSkeleton />
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle me-2"></i>
      {{ error }}
      <router-link to="/" class="btn btn-sm btn-outline-primary ms-3">
        Back to Dashboard
      </router-link>
    </div>

    <!-- Stock Detail -->
    <div v-else-if="stock">
      <!-- Header -->
      <div class="d-flex justify-content-between align-items-start mb-4">
        <div>
          <router-link to="/" class="text-decoration-none text-muted mb-2 d-block">
            <i class="bi bi-arrow-left me-1" aria-hidden="true"></i>
            Back to Dashboard
          </router-link>
          <div class="d-flex align-items-center gap-2">
            <a
              :href="`https://www.google.com/finance/quote/${stock.symbol}:NASDAQ`"
              target="_blank"
              class="text-decoration-none text-dark"
              :aria-label="`View ${stock.symbol} on Google Finance (opens in new tab)`"
            >
              <h1 class="h2 mb-1 stock-symbol-link">
                {{ stock.symbol }}
              </h1>
            </a>
            <a
              :href="`https://finance.yahoo.com/chart/${stock.symbol}`"
              target="_blank"
              class="btn btn-sm btn-outline-secondary"
              :aria-label="`View ${stock.symbol} chart on Yahoo Finance (opens in new tab)`"
            >
              <i class="bi bi-graph-up" aria-hidden="true"></i>
            </a>
          </div>
          <div v-if="stock.company_name">
            <p class="text-muted mb-0">{{ stock.company_name }}</p>
          </div>
          <div v-else>
            <button
              class="btn btn-sm btn-link text-muted p-0"
              @click="fetchCompanyInfo"
              :disabled="fetchingInfo"
              aria-label="Fetch company name from yfinance"
            >
              <span v-if="fetchingInfo">
                <span class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
                Fetching...
              </span>
              <span v-else>
                <i class="bi bi-cloud-download me-1" aria-hidden="true"></i>
                Fetch Company Name
              </span>
            </button>
          </div>
        </div>
        <div class="text-end">
          <div class="h2 mb-0" v-if="stock.current_price">
            {{ formatPrice(stock.current_price) }}
          </div>
          <div v-if="stock.after_hours" class="mt-1">
            <div class="text-muted small">
              {{ stock.after_hours.is_premarket ? 'Pre-Market' : 'After Hours' }}
            </div>
            <div>
              <span class="fw-bold">{{ formatPrice(stock.after_hours.price) }}</span>
              <span
                class="ms-2"
                :class="stock.after_hours.change >= 0 ? 'text-success' : 'text-danger'"
              >
                {{ stock.after_hours.change >= 0 ? '+' : '' }}{{ formatPrice(stock.after_hours.change) }}
                ({{ stock.after_hours.change_percent >= 0 ? '+' : '' }}{{ stock.after_hours.change_percent.toFixed(2) }}%)
              </span>
            </div>
          </div>
          <div v-if="stock.rsi" class="mt-2">
            <span class="badge" :class="getRsiBadgeClass(stock.rsi)">
              RSI: {{ stock.rsi.toFixed(2) }}
            </span>
          </div>
          <button
            class="btn btn-sm btn-outline-primary mt-2"
            @click="refreshData"
            aria-label="Refresh stock data"
          >
            <i class="bi bi-arrow-clockwise me-1" aria-hidden="true"></i>
            Refresh
          </button>
        </div>
      </div>

      <!-- Tags -->
      <div class="mb-3">
        <label class="form-label small text-muted mb-1">Tags</label>
        <div v-if="stock.tags && stock.tags.length" class="d-flex flex-wrap gap-2">
          <button
            v-for="tag in stock.tags"
            :key="tag.id"
            class="badge tag-badge clickable-tag"
            :style="{ backgroundColor: tag.color || '#6c757d' }"
            @click="showManageTagsModal"
            :aria-label="`${tag.name} tag, click to manage tags`"
          >
            {{ tag.name }}
          </button>
        </div>
        <button
          v-else
          class="badge bg-secondary clickable-tag"
          @click="showManageTagsModal"
          aria-label="Add tags to this stock"
        >
          <i class="bi bi-plus me-1" aria-hidden="true"></i>
          Add Tags
        </button>
      </div>

      <!-- Investment Timeframes -->
      <div class="mb-4">
        <div v-if="stock.timeframes && stock.timeframes.length" class="d-flex flex-wrap gap-2">
          <button
            v-for="timeframe in stock.timeframes"
            :key="timeframe.id"
            class="badge timeframe-badge clickable-tag"
            :style="{ backgroundColor: timeframe.color || '#6c757d' }"
            @click="showManageTimeframesModal"
            :aria-label="`${timeframe.name} timeframe, click to manage timeframes`"
            :title="timeframe.description"
          >
            <i class="bi bi-clock me-1" aria-hidden="true"></i>
            {{ timeframe.name }}
          </button>
        </div>
        <button
          v-else
          class="badge bg-secondary clickable-tag"
          @click="showManageTimeframesModal"
          aria-label="Add investment timeframes to this stock"
        >
          <i class="bi bi-plus me-1" aria-hidden="true"></i>
          Add Timeframe
        </button>
      </div>

      <div class="row">
        <!-- Left Column: Chart, Fundamental Data, Targets & Alerts - Responsive col-md-8 -->
        <div class="col-md-8">
          <!-- TradingView Chart -->
          <CollapsibleCard
            title="Chart"
            icon="bi bi-graph-up"
            :default-open="true"
            storage-key="stock-chart"
            body-class="p-0"
          >
            <template #actions>
              <a
                :href="`https://www.google.com/finance/quote/${stock.symbol}:NASDAQ`"
                target="_blank"
                class="btn btn-sm btn-outline-secondary"
                title="View on Google Finance"
                @click.stop
              >
                <i class="bi bi-box-arrow-up-right"></i>
              </a>
            </template>
            <!-- TradingView Widget -->
            <div class="tradingview-widget-container">
              <div :id="`tradingview_${stock.symbol}`" style="height: 500px;"></div>
            </div>
          </CollapsibleCard>

          <!-- Fundamental Data Panel -->
          <CollapsibleCard
            title="Fundamental Data"
            icon="bi bi-graph-up-arrow"
            :default-open="true"
            storage-key="fundamental-data"
          >
            <template #actions>
              <button
                class="btn btn-sm btn-outline-secondary"
                @click.stop="refreshData"
                aria-label="Refresh fundamental data"
              >
                <i class="bi bi-arrow-clockwise" aria-hidden="true"></i>
              </button>
            </template>
            <FundamentalDataContent
              :data="stock.fundamental_data"
              :current-price="stock.current_price"
            />
          </CollapsibleCard>

          <!-- Targets Section -->
          <CollapsibleCard
            title="Price Targets"
            icon="bi bi-crosshair"
            :default-open="true"
            storage-key="price-targets"
          >
            <template #actions>
              <button
                class="btn btn-sm btn-outline-primary"
                @click.stop="showAddTargetModal"
                aria-label="Add new price target"
              >
                <i class="bi bi-plus" aria-hidden="true"></i>
              </button>
            </template>
            <div>
              <div
                v-for="target in stock.targets"
                :key="target.id"
                class="p-3 mb-3 border rounded target-item"
                :class="{ 'alert-triggered bg-light': target.is_triggered }"
              >
                <div class="d-flex justify-content-between align-items-start">
                  <div class="flex-grow-1">
                    <span
                      class="badge target-badge me-2"
                      :class="getTargetBadgeClass(target.target_type)"
                    >
                      {{ target.target_type }}
                      <span v-if="target.trim_percentage"> ({{ target.trim_percentage }}%)</span>
                    </span>
                    <span class="h5">{{ formatPrice(target.target_price) }}</span>
                  </div>
                  <div class="text-end d-flex align-items-start gap-2">
                    <div>
                      <div>
                        <i v-if="target.is_triggered" class="bi bi-bell-fill text-warning fs-5"></i>
                        <span
                          class="ms-2"
                          :class="getPriceChangeClass(target.difference_percent)"
                        >
                          {{ formatPrice(target.difference) }}
                          ({{ formatPercent(target.difference_percent) }})
                        </span>
                      </div>
                      <span
                        class="badge"
                        :class="target.is_active ? 'bg-success' : 'bg-secondary'"
                      >
                        {{ target.is_active ? 'Active' : 'Inactive' }}
                      </span>
                    </div>
                    <div class="btn-group-vertical btn-group-sm">
                      <button
                        class="btn btn-outline-primary btn-sm"
                        @click="editTarget(target)"
                        aria-label="Edit target"
                      >
                        <i class="bi bi-pencil" aria-hidden="true"></i>
                      </button>
                      <button
                        class="btn btn-outline-secondary btn-sm"
                        @click="toggleTarget(target)"
                        :aria-label="target.is_active ? 'Deactivate target' : 'Activate target'"
                      >
                        <i :class="target.is_active ? 'bi bi-toggle-on' : 'bi bi-toggle-off'" aria-hidden="true"></i>
                      </button>
                    </div>
                  </div>
                </div>
                <div v-if="target.alert_note" class="mt-2 text-muted small">
                  <i class="bi bi-info-circle me-1"></i>
                  {{ target.alert_note }}
                </div>
              </div>
            </div>
          </CollapsibleCard>

          <!-- Alert History -->
          <CollapsibleCard
            v-if="stock.alert_history && stock.alert_history.length"
            title="Recent Alerts"
            icon="bi bi-clock-history"
            :default-open="false"
            storage-key="alert-history"
          >
            <div
              v-for="alert in stock.alert_history"
              :key="alert.id"
              class="d-flex justify-content-between align-items-center mb-3 pb-3 border-bottom"
            >
              <div>
                <span
                  class="badge me-2"
                  :class="getTargetBadgeClass(alert.target_type)"
                >
                  {{ alert.target_type }}
                </span>
                <span>
                  {{ formatPrice(alert.current_price) }}
                  (target: {{ formatPrice(alert.target_price) }})
                </span>
                <div v-if="alert.alert_note" class="text-muted small mt-1">
                  {{ alert.alert_note }}
                </div>
              </div>
              <div class="text-end text-muted small">
                <div>{{ formatDateTime(alert.triggered_at) }}</div>
                <i
                  v-if="alert.email_sent"
                  class="bi bi-envelope-check text-success"
                  title="Email sent"
                ></i>
              </div>
            </div>
          </CollapsibleCard>
        </div>

        <!-- Right Column: Notes - Responsive col-md-4 -->
        <div class="col-md-4">
          <CollapsibleCard
            title="Analysis Notes"
            icon="bi bi-journal-text"
            :default-open="true"
            storage-key="analysis-notes"
            body-class="p-0"
          >
            <template #actions>
              <button
                class="btn btn-sm btn-outline-primary"
                @click.stop="showAddNoteModal"
                aria-label="Add new analysis note"
              >
                <i class="bi bi-plus" aria-hidden="true"></i>
              </button>
            </template>
            <div style="max-height: 600px; overflow-y: auto; padding: 1rem;">
              <div
                v-for="note in stock.notes"
                :key="note.id"
                class="note-card p-3 mb-3 border rounded cursor-pointer"
                @click="viewNote(note)"
              >
                <div class="d-flex justify-content-between align-items-start">
                  <div class="flex-grow-1">
                    <h6 class="mb-1">{{ note.title }}</h6>
                    <p class="text-muted small mb-0">
                      <i class="bi bi-calendar me-1"></i>
                      {{ formatDate(note.note_date) }}
                    </p>
                  </div>
                  <i class="bi bi-chevron-right text-muted"></i>
                </div>
              </div>
              <div v-if="!stock.notes || stock.notes.length === 0" class="text-center text-muted py-4">
                <i class="bi bi-inbox display-6"></i>
                <p class="mt-2">No notes yet</p>
                <button class="btn btn-sm btn-primary" @click="showAddNoteModal">
                  Add First Note
                </button>
              </div>
            </div>
          </CollapsibleCard>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <AddTargetModal
      v-if="stock"
      :stock-id="stock.id"
      @target-added="handleTargetAdded"
    />
    <EditTargetModal
      v-if="stock && selectedTarget"
      :target="selectedTarget"
      @target-updated="handleTargetUpdated"
      @target-deleted="handleTargetDeleted"
    />
    <AddNoteModal
      v-if="stock"
      :stock-id="stock.id"
      :note="editingNote"
      @note-added="handleNoteAdded"
      @note-updated="handleNoteUpdated"
    />
    <ViewNoteModal
      v-if="selectedNote"
      :note="selectedNote"
      @note-deleted="handleNoteDeleted"
      @edit="editNote"
    />
    <ManageTagsModal
      v-if="stock"
      :stock-id="stock.id"
      :current-tags="stock.tags || []"
      @tags-updated="handleTagsUpdated"
    />
    <ManageTimeframesModal
      v-if="stock"
      :stock-id="stock.id"
      :current-timeframes="stock.timeframes || []"
      @timeframes-updated="handleTimeframesUpdated"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useStocksStore } from '@/stores/stocks'
import { useToastStore } from '@/stores/toast'
import { formatPrice, formatPercent, formatDate, formatDateTime, getPriceChangeClass, getTargetBadgeClass } from '@/utils/formatters'
import AddTargetModal from '@/components/AddTargetModal.vue'
import EditTargetModal from '@/components/EditTargetModal.vue'
import AddNoteModal from '@/components/AddNoteModal.vue'
import ViewNoteModal from '@/components/ViewNoteModal.vue'
import ManageTagsModal from '@/components/ManageTagsModal.vue'
import ManageTimeframesModal from '@/components/ManageTimeframesModal.vue'
import StockDetailSkeleton from '@/components/StockDetailSkeleton.vue'
import CollapsibleCard from '@/components/CollapsibleCard.vue'
import FundamentalDataContent from '@/components/FundamentalDataContent.vue'
import { targetsApi, stocksApi } from '@/api'

export default {
  name: 'StockDetail',
  components: {
    AddTargetModal,
    EditTargetModal,
    AddNoteModal,
    ViewNoteModal,
    ManageTagsModal,
    ManageTimeframesModal,
    StockDetailSkeleton,
    CollapsibleCard,
    FundamentalDataContent
  },
  setup() {
    const route = useRoute()
    const stocksStore = useStocksStore()
    const toast = useToastStore()
    const symbol = route.params.symbol

    const loading = computed(() => stocksStore.loading)
    const error = computed(() => stocksStore.error)
    const stock = computed(() => stocksStore.currentStock)

    const selectedTarget = ref(null)
    const selectedNote = ref(null)
    const editingNote = ref(null)
    const fetchingInfo = ref(false)

    // Load TradingView script
    const loadTradingViewScript = () => {
      return new Promise((resolve, reject) => {
        if (document.getElementById('tradingview-widget-script')) {
          resolve()
          return
        }

        const script = document.createElement('script')
        script.id = 'tradingview-widget-script'
        script.src = 'https://s3.tradingview.com/tv.js'
        script.async = true
        script.onload = resolve
        script.onerror = reject
        document.head.appendChild(script)
      })
    }

    // Initialize TradingView chart
    const initTradingViewChart = async () => {
      if (!stock.value) return

      try {
        await loadTradingViewScript()
        await nextTick()

        if (window.TradingView) {
          new window.TradingView.widget({
            autosize: true,
            symbol: stock.value.symbol,
            interval: 'D',
            timezone: 'America/New_York',
            theme: 'light',
            style: '1',
            locale: 'en',
            toolbar_bg: '#f1f3f6',
            enable_publishing: false,
            hide_top_toolbar: false,
            hide_legend: false,
            save_image: false,
            container_id: `tradingview_${stock.value.symbol}`
          })
        }
      } catch (error) {
        console.error('Failed to load TradingView chart:', error)
      }
    }

    onMounted(() => {
      loadStock()
    })

    const loadStock = async () => {
      try {
        await stocksStore.fetchStockDetails(symbol)
        await initTradingViewChart()
      } catch (error) {
        console.error('Failed to load stock:', error)
      }
    }

    const refreshData = () => {
      loadStock()
    }

    const fetchCompanyInfo = async () => {
      if (!stock.value) return

      fetchingInfo.value = true

      try {
        const response = await stocksApi.fetchInfo(stock.value.id)
        if (response.data.company_name) {
          // Refresh stock data to show updated name
          await loadStock()
          toast.success('Company information fetched successfully')
        }
      } catch (error) {
        toast.error('Failed to fetch company info: ' + (error.response?.data?.error || error.message))
      } finally {
        fetchingInfo.value = false
      }
    }

    // Target functions
    const showAddTargetModal = () => {
      const modal = new window.bootstrap.Modal(document.getElementById('addTargetModal'))
      modal.show()
    }

    const editTarget = (target) => {
      selectedTarget.value = target
      const modal = new window.bootstrap.Modal(document.getElementById('editTargetModal'))
      modal.show()
    }

    const toggleTarget = async (target) => {
      try {
        await targetsApi.toggle(target.id)
        loadStock()
        toast.success(`Target ${target.is_active ? 'deactivated' : 'activated'}`)
      } catch (error) {
        toast.error('Failed to toggle target: ' + (error.response?.data?.error || error.message))
      }
    }

    const handleTargetAdded = () => {
      loadStock()
      selectedTarget.value = null
      toast.success('Target added successfully')
    }

    const handleTargetUpdated = () => {
      loadStock()
      selectedTarget.value = null
      toast.success('Target updated successfully')
    }

    const handleTargetDeleted = () => {
      loadStock()
      selectedTarget.value = null
      toast.success('Target deleted successfully')
    }

    // Note functions
    const showAddNoteModal = () => {
      editingNote.value = null
      const modal = new window.bootstrap.Modal(document.getElementById('addNoteModal'))
      modal.show()
    }

    const viewNote = (note) => {
      selectedNote.value = note
      const modal = new window.bootstrap.Modal(document.getElementById('viewNoteModal'))
      modal.show()
    }

    const editNote = (note) => {
      // Close view modal
      const viewModal = window.bootstrap.Modal.getInstance(document.getElementById('viewNoteModal'))
      if (viewModal) {
        viewModal.hide()
      }

      // Open edit modal
      editingNote.value = note
      setTimeout(() => {
        const editModal = new window.bootstrap.Modal(document.getElementById('addNoteModal'))
        editModal.show()
      }, 300)
    }

    const handleNoteAdded = () => {
      loadStock()
      editingNote.value = null
      toast.success('Note added successfully')
    }

    const handleNoteUpdated = () => {
      loadStock()
      editingNote.value = null
      selectedNote.value = null
      toast.success('Note updated successfully')
    }

    const handleNoteDeleted = () => {
      loadStock()
      selectedNote.value = null
      toast.success('Note deleted successfully')
    }

    // Tags functions
    const showManageTagsModal = () => {
      const modal = new window.bootstrap.Modal(document.getElementById('manageTagsModal'))
      modal.show()
    }

    const handleTagsUpdated = () => {
      loadStock()
      toast.success('Tags updated successfully')
    }

    // Timeframes functions
    const showManageTimeframesModal = () => {
      const modal = new window.bootstrap.Modal(document.getElementById('manageTimeframesModal'))
      modal.show()
    }

    const handleTimeframesUpdated = () => {
      loadStock()
      toast.success('Timeframes updated successfully')
    }

    const getRsiBadgeClass = (rsi) => {
      if (rsi < 30) return 'bg-success'  // Oversold
      if (rsi > 70) return 'bg-danger'   // Overbought
      return 'bg-secondary'              // Neutral
    }

    return {
      loading,
      error,
      stock,
      selectedTarget,
      selectedNote,
      editingNote,
      fetchingInfo,
      refreshData,
      fetchCompanyInfo,
      showAddTargetModal,
      editTarget,
      toggleTarget,
      handleTargetAdded,
      handleTargetUpdated,
      handleTargetDeleted,
      showAddNoteModal,
      viewNote,
      editNote,
      handleNoteAdded,
      handleNoteUpdated,
      handleNoteDeleted,
      showManageTagsModal,
      handleTagsUpdated,
      showManageTimeframesModal,
      handleTimeframesUpdated,
      formatPrice,
      formatPercent,
      formatDate,
      formatDateTime,
      getPriceChangeClass,
      getTargetBadgeClass,
      getRsiBadgeClass
    }
  }
}
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}

.stock-symbol-link {
  transition: all 0.2s ease;
  display: inline-block;
}

.stock-symbol-link:hover {
  color: #0d6efd !important;
  transform: translateX(2px);
}

.stock-symbol-link .bi-box-arrow-up-right {
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.stock-symbol-link:hover .bi-box-arrow-up-right {
  opacity: 1;
}

.clickable-tag {
  cursor: pointer;
  transition: all 0.2s ease;
}

.clickable-tag:hover {
  opacity: 0.85;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.note-card {
  transition: all 0.2s ease;
}

.note-card:hover {
  background-color: #f8f9fa;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.target-item {
  transition: all 0.2s ease;
}

.target-item:hover {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.note-content {
  word-wrap: break-word;
  overflow-wrap: break-word;
}

/* Quill content styling */
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

.note-content :deep(strong) {
  font-weight: bold;
}

.note-content :deep(em) {
  font-style: italic;
}

.note-content :deep(u) {
  text-decoration: underline;
}

.note-content :deep(s) {
  text-decoration: line-through;
}
</style>
