<template>
  <div class="card quick-action-card">
    <div class="quick-action-card__header">
      <h3 class="quick-action-card__title">{{ title }}</h3>
      <span class="quick-action-card__badge">{{ pendingCount }} Pending</span>
    </div>

    <p class="quick-action-card__description">{{ description }}</p>

    <div class="quick-action-card__footer">
      <AppButton variant="primary" class="quick-action-card__button" @click="router.push(to)">
        {{ buttonLabel }}
      </AppButton>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import AppButton from '../common/AppButton.vue'

defineProps({
  title: {
    type: String,
    required: true
  },
  pendingCount: {
    type: Number,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  buttonLabel: {
    type: String,
    required: true
  },
  to: {
    type: String,
    required: true
  }
})

const router = useRouter()
</script>

<style scoped>
.quick-action-card {
  display: flex;
  flex-direction: column;
}

.quick-action-card__header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
}

.quick-action-card__title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.quick-action-card__badge {
  background-color: var(--color-warning-light);
  color: var(--color-warning);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  border-radius: var(--border-radius-pill);
  padding-block: var(--space-1);
  padding-inline: var(--space-2);
  white-space: nowrap;
}

.quick-action-card__description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-base);
  flex-grow: 1;
  margin: 0;
  margin-bottom: var(--space-4);
}

.quick-action-card__footer {
  width: 100%;
}

.quick-action-card__button {
  width: 100%;
}
</style>
