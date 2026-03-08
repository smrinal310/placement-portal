<template>
  <button class="app-button" :class="[
    variantClass,
    sizeClass,
    {
      'app-button--loading': loading,
      'app-button--disabled': disabled,
    },
  ]" :disabled="disabled || loading" @click="handleClick">
    <span v-if="loading" class="app-button__spinner"></span>
    <i v-if="iconLeft && !loading" :class="iconLeft" class="app-button__icon"></i>
    <slot></slot>
    <i v-if="iconRight && !loading" :class="iconRight" class="app-button__icon"></i>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'outline', 'danger', 'ghost', 'approve'].includes(value),
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md'].includes(value),
  },
  loading: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  iconLeft: {
    type: String,
    default: null,
  },
  iconRight: {
    type: String,
    default: null,
  },
})

const emit = defineEmits(['click'])

const normalizedVariant = computed(() => props.variant)
const normalizedSize = computed(() => props.size)
const normalizedLoading = computed(() => props.loading)
const normalizedDisabled = computed(() => props.disabled)

const variantClass = computed(() =>
  normalizedVariant.value ? `app-button--${normalizedVariant.value}` : null,
)
const sizeClass = computed(() =>
  normalizedSize.value ? `app-button--${normalizedSize.value}` : null,
)

const handleClick = (event) => {
  if (!normalizedLoading.value && !normalizedDisabled.value) {
    emit('click', event)
  }
}
</script>

<style scoped>
.app-button {
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
}

.app-button:focus {
  box-shadow: 0 0 0 var(--space-1) var(--color-primary-light);
}

.app-button:active {
  transform: scale(var(--button-active-scale));
}

.app-button--disabled {
  opacity: var(--opacity-disabled);
  pointer-events: none;
  cursor: not-allowed;
}

.app-button--loading {
  opacity: var(--opacity-loading);
  pointer-events: none;
  cursor: wait;
}

.app-button__spinner {
  width: var(--font-size-md);
  height: var(--font-size-md);
  border: var(--border-width) solid currentColor;
  border-right-color: transparent;
  border-radius: var(--border-radius-pill);
  animation: spin var(--spinner-speed) linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

.app-button--sm {
  padding-block: var(--space-1);
  padding-inline: var(--space-3);
  font-size: var(--font-size-xs);
}

.app-button--md {
  padding-block: var(--space-2);
  padding-inline: var(--space-4);
  font-size: var(--font-size-sm);
}

.app-button--primary {
  background-color: var(--color-primary);
  color: var(--color-white);
}

.app-button--primary:hover {
  background-color: var(--color-primary-hover);
}

.app-button--outline {
  background-color: transparent;
  color: var(--color-text-secondary);
  border-color: var(--color-border);
}

.app-button--outline:hover {
  background-color: var(--color-gray-50);
  color: var(--color-text-primary);
}

.app-button--danger {
  background-color: var(--color-danger);
  color: var(--color-white);
}

.app-button--danger:hover {
  opacity: var(--opacity-hover);
}

.app-button--ghost {
  background-color: transparent;
  color: var(--color-primary);
}

.app-button--ghost:hover {
  background-color: var(--color-primary-light);
}

.app-button--approve {
  background-color: var(--color-primary);
  color: var(--color-white);
  padding-block: var(--space-1);
  padding-inline: var(--space-3);
  font-size: var(--font-size-xs);
}

.app-button--approve:hover {
  background-color: var(--color-primary-hover);
}
</style>
