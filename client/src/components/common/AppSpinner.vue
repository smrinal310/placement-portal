<template>
  <div v-if="fullPage" class="app-spinner-overlay">
    <div class="app-spinner" :class="normalizedSizeClass"></div>
  </div>
  <div v-else class="app-spinner" :class="normalizedSizeClass"></div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  fullPage: {
    type: Boolean,
    default: false
  }
})

const normalizedSize = computed(() => props.size)
const normalizedSizeClass = computed(() => `app-spinner--${normalizedSize.value}`)
</script>

<style scoped>
.app-spinner-overlay {
  position: fixed;
  inset: 0;
  /* Hardcoded rgba exemption: overlay backdrop */
  background-color: rgba(255, 255, 255, 0.7);
  z-index: var(--z-modal);
  display: flex;
  align-items: center;
  justify-content: center;
}

.app-spinner {
  display: inline-block;
  border-radius: var(--border-radius-pill);
  border: 3px solid var(--color-gray-200);
  border-top-color: var(--color-primary);
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

.app-spinner--sm {
  width: var(--spinner-size-sm);
  height: var(--spinner-size-sm);
  border-width: 2px;
}

.app-spinner--md {
  width: var(--spinner-size-md);
  height: var(--spinner-size-md);
}

.app-spinner--lg {
  width: var(--spinner-size-lg);
  height: var(--spinner-size-lg);
  border-width: 4px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
