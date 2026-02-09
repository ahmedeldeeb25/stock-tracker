<template>
  <div class="market-overview mb-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h5 class="mb-0">
        <i class="bi bi-graph-up-arrow me-2"></i>
        Market Overview
      </h5>
      <div class="d-flex align-items-center gap-2">
        <small v-if="data?.updated_at" class="text-muted">
          Updated: {{ formatTime(data.updated_at) }}
        </small>
        <button
          class="btn btn-sm btn-outline-secondary"
          @click="fetchData"
          :disabled="loading"
          title="Refresh"
        >
          <i class="bi" :class="loading ? 'spinner-border spinner-border-sm' : 'bi-arrow-clockwise'"></i>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !data" class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-warning">
      <i class="bi bi-exclamation-triangle me-2"></i>
      Failed to load market data
    </div>

    <!-- Data Display -->
    <div v-else-if="data" class="row g-3">
      <!-- Fear & Greed Index -->
      <div class="col-12 col-lg-3">
        <div class="card h-100 fear-greed-card">
          <div class="card-body text-center">
            <h6 class="card-subtitle mb-2 text-muted">Fear & Greed Index</h6>
            <div v-if="data.fear_greed" class="fear-greed-display">
              <div
                class="fear-greed-score"
                :class="getFearGreedClass(data.fear_greed.score)"
              >
                {{ data.fear_greed.score }}
              </div>
              <div
                class="fear-greed-label"
                :class="getFearGreedClass(data.fear_greed.score)"
              >
                {{ data.fear_greed.sentiment }}
              </div>
              <div class="fear-greed-gauge mt-2">
                <div class="gauge-bar">
                  <div
                    class="gauge-fill"
                    :style="{ width: data.fear_greed.score + '%' }"
                    :class="getFearGreedClass(data.fear_greed.score)"
                  ></div>
                  <div
                    class="gauge-marker"
                    :style="{ left: data.fear_greed.score + '%' }"
                  ></div>
                </div>
                <div class="gauge-labels">
                  <span>Fear</span>
                  <span>Greed</span>
                </div>
              </div>
              <div class="mt-2 small text-muted">
                <span>Week ago: {{ data.fear_greed.week_ago }}</span>
                <span class="mx-2">|</span>
                <span>Month ago: {{ data.fear_greed.month_ago }}</span>
              </div>
            </div>
            <div v-else class="text-muted">
              <i class="bi bi-dash-circle"></i> Unavailable
            </div>
          </div>
        </div>
      </div>

      <!-- VIX -->
      <div class="col-6 col-md-3 col-lg-2">
        <div class="card h-100">
          <div class="card-body text-center">
            <h6 class="card-subtitle mb-2 text-muted">VIX</h6>
            <div v-if="data.vix" class="index-display">
              <div class="index-price" :class="getVixClass(data.vix.price)">
                {{ data.vix.price?.toFixed(2) }}
              </div>
              <div
                class="index-change small"
                :class="data.vix.change >= 0 ? 'text-danger' : 'text-success'"
              >
                {{ data.vix.change >= 0 ? '+' : '' }}{{ data.vix.change?.toFixed(2) }}
                ({{ data.vix.change_percent >= 0 ? '+' : '' }}{{ data.vix.change_percent?.toFixed(2) }}%)
              </div>
              <div class="vix-label small mt-1" :class="getVixClass(data.vix.price)">
                {{ getVixLabel(data.vix.price) }}
              </div>
            </div>
            <div v-else class="text-muted">--</div>
          </div>
        </div>
      </div>

      <!-- 10Y Treasury -->
      <div class="col-6 col-md-3 col-lg-2">
        <div class="card h-100">
          <div class="card-body text-center">
            <h6 class="card-subtitle mb-2 text-muted">10Y Treasury</h6>
            <div v-if="data.treasury_10y" class="index-display">
              <div class="index-price">
                {{ data.treasury_10y.price?.toFixed(2) }}%
              </div>
              <div
                class="index-change small"
                :class="data.treasury_10y.change >= 0 ? 'text-danger' : 'text-success'"
              >
                {{ data.treasury_10y.change >= 0 ? '+' : '' }}{{ data.treasury_10y.change?.toFixed(2) }}
              </div>
            </div>
            <div v-else class="text-muted">--</div>
          </div>
        </div>
      </div>

      <!-- Major Indices -->
      <div
        v-for="(index, symbol) in data.indices"
        :key="symbol"
        class="col-6 col-md-3 col-lg"
      >
        <div class="card h-100">
          <div class="card-body text-center">
            <h6 class="card-subtitle mb-2 text-muted">{{ index.name }}</h6>
            <div class="index-display">
              <div class="index-price">
                ${{ index.price?.toFixed(2) }}
              </div>
              <div
                class="index-change small"
                :class="index.change >= 0 ? 'text-success' : 'text-danger'"
              >
                {{ index.change >= 0 ? '+' : '' }}{{ index.change?.toFixed(2) }}
                ({{ index.change_percent >= 0 ? '+' : '' }}{{ index.change_percent?.toFixed(2) }}%)
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { pricesApi } from '@/api'

