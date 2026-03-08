<template>
  <div class="app-toggle" :class="{
    'app-toggle--on': modelValue,
    'app-toggle--disabled': disabled,
  }" @click="toggle">
    <span v-if="label" class="app-toggle__label">{{ label }}</span>
    <div class="app-toggle__track">
      <div class="app-toggle__thumb"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  label: {
    type: String,
    default: null,
  },
})

const emit = defineEmits(['update:modelValue'])

const normalizedModelValue = computed(() => props.modelValue)
const normalizedDisabled = computed(() => props.disabled)

const toggle = () => {
  if (!normalizedDisabled.value) {
    emit('update:modelValue', !normalizedModelValue.value)
  }
}
</script>

<style scoped>
.app-toggle {
  display: inline-flex;
  align-items: center;
  gap: var(--space-3);
  cursor: pointer;
  user-select: none;
}

.app-toggle--disabled {
  opacity: var(--opacity-disabled);
  cursor: not-allowed;
  pointer-events: none;
}

.app-toggle__label {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.app-toggle__track {
  position: relative;
  width: var(--toggle-width);
  height: var(--toggle-height);
  border-radius: var(--border-radius-pill);
  background-color: var(--color-gray-300);
  transition:
    background-color var(--transition-base),
    filter var(--transition-fast);
  flex-shrink: 0;
}

.app-toggle:not(.app-toggle--disabled):hover .app-toggle__track {
  filter: brightness(0.95);
}

.app-toggle--on .app-toggle__track {
  background-color: var(--color-primary);
}

.app-toggle__thumb {
  position: absolute;
  top: var(--toggle-gap);
  left: var(--toggle-gap);
  width: var(--toggle-thumb-size);
  height: var(--toggle-thumb-size);
  border-radius: var(--border-radius-pill);
  background-color: var(--color-white);
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-base);
}

.app-toggle--on .app-toggle__thumb {
  transform: translateX(calc(var(--toggle-width) - var(--toggle-thumb-size) - (var(--toggle-gap) * 2)));
}
</style>
