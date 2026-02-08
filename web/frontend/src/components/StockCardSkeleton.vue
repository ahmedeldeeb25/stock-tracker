<template>
  <article class="card stock-card h-100" aria-busy="true">
    <div class="card-body">
      <!-- Stock Symbol Skeleton -->
      <div class="skeleton skeleton-heading"></div>

      <!-- Company Name Skeleton -->
      <div class="skeleton skeleton-text" style="width: 70%; height: 0.83rem;"></div>

      <!-- Price Skeleton -->
      <div class="skeleton skeleton-price mt-3"></div>

      <!-- Price Change Skeleton -->
      <div class="skeleton skeleton-text" style="width: 50%; height: 0.9rem; margin-top: 0.25rem;"></div>

      <!-- After Hours Skeleton -->
      <div class="skeleton skeleton-text" style="width: 60%; height: 0.75rem; margin-top: 0.5rem;"></div>

      <!-- Tags Skeleton -->
      <div class="d-flex gap-2 mt-3">
        <div class="skeleton skeleton-badge"></div>
        <div class="skeleton skeleton-badge"></div>
      </div>

      <!-- Footer Info Skeleton -->
      <div class="d-flex justify-content-between align-items-center mt-3">
        <div class="skeleton skeleton-text" style="width: 40%; height: 0.83rem;"></div>
        <div class="skeleton skeleton-text" style="width: 30%; height: 0.83rem;"></div>
      </div>
    </div>
    <span class="visually-hidden">Loading stock information...</span>
  </article>
</template>

<script>
export default {
  name: 'StockCardSkeleton'
}
</script>

<style scoped>
.stock-card {
  transition: all var(--duration-fast) var(--ease-out);
  border: var(--card-border);
  border-radius: var(--card-radius);
}
</style>