export default {
  name: 'MarketOverview',
  setup() {
    const data = ref(null)
    const loading = ref(false)
    const error = ref(null)

    const fetchData = async () => {
      loading.value = true
      error.value = null

      try {
        const response = await pricesApi.getMarketOverview()
        data.value = response.data
      } catch (err) {
        console.error('Error fetching market overview:', err)
        error.value = err.message
      } finally {
        loading.value = false
      }
    }

    const formatTime = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const getFearGreedClass = (score) => {
      if (score <= 25) return 'extreme-fear'
      if (score <= 45) return 'fear'
      if (score <= 55) return 'neutral'
      if (score <= 75) return 'greed'
      return 'extreme-greed'
    }

    const getVixClass = (value) => {
      if (!value) return ''
      if (value >= 30) return 'text-danger'
      if (value >= 20) return 'text-warning'
      return 'text-success'
    }

    const getVixLabel = (value) => {
      if (!value) return ''
      if (value >= 30) return 'High Volatility'
      if (value >= 20) return 'Moderate'
      return 'Low Volatility'
    }

    onMounted(() => {
      fetchData()
    })

    return {
      data,
      loading,
      error,
      fetchData,
      formatTime,
      getFearGreedClass,
      getVixClass,
      getVixLabel
    }
  }
}
</script>

<style scoped>
.market-overview .card {
  border-radius: 0.5rem;
  transition: transform 0.2s, box-shadow 0.2s;
}

.market-overview .card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.fear-greed-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.fear-greed-score {
  font-size: 2.5rem;
  font-weight: bold;
  line-height: 1;
}

.fear-greed-label {
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.extreme-fear {
  color: #dc3545;
}

.fear {
  color: #fd7e14;
}

.neutral {
  color: #6c757d;
}

.greed {
  color: #20c997;
}

.extreme-greed {
  color: #198754;
}

.fear-greed-gauge {
  margin-top: 0.5rem;
}

.gauge-bar {
  height: 8px;
  background: linear-gradient(to right, #dc3545, #fd7e14, #ffc107, #20c997, #198754);
  border-radius: 4px;
  position: relative;
}

.gauge-fill {
  height: 100%;
  border-radius: 4px;
  opacity: 0;
}

.gauge-marker {
  position: absolute;
  top: -4px;
  width: 4px;
  height: 16px;
  background: #333;
  border-radius: 2px;
  transform: translateX(-50%);
}

.gauge-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: #6c757d;
  margin-top: 2px;
}

.index-display {
  min-height: 60px;
}

.index-price {
  font-size: 1.25rem;
  font-weight: 600;
}

.index-change {
  font-size: 0.85rem;
}

.vix-label {
  font-weight: 500;
}

@media (max-width: 768px) {
  .fear-greed-score {
    font-size: 2rem;
  }

  .index-price {
    font-size: 1.1rem;
  }
}
</style>
