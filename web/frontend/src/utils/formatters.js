// Format price to 2 decimal places with $ symbol
export function formatPrice(price) {
  if (price === null || price === undefined) return 'N/A'
  return `$${parseFloat(price).toFixed(2)}`
}

// Format percentage to 2 decimal places with % symbol
export function formatPercent(percent) {
  if (percent === null || percent === undefined) return 'N/A'
  const value = parseFloat(percent).toFixed(2)
  return `${value > 0 ? '+' : ''}${value}%`
}

// Format date to readable string
export function formatDate(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// Format datetime to readable string
export function formatDateTime(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Get color class for price change
export function getPriceChangeClass(value) {
  if (value > 0) return 'price-positive'
  if (value < 0) return 'price-negative'
  return 'text-muted'
}

// Get badge class for target type
export function getTargetBadgeClass(targetType) {
  const classes = {
    'Buy': 'bg-success',
    'Sell': 'bg-danger',
    'DCA': 'bg-info',
    'Trim': 'bg-warning'
  }
  return classes[targetType] || 'bg-secondary'
}

// Format number with commas (for shares)
export function formatNumber(num) {
  if (num === null || num === undefined) return 'N/A'
  return parseFloat(num).toLocaleString('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 6
  })
}

// Format gain/loss with + or - sign
export function formatGainLoss(value) {
  if (value === null || value === undefined) return 'N/A'
  const formatted = Math.abs(value).toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD'
  })
  return value >= 0 ? `+${formatted}` : `-${formatted}`
}

// Get CSS class for gain/loss display
export function getGainLossClass(value) {
  if (value > 0) return 'text-success'
  if (value < 0) return 'text-danger'
  return 'text-muted'
}
