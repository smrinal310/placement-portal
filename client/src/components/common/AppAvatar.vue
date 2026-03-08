<template>
  <div class="app-avatar" :class="[colorClass, sizeClass]">{{ initials }}</div>
</template>

<script setup>
import { computed } from 'vue'
import { getInitials } from '@/utils/formatters'

const props = defineProps({
  name: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v)
  }
})

const COLORS = ['blue', 'green', 'orange', 'red', 'teal', 'purple', 'pink', 'indigo']

const initials = computed(() => getInitials(props.name))

const colorClass = computed(() => {
  if (!props.name) return 'avatar-blue'
  let hash = 0
  for (let i = 0; i < props.name.length; i++) {
    hash = (hash * 31 + props.name.charCodeAt(i)) >>> 0
  }
  return `avatar-${COLORS[hash % COLORS.length]}`
})

const sizeClass = computed(() => `app-avatar--${props.size}`)
</script>

<style scoped>
.app-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius-pill);
  font-weight: var(--font-weight-semibold);
  flex-shrink: 0;
  line-height: 1;
  user-select: none;
}

.app-avatar--sm {
  width: var(--space-8);
  height: var(--space-8);
  font-size: var(--font-size-xs);
}

.app-avatar--md {
  width: var(--space-10);
  height: var(--space-10);
  font-size: var(--font-size-sm);
}

.app-avatar--lg {
  width: var(--space-12);
  height: var(--space-12);
  font-size: var(--font-size-base);
}
</style>

