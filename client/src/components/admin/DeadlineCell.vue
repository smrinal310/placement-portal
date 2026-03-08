<template>
  <div class="deadline-cell">
    <span class="deadline-cell__date" :class="{ 'deadline-cell__date--expired': isExpired }">
      {{ formattedDate }}
    </span>
    <span class="deadline-cell__countdown" :class="countdownColorClass">
      {{ countdownLabel }}
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  deadline: {
    type: String,
    required: true
  }
})

const normalizedDeadline = computed(() => props.deadline)
const deadlineDate = computed(() => new Date(normalizedDeadline.value))

const formattedDate = computed(() => {
  return deadlineDate.value.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
})

const daysRemaining = computed(() => {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const target = new Date(deadlineDate.value.getFullYear(), deadlineDate.value.getMonth(), deadlineDate.value.getDate())
  return Math.ceil((target - today) / (1000 * 60 * 60 * 24))
})

const isExpired = computed(() => daysRemaining.value < 0)

const countdownLabel = computed(() => {
  const days = daysRemaining.value
  if (days < 0) return 'Expired'
  if (days === 0) return 'Today'
  return `${days} days left`
})

const countdownColorClass = computed(() => {
  const days = daysRemaining.value
  if (days < 0) return 'deadline-cell__countdown--danger'
  if (days <= 7) return 'deadline-cell__countdown--warning'
  return 'deadline-cell__countdown--muted'
})
</script>

<style scoped>
.deadline-cell {
  display: flex;
  flex-direction: column;
}

.deadline-cell__date {
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  line-height: var(--line-height-tight);
}

.deadline-cell__date--expired {
  text-decoration: line-through;
}

.deadline-cell__countdown {
  font-size: var(--font-size-xs);
  margin-top: calc(var(--space-1) / 2);
}

.deadline-cell__countdown--danger {
  color: var(--color-danger);
}

.deadline-cell__countdown--warning {
  color: var(--color-warning);
}

.deadline-cell__countdown--muted {
  color: var(--color-text-muted);
}
</style>
