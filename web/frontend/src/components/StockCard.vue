<template>
  <article class="card stock-card h-100">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-start mb-2">
        <div class="flex-grow-1 me-2">
          <h2 class="h5 card-title mb-1">
            <router-link
              :to="`/stock/${stock.symbol}`"
              class="text-decoration-none"
              :aria-label="`View details for ${stock.symbol}${stock.company_name ? ', ' + stock.company_name : ''}`"
            >
              {{ stock.symbol }}
            </router-link>
          </h2>
          <p class="text-muted small mb-2" v-if="stock.company_name">
            {{ stock.company_name }}
          </p>
        </div>
        <div class="text-end flex-shrink-0">
          <!-- Regular Market Price -->
          <div v-if="stock.current_price" class="d-flex align-items-baseline justify-content-end gap-2 mb-1">
            <span class="h5 mb-0" aria-label="Current price">{{ formatPrice(stock.current_price) }}</span>
            <span
              v-if="stock.price_change_percent"
              :class="getPriceChangeClass(stock.price_change_percent)"
              class="small fw-semibold"
              :aria-label="`Price change ${stock.price_change_percent >= 0 ? 'up' : 'down'} ${Math.abs(stock.price_change_percent)}%`"
            >
              <i
                :class="stock.price_change_percent >= 0 ? 'bi bi-arrow-up' : 'bi bi-arrow-down'"
                aria-hidden="true"
              ></i>
              {{ stock.price_change_percent >= 0 ? '+' : '' }}{{ formatPercent(stock.price_change_percent) }}
            </span>
          </div>

          <!-- After Hours Price -->
          <div v-if="stock.after_hours" class="d-flex align-items-baseline justify-content-end gap-2">
            <small class="text-muted" style="font-size: 0.7rem;">
              {{ stock.after_hours.is_premarket ? 'Pre-Market:' : 'After Hours:' }}
            </small>
            <small class="fw-bold">{{ formatPrice(stock.after_hours.price) }}</small>
            <small
              :class="stock.after_hours.change >= 0 ? 'text-success' : 'text-danger'"
              class="fw-semibold"
              style="font-size: 0.75rem;"
            >
              {{ stock.after_hours.change >= 0 ? '+' : '' }}{{ formatPercent(stock.after_hours.change_percent) }}
            </small>
          </div>
        </div>
      </div>

      <!-- Tags -->
      <div class="mb-2" v-if="stock.tags && stock.tags.length" role="list" aria-label="Stock tags">
        <span
          v-for="tag in stock.tags"
          :key="tag.id"
          class="badge tag-badge me-1"
          :style="{ backgroundColor: tag.color || '#6c757d' }"
          role="listitem"
        >
          {{ tag.name }}
        </span>
      </div>

      <!-- Investment Timeframes -->
      <div class="mb-2" v-if="stock.timeframes && stock.timeframes.length" role="list" aria-label="Investment timeframes">
        <span
          v-for="timeframe in stock.timeframes"
          :key="timeframe.id"
          class="badge timeframe-badge me-1"
          :style="{ backgroundColor: timeframe.color || '#6c757d' }"
          role="listitem"
          :title="timeframe.description"
        >
          <i class="bi bi-clock me-1" aria-hidden="true"></i>
          {{ timeframe.name }}
        </span>
      </div>

      <!-- Holdings Section -->
      <div v-if="stock.holding" class="holdings-section mb-3 p-2 rounded bg-light border">
        <div class="holdings-label text-muted text-uppercase small fw-semibold mb-1" style="letter-spacing: 0.5px;">
          Holdings
        </div>
        <div class="holdings-content">
          <div class="shares-line">
            {{ formatNumber(stock.holding.shares) }} shares
            <span v-if="stock.holding.average_cost" class="text-muted">
              @ {{ formatPrice(stock.holding.average_cost) }} avg
            </span>
          </div>
          <div class="value-line fw-medium" v-if="stock.holding.position_value">
            Value: {{ formatPrice(stock.holding.position_value) }}
          </div>
          <div
            v-if="stock.holding.gain_loss !== undefined && stock.holding.gain_loss !== null"
            class="gain-loss-line"
            :class="getGainLossClass(stock.holding.gain_loss)"
          >
            <i
              :class="stock.holding.gain_loss >= 0 ? 'bi bi-arrow-up' : 'bi bi-arrow-down'"
              aria-hidden="true"
            ></i>
            {{ stock.holding.gain_loss >= 0 ? 'Gain' : 'Loss' }}:
            {{ formatGainLoss(stock.holding.gain_loss) }}
            ({{ formatPercent(stock.holding.gain_loss_percent) }})
          </div>
        </div>
      </div>

      <!-- Targets -->
      <div class="mt-3" v-if="filteredTargets.length">
        <h3 class="visually-hidden">Price Targets</h3>
        <div
          v-for="target in filteredTargets"
          :key="target.id"
          class="d-flex justify-content-between align-items-center mb-2 p-2 rounded"
          :class="{ 'alert-triggered bg-light': target.is_triggered }"
        >
          <div>
            <span
              class="badge target-badge me-2"
              :class="getTargetBadgeClass(target.target_type)"
            >
              {{ target.target_type }}
              <span v-if="target.trim_percentage"> ({{ target.trim_percentage }}%)</span>
            </span>
            <span class="text-muted">@ {{ formatPrice(target.target_price) }}</span>
          </div>
          <div class="text-end">
            <i
              v-if="target.is_triggered"
              class="bi bi-bell-fill text-warning"
              aria-label="Alert triggered"
            ></i>
            <small :class="getPriceChangeClass(target.difference_percent)">
              {{ target.difference_percent ? formatPercent(target.difference_percent) : '' }}
            </small>
          </div>
        </div>
      </div>

      <!-- Notes count -->
      <div class="mt-3 text-muted small" v-if="stock.notes_count">
        <i class="bi bi-journal-text me-1" aria-hidden="true"></i>
        {{ stock.notes_count }} {{ stock.notes_count === 1 ? 'note' : 'notes' }}
      </div>
    </div>

    <div class="card-footer bg-transparent">
      <div class="d-flex justify-content-between gap-2">
        <router-link
          :to="`/stock/${stock.symbol}`"
          class="btn btn-sm btn-outline-primary flex-grow-1"
          :aria-label="`View ${stock.symbol} details`"
        >
          <i class="bi bi-eye me-1" aria-hidden="true"></i>
          Details
        </router-link>
        <button
          @click="$emit('delete', stock.id)"
          class="btn btn-sm btn-outline-danger"
          :aria-label="`Delete ${stock.symbol} from portfolio`"
        >
          <i class="bi bi-trash" aria-hidden="true"></i>
        </button>
      </div>
    </div>
  </article>
</template>

<script>
import { computed } from 'vue'
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
    const filteredTargets = computed(() => {
      if (!props.stock.targets) return []
      return props.stock.targets.filter(target =>
        target.target_type === 'Buy' || target.target_type === 'Sell'
      )
    })

    return {
      filteredTargets,
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
