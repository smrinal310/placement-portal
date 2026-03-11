<template>
  <span class="app-badge" :class="[badgeClass, { 'app-badge--action-needed': isActionNeeded }]">
    <slot>{{ formattedStatus }}</slot>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true,
    validator: (value) =>
      [
        'approved',
        'pending',
        'rejected',
        'active',
        'blacklisted',
        'selected',
        'shortlisted',
        'applied',
        'closed',
        'placed',
        'action-needed',
      ].includes(value.toLowerCase()),
  },
})

const normalizedStatus = computed(() => props.status.toLowerCase())

const badgeClass = computed(() =>
  normalizedStatus.value === 'action-needed' ? null : `badge-${normalizedStatus.value}`,
)

const isActionNeeded = computed(() => normalizedStatus.value === 'action-needed')

const formattedStatus = computed(() =>
  normalizedStatus.value
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' '),
)
</script>

<style scoped>
.app-badge {
  display: inline-flex;
  align-items: center;
  padding-block: var(--space-1);
  padding-inline: var(--space-3);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  border-radius: var(--border-radius-pill);
  white-space: nowrap;
}

.app-badge--action-needed {
  color: var(--color-danger);
  padding-inline: 0;
}
</style>
