<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4" role="navigation" aria-label="Main navigation">
      <div class="container-fluid">
        <router-link to="/" class="navbar-brand">
          <i class="bi bi-graph-up-arrow me-2" aria-hidden="true"></i>
          Stock Tracker
        </router-link>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <router-link to="/" class="nav-link">
                <i class="bi bi-speedometer2 me-1" aria-hidden="true"></i>
                Dashboard
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/portfolio" class="nav-link">
                <i class="bi bi-briefcase me-1" aria-hidden="true"></i>
                Portfolio
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/watchlist" class="nav-link">
                <i class="bi bi-eye me-1" aria-hidden="true"></i>
                Watchlist
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/analyzer" class="nav-link">
                <i class="bi bi-bar-chart-line me-1" aria-hidden="true"></i>
                Analyzer
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/alerts" class="nav-link">
                <i class="bi bi-bell me-1" aria-hidden="true"></i>
                Alerts
              </router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <main class="container-fluid" role="main">
      <router-view />
    </main>

    <!-- Toast Notification Container -->
    <ToastContainer />

    <!-- Confirm Modal -->
    <ConfirmModal />
  </div>
</template>

<script>
import ToastContainer from '@/components/ToastContainer.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'

export default {
  name: 'App',
  components: {
    ToastContainer,
    ConfirmModal
  }
}
</script>
