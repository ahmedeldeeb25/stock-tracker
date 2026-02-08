<template>
  <div
    class="skeleton-loader"
    :class="[
      `skeleton-${variant}`,
      { 'skeleton-animated': animated }
    ]"
    :style="customStyles"
    role="status"
    aria-busy="true"
    :aria-label="ariaLabel"
  >
    <span class="visually-hidden">{{ ariaLabel }}</span>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'SkeletonLoader',
  props: {
    /**
     * Variant of skeleton loader
     * - text: Single line of text
     * - heading: Larger text (for headings)
     * - circle: Circular shape (for avatars)
     * - rectangle: Rectangular shape (for images)
     * - card: Card layout with multiple elements
     */
    variant: {
      type: String,
      default: 'text',
      validator: (value) => ['text', 'heading', 'circle', 'rectangle', 'card'].includes(value)
    },

    /**
     * Width of skeleton (CSS value: px, %, rem, etc.)
     */
    width: {
      type: String,
      default: null
    },

    /**
     * Height of skeleton (CSS value: px, %, rem, etc.)
     */
    height: {
      type: String,
      default: null
    },

    /**
     * Border radius (CSS value)
     */
    borderRadius: {
      type: String,
      default: null
    },

    /**
     * Enable/disable animation
     */
    animated: {
      type: Boolean,
      default: true
    },

    /**
     * Number of lines (for text variant)
     */
    lines: {
      type: Number,
      default: 1
    },

    /**
     * ARIA label for screen readers
     */
    ariaLabel: {
      type: String,
      default: 'Loading content...'
    }
  },
  setup(props) {
    /**
     * Compute custom styles based on props
     */
    const customStyles = computed(() => {
      const styles = {}

      if (props.width) {
        styles.width = props.width
      }

      if (props.height) {
        styles.height = props.height
      }

      if (props.borderRadius) {
        styles.borderRadius = props.borderRadius
      }

      return styles
    })

    return {
      customStyles
    }
  }
}
</script>

<style scoped>
/* Base skeleton styles */
.skeleton-loader {
  background: linear-gradient(
    90deg,
    var(--color-gray-100) 0%,
    var(--color-gray-200) 50%,
    var(--color-gray-100) 100%
  );
  background-size: 200% 100%;
  border-radius: var(--btn-radius);
  display: block;
}

/* Animation */
.skeleton-animated {
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

@keyframes skeleton-pulse {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* Variants */
.skeleton-text {
  width: 100%;
  height: 1rem;
  margin-bottom: 0.5rem;
}

.skeleton-heading {
  width: 60%;
  height: 1.67rem;
  margin-bottom: 0.75rem;
}

.skeleton-circle {
  width: 64px;
  height: 64px;
  border-radius: 50%;
}

.skeleton-rectangle {
  width: 100%;
  height: 200px;
  border-radius: var(--card-radius);
}

.skeleton-card {
  width: 100%;
  height: auto;
  padding: var(--card-padding);
  border-radius: var(--card-radius);
  border: var(--card-border);
  background: white;
}

/* Card skeleton internal structure */
.skeleton-card::before,
.skeleton-card::after {
  content: '';
  display: block;
  background: linear-gradient(
    90deg,
    var(--color-gray-100) 0%,
    var(--color-gray-200) 50%,
    var(--color-gray-100) 100%
  );
  background-size: 200% 100%;
  border-radius: var(--btn-radius);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-card::before {
  width: 40%;
  height: 1.17rem;
  margin-bottom: 0.75rem;
}

.skeleton-card::after {
  width: 60%;
  height: 1.5rem;
  margin-bottom: 0.5rem;
}

/* Multiple lines for text variant */
.skeleton-text:nth-child(2) {
  width: 85%;
}

.skeleton-text:nth-child(3) {
  width: 95%;
}

.skeleton-text:last-child {
  width: 70%;
}

/* Responsive adjustments */
@media (max-width: 767px) {
  .skeleton-heading {
    width: 80%;
  }

  .skeleton-circle {
    width: 48px;
    height: 48px;
  }

  .skeleton-rectangle {
    height: 150px;
  }
}

/* Accessibility */
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>
