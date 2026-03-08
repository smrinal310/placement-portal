<template>
  <div class="app-pagination" v-if="total > 0 && totalPages > 1">
    <div class="app-pagination__info">
      Showing <span class="app-pagination__bold">{{ startRecord.toLocaleString() }}</span> to
      <span class="app-pagination__bold">{{ endRecord.toLocaleString() }}</span> of
      <span class="app-pagination__bold">{{ total.toLocaleString() }}</span> results
    </div>

    <div class="app-pagination__controls" v-if="normalizedVariant === 'text'">
      <button class="app-pagination__btn-text" :class="{ 'app-pagination__btn--disabled': currentPage === 1 }"
        @click="goToPage(currentPage - 1)">
        Previous
      </button>
      <button class="app-pagination__btn-text" :class="{ 'app-pagination__btn--disabled': currentPage === totalPages }"
        @click="goToPage(currentPage + 1)">
        Next
      </button>
    </div>

    <div class="app-pagination__controls" v-if="normalizedVariant === 'numbered'">
      <button class="app-pagination__btn-icon" :class="{ 'app-pagination__btn--disabled': currentPage === 1 }"
        @click="goToPage(currentPage - 1)">
        <i class="bi bi-chevron-left"></i>
      </button>

      <template v-for="(page, index) in visiblePages" :key="index">
        <span v-if="page === null" class="app-pagination__ellipsis">...</span>
        <button v-else class="app-pagination__btn-number"
          :class="{ 'app-pagination__btn-number--active': page === currentPage }" @click="goToPage(page)">
          {{ page }}
        </button>
      </template>

      <button class="app-pagination__btn-icon" :class="{ 'app-pagination__btn--disabled': currentPage === totalPages }"
        @click="goToPage(currentPage + 1)">
        <i class="bi bi-chevron-right"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  total: {
    type: Number,
    required: true,
  },
  perPage: {
    type: Number,
    default: 10,
  },
  currentPage: {
    type: Number,
    required: true,
  },
  variant: {
    type: String,
    default: 'text',
    validator: (value) => ['text', 'numbered'].includes(value),
  },
})

const emit = defineEmits(['page-change'])

const normalizedVariant = computed(() => props.variant)
const normalizedTotal = computed(() => props.total)
const normalizedPerPage = computed(() => props.perPage)
const normalizedCurrentPage = computed(() => props.currentPage)

const totalPages = computed(() => Math.ceil(normalizedTotal.value / normalizedPerPage.value))
const startRecord = computed(() => (normalizedCurrentPage.value - 1) * normalizedPerPage.value + 1)
const endRecord = computed(() => Math.min(normalizedCurrentPage.value * normalizedPerPage.value, normalizedTotal.value))

const visiblePages = computed(() => {
  const current = normalizedCurrentPage.value
  const total = totalPages.value

  if (total <= 5) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }

  if (current <= 3) {
    return [1, 2, 3, 4, null, total]
  }

  if (current >= total - 2) {
    return [1, null, total - 3, total - 2, total - 1, total]
  }

  return [1, null, current - 1, current, current + 1, null, total]
})

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value && page !== normalizedCurrentPage.value) {
    emit('page-change', page)
  }
}
</script>

<style scoped>
.app-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.app-pagination__info {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.app-pagination__bold {
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.app-pagination__controls {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.app-pagination__btn-text,
.app-pagination__btn-number,
.app-pagination__btn-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius-md);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
  background-color: transparent;
  outline: none;
}

.app-pagination__btn-text {
  border: var(--border-width) solid var(--color-border);
  color: var(--color-text-secondary);
  padding-block: var(--space-1);
  padding-inline: var(--space-3);
  font-size: var(--font-size-sm);
}

.app-pagination__btn-text:hover:not(.app-pagination__btn--disabled) {
  background-color: var(--color-gray-50);
  color: var(--color-text-primary);
}

.app-pagination__btn-number {
  border: var(--border-width) solid transparent;
  color: var(--color-text-secondary);
  width: var(--pagination-button-size);
  height: var(--pagination-button-size);
  font-size: var(--font-size-sm);
}

.app-pagination__btn-number:hover:not(.app-pagination__btn-number--active,
  .app-pagination__btn--disabled) {
  background-color: var(--color-gray-50);
  color: var(--color-text-primary);
}

.app-pagination__btn-number--active {
  background-color: var(--color-primary);
  color: var(--color-white);
}

.app-pagination__btn-icon {
  border: var(--border-width) solid var(--color-border);
  color: var(--color-text-secondary);
  width: var(--pagination-button-size);
  height: var(--pagination-button-size);
}

.app-pagination__btn-icon:hover:not(.app-pagination__btn--disabled) {
  background-color: var(--color-gray-50);
  color: var(--color-text-primary);
}

.app-pagination__ellipsis {
  color: var(--color-text-muted);
  user-select: none;
  font-size: var(--font-size-sm);
}

.app-pagination__btn--disabled {
  opacity: var(--opacity-disabled);
  cursor: not-allowed;
  pointer-events: none;
}
</style>
