<template>
  <span class="eligibility-tag">{{ label }}</span>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
.eligibility-tag {
  display: inline-flex;
  align-items: center;
  background-color: var(--color-gray-100);
  color: var(--color-text-secondary);
  border-radius: var(--border-radius-pill);
  padding-block: var(--space-1);
  padding-inline: var(--space-3);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  white-space: nowrap;
}
</style>
