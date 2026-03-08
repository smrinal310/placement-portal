<script setup>
import { ref } from 'vue'

defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: 'Search...' },
  showSearch: { type: Boolean, default: true }
})

const emit = defineEmits(['update:modelValue'])
const slotRef = ref(null)

function handleClear() {
  emit('update:modelValue', '')
  slotRef.value?.querySelectorAll('select').forEach(sel => {
    sel.value = sel.options[0]?.value ?? ''
    sel.dispatchEvent(new Event('change'))
  })
}
</script>

<template>
  <div class="filter-bar card">
    <div v-if="showSearch" class="filter-bar__search-wrap">
      <i class="bi bi-search filter-bar__search-icon"></i>
      <input
        type="text"
        class="filter-bar__search-input"
        :placeholder="placeholder"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
      />
    </div>
    <div ref="slotRef" style="display: contents">
      <slot />
    </div>
    <button class="filter-bar__clear-btn" type="button" @click="handleClear">
      Clear
    </button>
  </div>
</template>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
}

.filter-bar__search-wrap {
  position: relative;
  flex: 1 1 0;
  min-width: 0;
}

.filter-bar__search-icon {
  position: absolute;
  left: var(--space-3);
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-muted);
  pointer-events: none;
}

.filter-bar__search-input {
  width: 100%;
  padding-top: var(--space-2);
  padding-bottom: var(--space-2);
  padding-left: var(--space-8);
  padding-right: var(--space-3);
  border: var(--border-width) solid var(--border-color);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-base);
  font-family: var(--font-family-base);
  color: var(--color-text-primary);
  background: var(--color-white);
  transition: border-color var(--transition-fast);
  outline: none;
  box-sizing: border-box;
}

.filter-bar__search-input:focus {
  border-color: var(--color-primary);
}

.filter-bar__search-input::placeholder {
  color: var(--color-text-placeholder);
}

.filter-bar__clear-btn {
  flex-shrink: 0;
  padding: var(--space-2) var(--space-3);
  border: var(--border-width) solid var(--color-border);
  border-radius: var(--border-radius-md);
  background: transparent;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-family: var(--font-family-base);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.filter-bar__clear-btn:hover {
  border-color: var(--color-text-secondary);
  color: var(--color-text-primary);
  background: var(--color-gray-100);
}
</style>
