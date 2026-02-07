<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
      <div class="container-fluid">
        <router-link to="/" class="navbar-brand">
          <i class="bi bi-graph-up-arrow me-2"></i>
          Stock Tracker
        </router-link>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <router-link to="/" class="nav-link">
                <i class="bi bi-speedometer2 me-1"></i>
                Dashboard
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/alerts" class="nav-link">
                <i class="bi bi-bell me-1"></i>
                Alert History
              </router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <div class="container-fluid">
      <router-view />
    </div>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>
