<template>
  <div class="drive-card card" :class="{ 'drive-card--applied': drive.has_applied }">

    <!-- Top row: company + deadline -->
    <div class="drive-card__top">
      <div class="drive-card__company">
        <AppAvatar size="sm" :name="drive.company_name" />
        <div class="drive-card__company-info">
          <span class="drive-card__company-name">{{ drive.company_name }}</span>
          <span v-if="drive.job_location" class="drive-card__location">
            <i class="bi bi-geo-alt"></i> {{ drive.job_location }}
          </span>
        </div>
      </div>

      <div class="drive-card__deadline" :class="deadlineClass">
        <i class="bi bi-clock"></i>
        {{ deadlineLabel }}
      </div>
    </div>

    <!-- Job title -->
    <h3 class="drive-card__title">{{ drive.job_title }}</h3>

    <!-- Tags row -->
    <div class="drive-card__tags">
      <span v-if="drive.job_type" class="drive-card__tag drive-card__tag--type">
        {{ drive.job_type }}
      </span>
      <span v-if="drive.salary_package" class="drive-card__tag drive-card__tag--salary">
        <i class="bi bi-currency-rupee"></i>{{ drive.salary_package }}
      </span>
      <span
        class="drive-card__tag"
        :class="drive.is_eligible ? 'drive-card__tag--eligible' : 'drive-card__tag--ineligible'"
      >
        <i :class="drive.is_eligible ? 'bi bi-check-circle-fill' : 'bi bi-x-circle-fill'"></i>
        {{ drive.is_eligible ? 'Eligible' : 'Not Eligible' }}
      </span>
    </div>

    <!-- Footer: actions -->
    <div class="drive-card__footer">
      <button
        class="drive-card__apply-btn"
        :class="{
          'drive-card__apply-btn--applied': drive.has_applied,
          'drive-card__apply-btn--ineligible': !drive.is_eligible && !drive.has_applied,
        }"
        :disabled="drive.has_applied || !drive.is_eligible || applying"
        @click.stop="$emit('apply', drive.drive_id)"
      >
        <i v-if="applying" class="bi bi-arrow-repeat drive-card__apply-spin"></i>
        <i v-else-if="drive.has_applied" class="bi bi-check-lg"></i>
        <i v-else class="bi bi-send"></i>
        {{ applying ? 'Applying…' : drive.has_applied ? 'Applied' : 'Apply Now' }}
      </button>

      <button class="drive-card__view-btn" title="View details" @click.stop="$emit('view', drive.drive_id)">
        <i class="bi bi-arrow-right"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import AppAvatar from '@/components/common/AppAvatar.vue'

const props = defineProps({
  drive: {
    type: Object,
    required: true,
  },
  applying: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['apply', 'view'])

const daysLeft = computed(() => {
  if (!props.drive.application_deadline) return null
  const diff = new Date(props.drive.application_deadline).getTime() - Date.now()
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
})

const deadlineLabel = computed(() => {
  const d = daysLeft.value
  if (d === null) return 'No deadline'
  if (d <= 0) return 'Deadline passed'
  if (d === 1) return 'Deadline: Tomorrow'
  return `Deadline: ${d} Days`
})

const deadlineClass = computed(() => {
  const d = daysLeft.value
  if (d === null || d > 7) return 'drive-card__deadline--normal'
  if (d <= 2) return 'drive-card__deadline--urgent'
  return 'drive-card__deadline--soon'
})
</script>

<style scoped>
.drive-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  transition: box-shadow var(--transition-fast), transform var(--transition-fast);
}

.drive-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.drive-card--applied {
  opacity: 0.85;
}

/* Top row */
.drive-card__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-3);
}

.drive-card__company {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-width: 0;
}

.drive-card__company-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.drive-card__company-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.drive-card__location {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.drive-card__location i {
  font-size: 10px;
}

/* Deadline chip */
.drive-card__deadline {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  white-space: nowrap;
  flex-shrink: 0;
  padding: 3px var(--space-2);
  border-radius: var(--border-radius-pill);
}

.drive-card__deadline--normal {
  background-color: var(--color-gray-100);
  color: var(--color-text-secondary);
}

.drive-card__deadline--soon {
  background-color: var(--color-warning-light);
  color: var(--color-warning);
}

.drive-card__deadline--urgent {
  background-color: var(--color-danger-light);
  color: var(--color-danger);
}

/* Title */
.drive-card__title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
  line-height: var(--line-height-tight);
}

/* Tags */
.drive-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.drive-card__tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  padding: 3px var(--space-2);
  border-radius: var(--border-radius-pill);
}

.drive-card__tag--type {
  background-color: var(--color-info-light);
  color: var(--color-info, #1d4ed8);
}

.drive-card__tag--salary {
  background-color: var(--color-success-light);
  color: var(--color-success);
}

.drive-card__tag--eligible {
  background-color: var(--color-success-light);
  color: var(--color-success);
}

.drive-card__tag--ineligible {
  background-color: var(--color-gray-100);
  color: var(--color-text-muted);
}

/* Footer */
.drive-card__footer {
  display: flex;
  gap: var(--space-2);
  margin-top: auto;
  padding-top: var(--space-2);
  border-top: var(--border-width) solid var(--color-border);
}

.drive-card__apply-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  border: none;
  transition: background-color var(--transition-fast), opacity var(--transition-fast);
  background-color: var(--color-primary);
  color: var(--color-white);
}

.drive-card__apply-btn:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
}

.drive-card__apply-btn--applied {
  background-color: var(--color-success-light);
  color: var(--color-success);
}

.drive-card__apply-btn--ineligible {
  background-color: var(--color-gray-100);
  color: var(--color-text-muted);
  cursor: not-allowed;
}

.drive-card__apply-btn:disabled {
  cursor: not-allowed;
  opacity: 0.8;
}

.drive-card__apply-spin {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.drive-card__view-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--border-radius-md);
  background: none;
  border: var(--border-width) solid var(--color-border);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.drive-card__view-btn:hover {
  background-color: var(--color-primary-light);
  border-color: var(--color-primary);
  color: var(--color-primary);
}
</style>
