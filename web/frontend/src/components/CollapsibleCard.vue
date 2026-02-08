<template>
  <div class="card mb-4">
    <div
      class="card-header d-flex justify-content-between align-items-center collapsible-header"
      :class="{ 'collapsed': !isOpen }"
      @click="toggle"
      role="button"
      :aria-expanded="isOpen"
      :aria-controls="collapseId"
      tabindex="0"
      @keydown.enter="toggle"
      @keydown.space.prevent="toggle"
    >
      <h5 class="mb-0">
        <slot name="title">
          <i v-if="icon" :class="icon" class="me-2" aria-hidden="true"></i>
          {{ title }}
        </slot>
      </h5>
      <div class="d-flex align-items-center gap-2">
        <slot name="actions"></slot>
        <i
          class="bi collapse-icon"
          :class="isOpen ? 'bi-chevron-up' : 'bi-chevron-down'"
          aria-hidden="true"
        ></i>
      </div>
    </div>
    <div
      :id="collapseId"
      class="collapse"
      :class="{ 'show': isOpen }"
      ref="collapseElement"
    >
      <div class="card-body" :class="bodyClass">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: ''
  },
  defaultOpen: {
    type: Boolean,
    default: true
  },
  bodyClass: {
    type: String,
    default: ''
  },
  storageKey: {
    type: String,
    default: null
  }
})

const collapseElement = ref(null)
const isOpen = ref(props.defaultOpen)

// Generate unique ID for collapse functionality
const collapseId = computed(() => {
  return `collapse-${props.storageKey || Math.random().toString(36).substring(7)}`
})

// Load saved state from localStorage if storageKey is provided
onMounted(() => {
  if (props.storageKey) {
    const savedState = localStorage.getItem(`collapse-${props.storageKey}`)
    if (savedState !== null) {
      isOpen.value = savedState === 'true'
    }
  }
})

// Save state to localStorage when it changes
watch(isOpen, (newValue) => {
  if (props.storageKey) {
    localStorage.setItem(`collapse-${props.storageKey}`, newValue.toString())
  }
})

const toggle = () => {
  isOpen.value = !isOpen.value
}

defineExpose({
  toggle,
  isOpen
})
</script>

<style scoped>
.collapsible-header {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s ease;
}

.collapsible-header:hover {
  background-color: #f8f9fa;
}

.collapsible-header:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: -2px;
}

.collapse-icon {
  font-size: 1.25rem;
  transition: transform 0.3s ease;
  color: #6c757d;
}

.collapsible-header:hover .collapse-icon {
  color: var(--color-primary);
}

.collapsed .collapse-icon {
  transform: rotate(0deg);
}

.collapse {
  transition: height 0.3s ease;
}

.collapse.show {
  display: block;
}

.collapse:not(.show) {
  display: none;
}

/* Animation for smooth collapse */
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-10px);
  }
}

.collapse.show {
  animation: slideDown 0.3s ease;
}
</style>
