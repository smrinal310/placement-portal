<template>
  <div class="app-empty-state">
    <i :class="[icon, 'app-empty-state__icon']" aria-hidden="true"></i>
    <h3 class="app-empty-state__title">{{ title }}</h3>
    <p v-if="subtitle" class="app-empty-state__subtitle">{{ subtitle }}</p>
    <button v-if="actionLabel" class="app-empty-state__action-btn" @click="$emit('action')">
      {{ actionLabel }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  icon: {
    type: String,
    default: 'bi bi-inbox'
  },
  title: {
    type: String,
    default: 'No results found'
  },
  subtitle: {
    type: String,
    default: ''
  },
  actionLabel: {
    type: String,
    default: ''
  }
})

defineEmits(['action'])
</script>

<style scoped>
.app-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding-block: var(--space-12);
  width: 100%;
}

.app-empty-state__icon {
  font-size: var(--empty-state-icon-size);
  color: var(--color-gray-300);
  margin-bottom: var(--space-4);
  line-height: 1;
}

.app-empty-state__title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin: 0;
  margin-bottom: var(--space-2);
}

.app-empty-state__subtitle {
  font-size: var(--font-size-base);
  color: var(--color-text-muted);
  margin: 0;
  margin-bottom: var(--space-6);
  max-width: 400px;
}

.app-empty-state__action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  border: var(--border-width) solid transparent;
  border-radius: var(--border-radius-md);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
  outline: none;
  background-color: var(--color-primary);
  color: var(--color-white);
  padding-block: var(--space-2);
  padding-inline: var(--space-4);
  font-size: var(--font-size-sm);
}

.app-empty-state__action-btn:hover {
  background-color: var(--color-primary-hover);
}

.app-empty-state__action-btn:focus {
  box-shadow: 0 0 0 var(--space-1) var(--color-primary-light);
}

.app-empty-state__action-btn:active {
  transform: scale(var(--button-active-scale));
}
</style>
