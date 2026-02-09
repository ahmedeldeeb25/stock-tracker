<template>
  <article class="card stock-card h-100" @click="navigateToStock">
    <div class="card-body p-3">
      <!-- Header: Symbol, Price, Change -->
      <div class="d-flex justify-content-between align-items-start mb-2">
        <div class="stock-info">
          <div class="d-flex align-items-center gap-2">
            <h2 class="h6 mb-0 stock-symbol">{{ stock.symbol }}</h2>
            <span
              v-if="stock.price_change_percent !== undefined"
              class="badge price-change-badge"
              :class="stock.price_change_percent >= 0 ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger'"
            >
              <i
                :class="stock.price_change_percent >= 0 ? 'bi bi-caret-up-fill' : 'bi bi-caret-down-fill'"
                aria-hidden="true"
              ></i>
              {{ formatPercent(stock.price_change_percent) }}
            </span>
          </div>
          <p class="text-muted small mb-0 company-name" v-if="stock.company_name">
            {{ truncate(stock.company_name, 25) }}
          </p>
        </div>
        <div class="text-end">
          <div class="h6 mb-0 stock-price">{{ formatPrice(stock.current_price) }}</div>
          <div v-if="stock.after_hours" class="after-hours-price">
            <small class="text-muted">{{ stock.after_hours.is_premarket ? 'PM' : 'AH' }}:</small>
            <small :class="stock.after_hours.change >= 0 ? 'text-success' : 'text-danger'">
              {{ formatPrice(stock.after_hours.price) }}
            </small>
          </div>
        </div>
      </div>

      <!-- Tags & Timeframes (compact) -->
      <div class="tags-row mb-2" v-if="(stock.tags && stock.tags.length) || (stock.timeframes && stock.timeframes.length)">
        <span
          v-for="tag in (stock.tags || []).slice(0, 3)"
          :key="'tag-' + tag.id"
          class="badge badge-sm me-1"
          :style="{ backgroundColor: tag.color || '#6c757d' }"
        >
          {{ tag.name }}
        </span>
        <span
          v-for="tf in (stock.timeframes || []).slice(0, 2)"
          :key="'tf-' + tf.id"
          class="badge badge-sm me-1"
          :style="{ backgroundColor: tf.color || '#6c757d', opacity: 0.8 }"
        >
          <i class="bi bi-clock" aria-hidden="true"></i> {{ tf.name }}
        </span>
        <span
          v-if="(stock.tags?.length || 0) + (stock.timeframes?.length || 0) > 5"
          class="badge badge-sm bg-secondary"
        >
          +{{ (stock.tags?.length || 0) + (stock.timeframes?.length || 0) - 5 }}
        </span>
      </div>

      <!-- Holdings (compact) -->
      <div v-if="stock.holding" class="holdings-compact mb-2">
        <div class="d-flex justify-content-between align-items-center">
          <span class="text-muted small">
            <i class="bi bi-wallet2 me-1"></i>
            {{ formatNumber(stock.holding.shares) }} shares
          </span>
          <span v-if="stock.holding.gain_loss !== undefined" class="small fw-medium" :class="getGainLossClass(stock.holding.gain_loss)">
            {{ formatGainLoss(stock.holding.gain_loss) }}
            <span class="text-muted">({{ formatPercent(stock.holding.gain_loss_percent) }})</span>
          </span>
          <span v-else-if="stock.holding.position_value" class="small fw-medium">
            {{ formatPrice(stock.holding.position_value) }}
          </span>
        </div>
      </div>

      <!-- Key Targets (compact - show closest buy/sell) -->
      <div class="targets-compact" v-if="keyTargets.length">
        <div
          v-for="target in keyTargets"
          :key="target.id"
          class="target-row d-flex justify-content-between align-items-center"
        >
          <div class="d-flex align-items-center gap-1">
            <span
              class="target-dot"
              :class="target.target_type === 'Buy' ? 'bg-success' : 'bg-danger'"
            ></span>
            <span class="small text-muted">{{ target.target_type }}</span>
            <span class="small">{{ formatPrice(target.target_price) }}</span>
          </div>
          <span class="small" :class="getPriceChangeClass(target.difference_percent)">
            {{ formatPercent(target.difference_percent) }}
          </span>
        </div>
      </div>

      <!-- Bottom row: Notes indicator & Quick actions -->
      <div class="d-flex justify-content-between align-items-center mt-2 pt-2 border-top">
        <div class="meta-info small text-muted">
          <span v-if="stock.notes_count" class="me-2">
            <i class="bi bi-journal-text"></i> {{ stock.notes_count }}
          </span>
          <span v-if="stock.targets?.length">
            <i class="bi bi-crosshair"></i> {{ stock.targets.length }}
          </span>
        </div>
        <div class="quick-actions" @click.stop>
          <button
            class="btn btn-sm btn-link text-danger p-0"
            @click="$emit('delete', stock.id)"
            title="Delete stock"
          >
            <i class="bi bi-trash"></i>
          </button>
        </div>
      </div>
    </div>
  </article>
