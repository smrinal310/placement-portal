<template>
  <Transition name="modal">
    <div v-if="show" class="app-modal__overlay" @click.self="$emit('cancel')">
      <div class="app-modal__card" role="dialog" aria-modal="true">

        <div class="app-modal__header">
          <div class="app-modal__title-group">
            <div class="app-modal__icon">
              <i :class="headerIcon"></i>
            </div>
            <h3 class="app-modal__title">{{ title }}</h3>
          </div>
          <button class="app-modal__close" @click="$emit('cancel')" :disabled="loading" aria-label="Close">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <div class="app-modal__body">
          <div class="app-modal__summary">
            <slot></slot>
          </div>

          <div v-if="warningMessage" class="app-modal__warning">
            <i class="bi bi-info-circle-fill app-modal__warning-icon"></i>
            <span class="app-modal__warning-text">{{ warningMessage }}</span>
          </div>
        </div>

        <div class="app-modal__footer">
          <AppButton variant="outline" :disabled="loading" @click="$emit('cancel')">
            Cancel
          </AppButton>
          <AppButton :variant="confirmVariant" :disabled="loading" :loading="loading" @click="$emit('confirm')">
            {{ confirmLabel }}
          </AppButton>
        </div>

      </div>
    </div>
  </Transition>
</template>

<script setup>
import AppButton from './AppButton.vue'

defineProps({
  show: {
    type: Boolean,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  headerIcon: {
    type: String,
    default: 'bi bi-shield-check'
  },
  confirmLabel: {
    type: String,
    default: 'Confirm'
  },
  confirmVariant: {
    type: String,
    default: 'primary'
  },
  warningMessage: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['confirm', 'cancel'])
</script>

<style scoped>
.app-modal__overlay {
  position: fixed;
  inset: 0;
  /* Hardcoded rgba exemption: overlay backdrop */
  background-color: rgba(15, 23, 42, 0.5);
  z-index: var(--z-modal);
  display: flex;
  align-items: center;
  justify-content: center;
}

.app-modal__card {
  width: 100%;
  max-width: 520px;
  background-color: var(--color-card-bg);
  border-radius: var(--border-radius-xl);
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
}

.app-modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--card-padding);
  padding-bottom: var(--space-4);
}

.app-modal__title-group {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.app-modal__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: var(--space-10);
  height: var(--space-10);
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  border-radius: var(--border-radius-pill);
  font-size: var(--font-size-lg);
}

.app-modal__title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.app-modal__close {
  background: transparent;
  border: none;
  font-size: var(--font-size-lg);
  color: var(--color-text-muted);
  cursor: pointer;
  padding: var(--space-1);
  transition: color var(--transition-fast);
  border-radius: var(--border-radius-sm);
  outline: none;
}

.app-modal__close:hover:not(:disabled) {
  color: var(--color-text-primary);
}

.app-modal__close:focus-visible {
  box-shadow: 0 0 0 calc(var(--border-width) * 2) var(--color-border);
}

.app-modal__close:disabled {
  cursor: not-allowed;
  opacity: var(--opacity-disabled);
}

.app-modal__body {
  padding-inline: var(--card-padding);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.app-modal__summary {
  background-color: var(--color-gray-50);
  border-radius: var(--border-radius-lg);
  padding: var(--space-4);
}

.app-modal__warning {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
}

.app-modal__warning-icon {
  color: var(--color-warning);
  font-size: var(--font-size-md);
  margin-top: calc(var(--space-1) / 2);
}

.app-modal__warning-text {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-base);
}

.app-modal__footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding-top: var(--space-4);
  margin: var(--card-padding);
  margin-top: var(--space-6);
  border-top: var(--border-width) solid var(--color-border);
}

.modal-enter-active,
.modal-leave-active {
  transition: all var(--transition-base);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .app-modal__card,
.modal-leave-to .app-modal__card {
  transform: scale(0.95);
}
</style>
