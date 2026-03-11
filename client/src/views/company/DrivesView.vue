<template>
  <div class="company-drives">

    <header class="company-drives__header">
      <div>
        <h1 class="company-drives__title">My Drives</h1>
        <p class="company-drives__subtitle">Manage all your placement drives in one place.</p>
      </div>
      <AppButton variant="primary" iconLeft="bi bi-plus-lg" @click="router.push('/company/drives/create')">
        Create New Drive
      </AppButton>
    </header>

    <AppFilterBar v-model="companyStore.drivesFilters.search" placeholder="Search by job title, type, salary...">
      <select class="filter-select" v-model="companyStore.drivesFilters.status">
        <option value="">All Statuses</option>
        <option :value="DriveStatus.APPROVED">Active</option>
        <option :value="DriveStatus.PENDING">Pending Review</option>
        <option :value="DriveStatus.CLOSED">Closed</option>
      </select>
    </AppFilterBar>

    <div class="company-drives__body">
      <AppSpinner v-if="companyStore.drivesLoading" />

      <AppEmptyState
        v-else-if="companyStore.drivesError"
        icon="bi bi-exclamation-circle"
        title="Failed to load drives"
        :subtitle="companyStore.drivesError"
        actionLabel="Retry"
        @action="companyStore.fetchDrives()"
      />

      <AppEmptyState
        v-else-if="!companyStore.drivesList.length"
        icon="bi bi-briefcase"
        title="No drives yet"
        subtitle="Create your first placement drive to start receiving applications."
        actionLabel="Create Drive"
        @action="router.push('/company/drives/create')"
      />

      <AppEmptyState
        v-else-if="!companyStore.filteredDrives.length"
        icon="bi bi-search"
        title="No drives match your filters"
        subtitle="Try adjusting your search or status filter."
      />

      <template v-else>
        <div class="company-drives__grid">
          <CompanyDriveCard
            v-for="drive in companyStore.filteredDrives"
            :key="drive.id"
            :drive="drive"
            @view="router.push('/company/drives/' + drive.id + '/applications')"
            @edit="router.push('/company/drives/' + drive.id + '/edit')"
            @delete="handleDelete(drive)"
          />
        </div>
      </template>
    </div>

  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCompanyStore } from '@/stores/company'
import { DriveStatus } from '@/utils/constants'

import AppButton from '@/components/common/AppButton.vue'
import AppFilterBar from '@/components/common/AppFilterBar.vue'
import AppSpinner from '@/components/common/AppSpinner.vue'
import AppEmptyState from '@/components/common/AppEmptyState.vue'
import CompanyDriveCard from '@/components/company/CompanyDriveCard.vue'

const router = useRouter()
const companyStore = useCompanyStore()

const handleDelete = (drive) => {
  // TODO: open confirmation modal when delete endpoint is available
  console.log('Delete drive:', drive.id)
}

onMounted(() => {
  companyStore.fetchDrives()
})
</script>

<style scoped>
.company-drives {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.company-drives__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: var(--space-4);
}

.company-drives__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-1);
}

.company-drives__subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.company-drives__body {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.company-drives__grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
}

@media (max-width: 900px) {
  .company-drives__grid {
    grid-template-columns: 1fr;
  }
}
</style>