</template>

<script>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { formatPrice, formatPercent, formatNumber, formatGainLoss, getPriceChangeClass, getTargetBadgeClass, getGainLossClass } from '@/utils/formatters'

export default {
  name: 'StockCard',
  props: {
    stock: {
      type: Object,
      required: true
    }
  },
  emits: ['delete'],
  setup(props) {
    const router = useRouter()

    // Get the most relevant targets (closest buy below, closest sell above)
    const keyTargets = computed(() => {
      if (!props.stock.targets || !props.stock.current_price) return []

      const currentPrice = props.stock.current_price
      const activeTargets = props.stock.targets.filter(t => t.is_active)

      // Find closest buy target (below current price)
      const buyTargets = activeTargets
        .filter(t => t.target_type === 'Buy' && t.target_price < currentPrice)
        .sort((a, b) => b.target_price - a.target_price)

      // Find closest sell target (above current price)
      const sellTargets = activeTargets
        .filter(t => t.target_type === 'Sell' && t.target_price > currentPrice)
        .sort((a, b) => a.target_price - b.target_price)

      const result = []
      if (buyTargets.length) result.push(buyTargets[0])
      if (sellTargets.length) result.push(sellTargets[0])

      return result.slice(0, 2)
    })

    const truncate = (str, length) => {
      if (!str) return ''
      return str.length > length ? str.substring(0, length) + '...' : str
    }

    const navigateToStock = () => {
      router.push(`/stock/${props.stock.symbol}`)
    }

    return {
      keyTargets,
      truncate,
      navigateToStock,
      formatPrice,
      formatPercent,
      formatNumber,
      formatGainLoss,
      getPriceChangeClass,
      getTargetBadgeClass,
      getGainLossClass
    }
  }
}
</script>

<style scoped>
.stock-card {
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid #e9ecef;
}

.stock-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #dee2e6;
}

.stock-symbol {
  font-weight: 700;
  color: #212529;
}

.company-name {
  font-size: 0.75rem;
  line-height: 1.2;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stock-price {
  font-weight: 600;
}

.price-change-badge {
  font-size: 0.7rem;
  padding: 0.2em 0.4em;
  font-weight: 600;
}

.after-hours-price {
  font-size: 0.7rem;
  line-height: 1.2;
}

.badge-sm {
  font-size: 0.65rem;
  padding: 0.2em 0.45em;
  font-weight: 500;
}

.holdings-compact {
  background: #f8f9fa;
  border-radius: 0.375rem;
  padding: 0.4rem 0.6rem;
  font-size: 0.8rem;
}

.targets-compact {
  font-size: 0.8rem;
}

.target-row {
  padding: 0.2rem 0;
}

.target-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.meta-info {
  font-size: 0.75rem;
}

.quick-actions .btn {
  opacity: 0.5;
  transition: opacity 0.2s;
}

.stock-card:hover .quick-actions .btn {
  opacity: 1;
}

/* Bootstrap 5.3+ subtle backgrounds fallback */
.bg-success-subtle {
  background-color: rgba(25, 135, 84, 0.1) !important;
}

.bg-danger-subtle {
  background-color: rgba(220, 53, 69, 0.1) !important;
}
</style>
