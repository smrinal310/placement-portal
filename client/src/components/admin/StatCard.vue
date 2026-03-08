<template>
  <div class="card stat-card">
    <span class="stat-card__label">{{ label }}</span>
    <div class="stat-card__main">
      <span class="stat-card__value">{{ formattedValue }}</span>
      <AppBadge v-if="trend" :status="badgeStatus">
        {{ trend }}
      </AppBadge>
    </div>
    <span v-if="subLabel" class="stat-card__sublabel">{{ subLabel }}</span>
    <span v-if="actionBadge" class="stat-card__action">{{ actionBadge }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import AppBadge from '../common/AppBadge.vue'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: Number,
    required: true
  },
  subLabel: {
    type: String,
    default: ''
  },
  trend: {
    type: String,
    default: ''
  },
  trendVariant: {
    type: String,
    default: 'success',
    validator: (val) => ['success', 'danger'].includes(val)
  },
  actionBadge: {
    type: String,
    default: ''
  }
})

const normalizedTrendVariant = computed(() => props.trendVariant)
const normalizedValue = computed(() => props.value)

const badgeStatus = computed(() => (normalizedTrendVariant.value === 'success' ? 'active' : 'rejected'))
const formattedValue = computed(() => normalizedValue.value.toLocaleString())
</script>

<style scoped>
.stat-card {
  display: flex;
  flex-direction: column;
}

.stat-card__label {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  font-weight: var(--font-weight-medium);
  margin-bottom: var(--space-2);
}

.stat-card__main {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.stat-card__value {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  line-height: var(--line-height-tight);
}

.stat-card__sublabel {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  margin-top: var(--space-1);
}

.stat-card__action {
  font-size: var(--font-size-xs);
  color: var(--color-danger);
  font-weight: var(--font-weight-medium);
  margin-top: var(--space-1);
}
</style>
