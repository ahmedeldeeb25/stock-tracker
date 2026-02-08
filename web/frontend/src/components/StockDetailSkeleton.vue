<template>
  <div aria-busy="true" role="status">
    <!-- Header Skeleton -->
    <div class="mb-4">
      <div class="skeleton skeleton-text" style="width: 150px; height: 0.875rem; margin-bottom: 0.5rem;"></div>
      <div class="d-flex align-items-center gap-2 mb-2">
        <div class="skeleton skeleton-heading" style="width: 120px;"></div>
        <div class="skeleton" style="width: 40px; height: 32px;"></div>
      </div>
      <div class="skeleton skeleton-text" style="width: 200px; height: 0.875rem;"></div>
    </div>

    <!-- Price Section Skeleton -->
    <div class="text-end mb-4">
      <div class="skeleton" style="width: 150px; height: 2rem; margin-left: auto;"></div>
      <div class="skeleton skeleton-text" style="width: 100px; height: 0.875rem; margin-left: auto; margin-top: 0.5rem;"></div>
      <div class="skeleton" style="width: 80px; height: 28px; margin-left: auto; margin-top: 0.5rem;"></div>
    </div>

    <!-- Tags Skeleton -->
    <div class="d-flex gap-2 mb-4">
      <div class="skeleton skeleton-badge"></div>
      <div class="skeleton skeleton-badge"></div>
      <div class="skeleton skeleton-badge"></div>
    </div>

    <div class="row">
      <!-- Left Column Skeleton -->
      <div class="col-md-8">
        <!-- Chart Card Skeleton -->
        <div class="card mb-4">
          <div class="card-header">
            <div class="skeleton skeleton-text" style="width: 100px; height: 1.17rem;"></div>
          </div>
          <div class="card-body p-0">
            <div class="skeleton" style="width: 100%; height: 500px;"></div>
          </div>
        </div>

        <!-- Targets Card Skeleton -->
        <div class="card mb-4">
          <div class="card-header">
            <div class="skeleton skeleton-text" style="width: 150px; height: 1.17rem;"></div>
          </div>
          <div class="card-body">
            <div v-for="n in 3" :key="`target-${n}`" class="p-3 mb-3 border rounded">
              <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                  <div class="skeleton skeleton-badge mb-2"></div>
                  <div class="skeleton" style="width: 100px; height: 1.5rem;"></div>
                </div>
                <div class="skeleton" style="width: 120px; height: 1.5rem;"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column Skeleton -->
      <div class="col-md-4">
        <div class="card">
          <div class="card-header">
            <div class="skeleton skeleton-text" style="width: 130px; height: 1.17rem;"></div>
          </div>
          <div class="card-body">
            <div v-for="n in 4" :key="`note-${n}`" class="p-3 mb-3 border rounded">
              <div class="skeleton skeleton-text" style="width: 80%; height: 1rem; margin-bottom: 0.5rem;"></div>
              <div class="skeleton skeleton-text" style="width: 60%; height: 0.75rem;"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <span class="visually-hidden">Loading stock details...</span>
  </div>
</template>

<script>
export default {
  name: 'StockDetailSkeleton'
}
</script>

<style scoped>
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s ease-in-out infinite;
  border-radius: 6px;
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
