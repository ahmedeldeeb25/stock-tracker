<template>
  <div class="analyzer-view">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h2 mb-0">
        <i class="bi bi-bar-chart-line me-2"></i>
        Portfolio Analyzer
      </h1>
      <div class="d-flex gap-2">
        <button
          class="btn btn-outline-secondary"
          @click="fetchData"
          :disabled="loading"
        >
          <i class="bi bi-arrow-clockwise me-1"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-2">Analyzing portfolio...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle me-2"></i>
      {{ error }}
    </div>

    <!-- Empty State -->
    <div v-else-if="!holdings.length" class="text-center py-5">
      <i class="bi bi-pie-chart display-1 text-muted"></i>
      <p class="lead text-muted mt-3">No holdings to analyze</p>
      <p class="text-muted">Add stocks with shares to see portfolio analysis</p>
      <router-link to="/portfolio" class="btn btn-primary">
        <i class="bi bi-briefcase me-1"></i>
        Go to Portfolio
      </router-link>
    </div>

    <!-- Analysis Content -->
    <div v-else>
      <!-- Summary Cards -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-2">
          <div class="card summary-card h-100">
            <div class="card-body text-center">
              <div class="summary-label text-muted small">Total Value</div>
              <div class="summary-value h5 mb-0">{{ formatPrice(analysis.totalValue) }}</div>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-2">
          <div class="card summary-card h-100">
            <div class="card-body text-center">
              <div class="summary-label text-muted small">Total P/L</div>
              <div class="summary-value h5 mb-0" :class="getPLClass(analysis.totalPL)">
                {{ formatPL(analysis.totalPL) }}
              </div>
              <div class="small" :class="getPLClass(analysis.totalPLPercent)">
                {{ formatPercent(analysis.totalPLPercent) }}
              </div>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-2">
          <div class="card summary-card h-100">
            <div class="card-body text-center">
              <div class="summary-label text-muted small">Portfolio Beta</div>
              <div class="summary-value h5 mb-0" :class="getBetaClass(analysis.portfolioBeta)">
                {{ analysis.portfolioBeta?.toFixed(2) || '-' }}
              </div>
              <div class="small text-muted">{{ getBetaLabel(analysis.portfolioBeta) }}</div>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-2">
          <div class="card summary-card h-100">
            <div class="card-body text-center">
              <div class="summary-label text-muted small">Dividend Yield</div>
              <div class="summary-value h5 mb-0 text-info">
                {{ analysis.avgDividendYield?.toFixed(2) || '0.00' }}%
              </div>
              <div class="small text-muted">{{ formatPrice(analysis.annualIncome) }}/yr</div>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-2">
          <div class="card summary-card h-100">
            <div class="card-body text-center">
              <div class="summary-label text-muted small">Diversification</div>
              <div class="summary-value h5 mb-0" :class="getDiversificationClass(analysis.diversificationScore)">
                {{ analysis.diversificationScore || '-' }}
              </div>
              <div class="small text-muted">{{ analysis.sectors?.length || 0 }} sectors</div>
            </div>
          </div>
        </div>
        <div class="col-6 col-md-2">
          <div class="card summary-card h-100">
            <div class="card-body text-center">
              <div class="summary-label text-muted small">Avg P/E Ratio</div>
              <div class="summary-value h5 mb-0">
                {{ analysis.avgPE?.toFixed(1) || '-' }}
              </div>
              <div class="small text-muted">weighted</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Allocation Section -->
      <div class="row g-4 mb-4">
        <!-- Sector Allocation -->
        <div class="col-md-6">
          <div class="card h-100">
            <div class="card-header">
              <h6 class="mb-0">
                <i class="bi bi-pie-chart me-2"></i>
                Sector Allocation
              </h6>
            </div>
            <div class="card-body">
              <div v-if="analysis.sectorAllocation?.length" class="allocation-list">
                <div
                  v-for="(sector, index) in analysis.sectorAllocation"
                  :key="sector.name"
                  class="allocation-item mb-2"
                >
                  <div class="d-flex justify-content-between mb-1">
                    <span class="small fw-medium">{{ sector.name || 'Unknown' }}</span>
                    <span class="small text-muted">{{ sector.percent.toFixed(1) }}%</span>
                  </div>
                  <div class="progress" style="height: 8px;">
                    <div
                      class="progress-bar"
                      :style="{ width: sector.percent + '%', backgroundColor: getAllocationColor(index) }"
                    ></div>
                  </div>
                </div>
              </div>
              <div v-else class="text-center text-muted py-3">
                No sector data available
              </div>
            </div>
          </div>
        </div>

        <!-- Market Cap Allocation -->
        <div class="col-md-6">
          <div class="card h-100">
            <div class="card-header">
              <h6 class="mb-0">
                <i class="bi bi-building me-2"></i>
                Market Cap Allocation
              </h6>
            </div>
            <div class="card-body">
              <div v-if="analysis.marketCapAllocation?.length" class="allocation-list">
                <div
                  v-for="(cap, index) in analysis.marketCapAllocation"
                  :key="cap.name"
                  class="allocation-item mb-2"
                >
                  <div class="d-flex justify-content-between mb-1">
                    <span class="small fw-medium">
                      <span class="badge me-1" :class="getCapBadgeClass(cap.name)">
                        {{ cap.name }}
                      </span>
                    </span>
                    <span class="small text-muted">{{ cap.percent.toFixed(1) }}% ({{ cap.count }})</span>
                  </div>
                  <div class="progress" style="height: 8px;">
                    <div
                      class="progress-bar"
                      :style="{ width: cap.percent + '%', backgroundColor: getCapColor(cap.name) }"
                    ></div>
                  </div>
                </div>
              </div>
              <div v-else class="text-center text-muted py-3">
                No market cap data available
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Risk & Concentration -->
      <div class="row g-4 mb-4">
        <div class="col-md-6">
          <div class="card h-100">
            <div class="card-header">
              <h6 class="mb-0">
                <i class="bi bi-shield-exclamation me-2"></i>
                Risk Metrics
              </h6>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-6">
                  <div class="metric-box p-3 rounded bg-light">
                    <div class="small text-muted">Concentration</div>
                    <div class="h5 mb-0" :class="getConcentrationClass(analysis.topHoldingPercent)">
                      {{ analysis.topHoldingPercent?.toFixed(1) || 0 }}%
                    </div>
                    <div class="small text-muted">in top holding</div>
                  </div>
                </div>
                <div class="col-6">
                  <div class="metric-box p-3 rounded bg-light">
                    <div class="small text-muted">Top 3 Holdings</div>
                    <div class="h5 mb-0" :class="getConcentrationClass(analysis.top3Percent)">
                      {{ analysis.top3Percent?.toFixed(1) || 0 }}%
                    </div>
                    <div class="small text-muted">of portfolio</div>
                  </div>
                </div>
                <div class="col-6">
                  <div class="metric-box p-3 rounded bg-light">
                    <div class="small text-muted">Positions</div>
                    <div class="h5 mb-0">{{ holdings.length }}</div>
                    <div class="small text-muted">stocks</div>
                  </div>
                </div>
                <div class="col-6">
                  <div class="metric-box p-3 rounded bg-light">
                    <div class="small text-muted">Avg Position</div>
                    <div class="h5 mb-0">{{ formatPrice(analysis.avgPositionSize) }}</div>
                    <div class="small text-muted">per stock</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Top Holdings -->
        <div class="col-md-6">
          <div class="card h-100">
            <div class="card-header">
              <h6 class="mb-0">
                <i class="bi bi-trophy me-2"></i>
                Top Holdings
              </h6>
            </div>
            <div class="card-body p-0">
              <table class="table table-sm mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Symbol</th>
                    <th class="text-end">Value</th>
                    <th class="text-end">Weight</th>
                    <th class="text-end">P/L</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="holding in analysis.topHoldings"
                    :key="holding.symbol"
                    class="cursor-pointer"
                    @click="goToStock(holding.symbol)"
                  >
                    <td class="fw-medium">{{ holding.symbol }}</td>
                    <td class="text-end">{{ formatPrice(holding.marketValue) }}</td>
                    <td class="text-end">{{ holding.weight.toFixed(1) }}%</td>
                    <td class="text-end" :class="getPLClass(holding.plPercent)">
                      {{ formatPercent(holding.plPercent) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Performance Section -->
      <div class="row g-4 mb-4">
        <!-- Best Performers -->
        <div class="col-md-6">
          <div class="card h-100">
            <div class="card-header bg-success-subtle">
              <h6 class="mb-0 text-success">
                <i class="bi bi-graph-up-arrow me-2"></i>
                Best Performers
              </h6>
            </div>
            <div class="card-body p-0">
              <table class="table table-sm mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Symbol</th>
                    <th class="text-end">Gain/Loss</th>
                    <th class="text-end">Return</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="stock in analysis.bestPerformers"
                    :key="stock.symbol"
                    class="cursor-pointer"
                    @click="goToStock(stock.symbol)"
                  >
                    <td>
                      <span class="fw-medium">{{ stock.symbol }}</span>
                    </td>
                    <td class="text-end text-success">{{ formatPL(stock.pl) }}</td>
                    <td class="text-end">
                      <span class="badge bg-success">{{ formatPercent(stock.plPercent) }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Worst Performers -->
        <div class="col-md-6">
          <div class="card h-100">
            <div class="card-header bg-danger-subtle">
              <h6 class="mb-0 text-danger">
                <i class="bi bi-graph-down-arrow me-2"></i>
                Worst Performers
              </h6>
            </div>
            <div class="card-body p-0">
              <table class="table table-sm mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Symbol</th>
                    <th class="text-end">Gain/Loss</th>
                    <th class="text-end">Return</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="stock in analysis.worstPerformers"
                    :key="stock.symbol"
                    class="cursor-pointer"
                    @click="goToStock(stock.symbol)"
                  >
                    <td>
                      <span class="fw-medium">{{ stock.symbol }}</span>
                    </td>
                    <td class="text-end text-danger">{{ formatPL(stock.pl) }}</td>
                    <td class="text-end">
                      <span class="badge bg-danger">{{ formatPercent(stock.plPercent) }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Valuation & Targets Section -->
      <div class="row g-4 mb-4">
        <!-- Valuation Table -->
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h6 class="mb-0">
                <i class="bi bi-calculator me-2"></i>
                Valuation & Analyst Targets
              </h6>
            </div>
            <div class="card-body p-0">
              <div class="table-responsive">
                <table class="table table-sm table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Symbol</th>
                      <th class="text-end">Current</th>
                      <th class="text-end">P/E</th>
                      <th class="text-end">P/B</th>
                      <th class="text-end">Beta</th>
                      <th class="text-end">Div Yield</th>
                      <th class="text-end">Analyst Target</th>
                      <th class="text-end">Upside</th>
                      <th class="text-center">Rating</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="stock in analysis.valuationData"
                      :key="stock.symbol"
                      class="cursor-pointer"
                      @click="goToStock(stock.symbol)"
                    >
                      <td class="fw-medium">{{ stock.symbol }}</td>
                      <td class="text-end">{{ formatPrice(stock.currentPrice) }}</td>
                      <td class="text-end">{{ stock.pe?.toFixed(1) || '-' }}</td>
                      <td class="text-end">{{ stock.pb?.toFixed(2) || '-' }}</td>
                      <td class="text-end" :class="getBetaClass(stock.beta)">
                        {{ stock.beta?.toFixed(2) || '-' }}
                      </td>
                      <td class="text-end">
                        <span v-if="stock.dividendYield" class="text-info">
                          {{ (stock.dividendYield * 100).toFixed(2) }}%
                        </span>
                        <span v-else class="text-muted">-</span>
                      </td>
                      <td class="text-end">{{ formatPrice(stock.analystTarget) }}</td>
                      <td class="text-end" :class="getPLClass(stock.upside)">
                        {{ stock.upside ? formatPercent(stock.upside) : '-' }}
                      </td>
                      <td class="text-center">
                        <span
                          v-if="stock.recommendation"
                          class="badge"
                          :class="getRatingClass(stock.recommendation)"
                        >
                          {{ formatRating(stock.recommendation) }}
                        </span>
                        <span v-else class="text-muted">-</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Income Section -->
      <div class="row g-4 mb-4" v-if="analysis.dividendStocks?.length">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h6 class="mb-0">
                <i class="bi bi-cash-coin me-2"></i>
                Dividend Income
              </h6>
            </div>
            <div class="card-body p-0">
              <div class="table-responsive">
                <table class="table table-sm table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Symbol</th>
                      <th class="text-end">Shares</th>
                      <th class="text-end">Div Rate</th>
                      <th class="text-end">Yield</th>
                      <th class="text-end">Annual Income</th>
                      <th class="text-end">% of Income</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="stock in analysis.dividendStocks"
                      :key="stock.symbol"
                      class="cursor-pointer"
                      @click="goToStock(stock.symbol)"
                    >
                      <td class="fw-medium">{{ stock.symbol }}</td>
                      <td class="text-end">{{ stock.shares.toLocaleString() }}</td>
                      <td class="text-end">${{ stock.dividendRate?.toFixed(2) || '-' }}</td>
                      <td class="text-end text-info">{{ (stock.dividendYield * 100).toFixed(2) }}%</td>
                      <td class="text-end text-success">{{ formatPrice(stock.annualIncome) }}</td>
                      <td class="text-end">{{ stock.incomePercent.toFixed(1) }}%</td>
                    </tr>
                  </tbody>
                  <tfoot class="table-light fw-bold">
                    <tr>
                      <td colspan="4">Total Annual Income</td>
                      <td class="text-end text-success">{{ formatPrice(analysis.annualIncome) }}</td>
                      <td class="text-end">100%</td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { stocksApi, pricesApi } from '@/api'

export default {
  name: 'PortfolioAnalyzer',
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const error = ref(null)
    const holdings = ref([])
    const analysis = reactive({
      totalValue: 0,
      totalCostBasis: 0,
      totalPL: 0,
      totalPLPercent: 0,
      portfolioBeta: null,
      avgDividendYield: 0,
      annualIncome: 0,
      avgPE: null,
      diversificationScore: null,
      sectors: [],
      sectorAllocation: [],
      marketCapAllocation: [],
      topHoldingPercent: 0,
      top3Percent: 0,
      avgPositionSize: 0,
      topHoldings: [],
      bestPerformers: [],
      worstPerformers: [],
      valuationData: [],
      dividendStocks: []
    })

    const fetchData = async () => {
      loading.value = true
      error.value = null

      try {
        // Fetch all stocks with prices
        const response = await stocksApi.getAll({ include_prices: true })
        const stocks = response.data.stocks

        // Filter to only stocks with holdings
        const stocksWithHoldings = stocks.filter(s => s.holding)
        holdings.value = stocksWithHoldings

        if (!stocksWithHoldings.length) {
          loading.value = false
          return
        }

        // Fetch fundamental data for all stocks in batch
        const symbols = stocksWithHoldings.map(s => s.symbol)
        let fundamentalData = {}

        try {
          const fundamentalRes = await pricesApi.getBatchFundamental(symbols)
          fundamentalData = fundamentalRes.data.data || {}
        } catch (err) {
          console.warn('Could not fetch fundamental data:', err)
        }

        // Process holdings data
        const holdingsData = stocksWithHoldings.map(stock => {
          const holding = stock.holding
          const currentPrice = stock.current_price || 0
          const avgCost = holding.average_cost || 0
          const shares = holding.shares || 0
          const marketValue = shares * currentPrice
          const costBasis = shares * avgCost
          const pl = avgCost ? marketValue - costBasis : 0
          const plPercent = costBasis > 0 ? (pl / costBasis) * 100 : 0
          const fundamental = fundamentalData[stock.symbol]

          return {
            symbol: stock.symbol,
            companyName: stock.company_name,
            shares,
            avgCost,
            currentPrice,
            marketValue,
            costBasis,
            pl,
            plPercent,
            weight: 0, // Calculate after
            // Fundamental data
            sector: fundamental?.sector || null,
            industry: fundamental?.industry || null,
            marketCap: fundamental?.market_cap || null,
            beta: fundamental?.beta || null,
            pe: fundamental?.pe_ratio || null,
            pb: fundamental?.price_to_book || null,
            dividendRate: fundamental?.dividend_rate || null,
            dividendYield: fundamental?.dividend_yield || null,
            analystTarget: fundamental?.target_mean_price || null,
            recommendation: fundamental?.recommendation || null
          }
        })

        // Calculate total value and weights
        const totalValue = holdingsData.reduce((sum, h) => sum + h.marketValue, 0)
        holdingsData.forEach(h => {
          h.weight = totalValue > 0 ? (h.marketValue / totalValue) * 100 : 0
        })

        // Calculate portfolio metrics
        const totalCostBasis = holdingsData.reduce((sum, h) => sum + h.costBasis, 0)
        const totalPL = holdingsData.reduce((sum, h) => sum + h.pl, 0)
        const totalPLPercent = totalCostBasis > 0 ? (totalPL / totalCostBasis) * 100 : 0

        // Calculate weighted beta
        let weightedBeta = 0
        let betaWeight = 0
        holdingsData.forEach(h => {
          if (h.beta) {
            weightedBeta += h.beta * h.weight
            betaWeight += h.weight
          }
        })
        const portfolioBeta = betaWeight > 0 ? weightedBeta / betaWeight : null

        // Calculate weighted P/E
        let weightedPE = 0
        let peWeight = 0
        holdingsData.forEach(h => {
          if (h.pe && h.pe > 0) {
            weightedPE += h.pe * h.weight
            peWeight += h.weight
          }
        })
        const avgPE = peWeight > 0 ? weightedPE / peWeight : null

        // Calculate dividend metrics
        let totalAnnualIncome = 0
        const dividendStocks = []
        holdingsData.forEach(h => {
          if (h.dividendRate && h.dividendRate > 0) {
            const annualIncome = h.shares * h.dividendRate
            totalAnnualIncome += annualIncome
            dividendStocks.push({
              symbol: h.symbol,
              shares: h.shares,
              dividendRate: h.dividendRate,
              dividendYield: h.dividendYield || 0,
              annualIncome,
              incomePercent: 0 // Calculate after
            })
          }
        })
        dividendStocks.forEach(d => {
          d.incomePercent = totalAnnualIncome > 0 ? (d.annualIncome / totalAnnualIncome) * 100 : 0
        })
        dividendStocks.sort((a, b) => b.annualIncome - a.annualIncome)

        const avgDividendYield = totalValue > 0 ? (totalAnnualIncome / totalValue) * 100 : 0

        // Calculate sector allocation
        const sectorMap = {}
        holdingsData.forEach(h => {
          const sector = h.sector || 'Unknown'
          if (!sectorMap[sector]) {
            sectorMap[sector] = { value: 0, count: 0 }
          }
          sectorMap[sector].value += h.marketValue
          sectorMap[sector].count++
        })
        const sectorAllocation = Object.entries(sectorMap)
          .map(([name, data]) => ({
            name,
            value: data.value,
            count: data.count,
            percent: totalValue > 0 ? (data.value / totalValue) * 100 : 0
          }))
          .sort((a, b) => b.percent - a.percent)

        // Calculate market cap allocation
        const capCategories = { 'Large Cap': 0, 'Mid Cap': 0, 'Small Cap': 0, 'Unknown': 0 }
        const capCounts = { 'Large Cap': 0, 'Mid Cap': 0, 'Small Cap': 0, 'Unknown': 0 }
        holdingsData.forEach(h => {
          let category = 'Unknown'
          if (h.marketCap) {
            if (h.marketCap >= 10e9) category = 'Large Cap'
            else if (h.marketCap >= 2e9) category = 'Mid Cap'
            else category = 'Small Cap'
          }
          capCategories[category] += h.marketValue
          capCounts[category]++
        })
        const marketCapAllocation = Object.entries(capCategories)
          .filter(([_, value]) => value > 0)
          .map(([name, value]) => ({
            name,
            value,
            count: capCounts[name],
            percent: totalValue > 0 ? (value / totalValue) * 100 : 0
          }))
          .sort((a, b) => b.percent - a.percent)

        // Calculate concentration metrics
        const sortedByValue = [...holdingsData].sort((a, b) => b.marketValue - a.marketValue)
        const topHoldingPercent = sortedByValue[0]?.weight || 0
        const top3Percent = sortedByValue.slice(0, 3).reduce((sum, h) => sum + h.weight, 0)
        const avgPositionSize = holdingsData.length > 0 ? totalValue / holdingsData.length : 0

        // Calculate diversification score (simple: based on number of sectors and concentration)
        const numSectors = sectorAllocation.filter(s => s.name !== 'Unknown').length
        let diversificationScore = 'Poor'
        if (numSectors >= 8 && topHoldingPercent < 15) diversificationScore = 'Excellent'
        else if (numSectors >= 5 && topHoldingPercent < 25) diversificationScore = 'Good'
        else if (numSectors >= 3 && topHoldingPercent < 35) diversificationScore = 'Fair'

        // Top holdings
        const topHoldings = sortedByValue.slice(0, 5)

        // Best and worst performers
        const sortedByPerformance = [...holdingsData].sort((a, b) => b.plPercent - a.plPercent)
        const bestPerformers = sortedByPerformance.filter(h => h.plPercent > 0).slice(0, 5)
        const worstPerformers = sortedByPerformance.filter(h => h.plPercent < 0).slice(-5).reverse()

        // Valuation data (upside calculation)
        const valuationData = holdingsData.map(h => ({
          symbol: h.symbol,
          currentPrice: h.currentPrice,
          pe: h.pe,
          pb: h.pb,
          beta: h.beta,
          dividendYield: h.dividendYield,
          analystTarget: h.analystTarget,
          upside: h.analystTarget && h.currentPrice
            ? ((h.analystTarget - h.currentPrice) / h.currentPrice) * 100
            : null,
          recommendation: h.recommendation
        })).sort((a, b) => (b.upside || -100) - (a.upside || -100))

        // Update reactive analysis object
        Object.assign(analysis, {
          totalValue,
          totalCostBasis,
          totalPL,
          totalPLPercent,
          portfolioBeta,
          avgDividendYield,
          annualIncome: totalAnnualIncome,
          avgPE,
          diversificationScore,
          sectors: sectorAllocation.map(s => s.name),
          sectorAllocation,
          marketCapAllocation,
          topHoldingPercent,
          top3Percent,
          avgPositionSize,
          topHoldings,
          bestPerformers,
          worstPerformers,
          valuationData,
          dividendStocks
        })

      } catch (err) {
        console.error('Error analyzing portfolio:', err)
        error.value = err.message || 'Failed to analyze portfolio'
      } finally {
        loading.value = false
      }
    }

    const goToStock = (symbol) => {
      router.push(`/stock/${symbol}`)
    }

    // Formatting helpers
    const formatPrice = (value) => {
      if (value === null || value === undefined) return '-'
      return '$' + value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }

    const formatPL = (value) => {
      if (value === null || value === undefined) return '-'
      const prefix = value >= 0 ? '+' : ''
      return prefix + '$' + Math.abs(value).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }

    const formatPercent = (value) => {
      if (value === null || value === undefined) return '-'
      const prefix = value >= 0 ? '+' : ''
      return prefix + value.toFixed(2) + '%'
    }

    const getPLClass = (value) => {
      if (value === null || value === undefined) return ''
      return value >= 0 ? 'text-success' : 'text-danger'
    }

    const getBetaClass = (beta) => {
      if (!beta) return ''
      if (beta > 1.5) return 'text-danger'
      if (beta > 1.2) return 'text-warning'
      if (beta < 0.8) return 'text-info'
      return ''
    }

    const getBetaLabel = (beta) => {
      if (!beta) return '-'
      if (beta > 1.5) return 'High Risk'
      if (beta > 1.2) return 'Above Avg'
      if (beta > 0.8) return 'Average'
      return 'Low Risk'
    }

    const getDiversificationClass = (score) => {
      if (score === 'Excellent') return 'text-success'
      if (score === 'Good') return 'text-info'
      if (score === 'Fair') return 'text-warning'
      return 'text-danger'
    }

    const getConcentrationClass = (percent) => {
      if (percent > 30) return 'text-danger'
      if (percent > 20) return 'text-warning'
      return 'text-success'
    }

    const getAllocationColor = (index) => {
      const colors = [
        '#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545',
        '#fd7e14', '#ffc107', '#198754', '#20c997', '#0dcaf0'
      ]
      return colors[index % colors.length]
    }

    const getCapBadgeClass = (cap) => {
      if (cap === 'Large Cap') return 'bg-primary'
      if (cap === 'Mid Cap') return 'bg-info'
      if (cap === 'Small Cap') return 'bg-warning text-dark'
      return 'bg-secondary'
    }

    const getCapColor = (cap) => {
      if (cap === 'Large Cap') return '#0d6efd'
      if (cap === 'Mid Cap') return '#0dcaf0'
      if (cap === 'Small Cap') return '#ffc107'
      return '#6c757d'
    }

    const getRatingClass = (rating) => {
      if (!rating) return 'bg-secondary'
      const r = rating.toLowerCase()
      if (r.includes('strong_buy') || r.includes('buy')) return 'bg-success'
      if (r.includes('hold') || r.includes('neutral')) return 'bg-warning text-dark'
      if (r.includes('sell') || r.includes('underperform')) return 'bg-danger'
      return 'bg-secondary'
    }

    const formatRating = (rating) => {
      if (!rating) return '-'
      return rating.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }

    onMounted(() => {
      fetchData()
    })

    return {
      loading,
      error,
      holdings,
      analysis,
      fetchData,
      goToStock,
      formatPrice,
      formatPL,
      formatPercent,
      getPLClass,
      getBetaClass,
      getBetaLabel,
      getDiversificationClass,
      getConcentrationClass,
      getAllocationColor,
      getCapBadgeClass,
      getCapColor,
      getRatingClass,
      formatRating
    }
  }
}
</script>

<style scoped>
.analyzer-view {
  max-width: 1400px;
  margin: 0 auto;
}

.summary-card {
  border: none;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  transition: transform 0.2s;
}

.summary-card:hover {
  transform: translateY(-2px);
}

.summary-label {
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.7rem;
}

.summary-value {
  font-weight: 600;
}

.allocation-item .progress {
  border-radius: 4px;
}

.metric-box {
  transition: transform 0.2s;
}

.metric-box:hover {
  transform: translateY(-2px);
}

.cursor-pointer {
  cursor: pointer;
}

.cursor-pointer:hover {
  background-color: #f8f9fa !important;
}

/* Bootstrap 5.3+ subtle backgrounds fallback */
.bg-success-subtle {
  background-color: rgba(25, 135, 84, 0.15) !important;
}

.bg-danger-subtle {
  background-color: rgba(220, 53, 69, 0.15) !important;
}

.bg-warning-subtle {
  background-color: rgba(255, 193, 7, 0.2) !important;
}

/* Responsive */
@media (max-width: 768px) {
  .table {
    font-size: 0.8rem;
  }
}
</style>
