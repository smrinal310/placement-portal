<template>
  <div class="card company-drive-card" :class="{ 'company-drive-card--closed': isClosed }">
    <div class="company-drive-card__top">
      <AppBadge :status="badgeStatus">{{ badgeLabel }}</AppBadge>
      <div class="company-drive-card__actions">
        <button
          v-if="!isClosed"
          class="company-drive-card__action-btn"
          title="Edit drive"
          @click="$emit('edit', drive)"
        >
          <i class="bi bi-pencil"></i>
        </button>
        <button
          v-else
          class="company-drive-card__action-btn company-drive-card__action-btn--danger"
          title="Delete drive"
          @click="$emit('delete', drive)"
        >
          <i class="bi bi-trash"></i>
        </button>
      </div>
    </div>

    <h3 class="company-drive-card__title">{{ drive.job_title }}</h3>
    <p v-if="metaText" class="company-drive-card__meta">{{ metaText }}</p>

    <div class="company-drive-card__stats">
      <div class="company-drive-card__stat">
        <span class="company-drive-card__stat-label">DEADLINE</span>
        <span
          class="company-drive-card__stat-value"
          :class="{ 'company-drive-card__stat-value--danger': isExpired, 'company-drive-card__stat-value--warning': isClosingSoon && !isExpired }"
        >
          {{ deadlineDisplay }}
        </span>
      </div>
      <div class="company-drive-card__stat">
        <span class="company-drive-card__stat-label">APPLICANTS</span>
        <span class="company-drive-card__stat-value">{{ drive.applicant_count ?? 0 }}</span>
      </div>
      <div v-if="drive.shortlisted_count > 0" class="company-drive-card__stat">
        <span class="company-drive-card__stat-label">SHORTLISTED</span>
        <span class="company-drive-card__stat-value company-drive-card__stat-value--success">
          {{ drive.shortlisted_count }}
        </span>
      </div>
    </div>

    <div class="company-drive-card__footer">
      <AppButton
        :variant="isClosed ? 'ghost' : 'outline'"
        :iconLeft="isClosed ? 'bi bi-clock-history' : 'bi bi-eye'"
        @click="$emit('view', drive)"
      >
        {{ isClosed ? 'View History' : 'View Applications' }}
      </AppButton>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatDate } from '@/utils/formatters'
import { DriveStatus } from '@/utils/constants'
import AppBadge from '@/components/common/AppBadge.vue'
import AppButton from '@/components/common/AppButton.vue'

const props = defineProps({
  drive: {
    type: Object,
    required: true
  }
})

defineEmits(['view', 'edit', 'delete'])

const isClosed = computed(() => props.drive.status === DriveStatus.CLOSED)
const isPending = computed(() => props.drive.status === DriveStatus.PENDING)

const deadlineRaw = computed(() => props.drive.application_deadline ?? props.drive.deadline ?? null)

const daysUntilDeadline = computed(() => {
  if (!deadlineRaw.value) return null
  const diff = new Date(deadlineRaw.value).getTime() - Date.now()
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
})

const isExpired = computed(() => daysUntilDeadline.value !== null && daysUntilDeadline.value < 0)
const isClosingSoon = computed(
  () => daysUntilDeadline.value !== null && daysUntilDeadline.value >= 0 && daysUntilDeadline.value <= 3
)

const badgeStatus = computed(() => {
  if (isClosed.value) return 'closed'
  if (isPending.value) return 'pending'
  if (isClosingSoon.value) return 'pending'
  return 'active'
})

const badgeLabel = computed(() => {
  if (isClosed.value) return 'Closed'
  if (isPending.value) return 'Pending Review'
  if (isClosingSoon.value) return 'Closing Soon'
  return 'Active'
})

const deadlineDisplay = computed(() => {
  if (!deadlineRaw.value) return '—'
  if (isExpired.value) return 'Ended ' + formatDate(deadlineRaw.value, { style: 'short' })
  if (daysUntilDeadline.value === 0) return 'Today'
  if (daysUntilDeadline.value === 1) return 'Tomorrow'
  return formatDate(deadlineRaw.value, { style: 'short' })
})

const metaText = computed(() => {
  const parts = [props.drive.job_type, props.drive.salary_package].filter(Boolean)
  return parts.join(' • ')
})
</script>

<style scoped>
.company-drive-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  transition: box-shadow var(--transition-fast);
}

.company-drive-card:hover {
  box-shadow: var(--shadow-md);
}

.company-drive-card--closed {
  opacity: 0.8;
}

.company-drive-card__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.company-drive-card__actions {
  display: flex;
  gap: var(--space-1);
}

.company-drive-card__action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-1);
  border-radius: var(--border-radius-sm);
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background-color var(--transition-fast), color var(--transition-fast);
  outline: none;
}

.company-drive-card__action-btn:hover {
  background-color: var(--color-gray-100);
  color: var(--color-text-primary);
}

.company-drive-card__action-btn--danger:hover {
  background-color: var(--color-danger-light);
  color: var(--color-danger);
}

.company-drive-card__title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
  line-height: var(--line-height-tight);
}

.company-drive-card__meta {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  margin: 0;
}

.company-drive-card__stats {
  display: flex;
  gap: var(--space-4);
  flex-wrap: wrap;
}

.company-drive-card__stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.company-drive-card__stat-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-muted);
  letter-spacing: 0.04em;
}

.company-drive-card__stat-value {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.company-drive-card__stat-value--danger {
  color: var(--color-danger);
}

.company-drive-card__stat-value--warning {
  color: var(--color-warning);
}

.company-drive-card__stat-value--success {
  color: var(--color-success);
}

.company-drive-card__footer {
  margin-top: auto;
  padding-top: var(--space-2);
  border-top: var(--border-width) solid var(--color-border);
}
</style>
