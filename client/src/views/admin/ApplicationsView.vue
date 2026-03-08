<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { ApplicationStatus } from '@/utils/constants'
import { formatDate } from '@/utils/formatters'
import AppAvatar from '@/components/common/AppAvatar.vue'
import AppBadge from '@/components/common/AppBadge.vue'
import AppButton from '@/components/common/AppButton.vue'
import AppSpinner from '@/components/common/AppSpinner.vue'
import AppEmptyState from '@/components/common/AppEmptyState.vue'
import AppPagination from '@/components/common/AppPagination.vue'

const router = useRouter()
const adminStore = useAdminStore()

const selectedDriveId = ref('')
const selectedCompanyId = ref('')
const selectedStatus = ref('')
const exportLoading = ref(false)
const feedbackMessage = ref('')
const feedbackType = ref('success')

function applyFilters() {
  adminStore.fetchApplications({
    driveId: selectedDriveId.value,
    companyId: selectedCompanyId.value,
    status: selectedStatus.value,
    page: 1
  })
}

function clearFilters() {
  selectedDriveId.value = ''
  selectedCompanyId.value = ''
  selectedStatus.value = ''
  adminStore.fetchApplications({ driveId: '', companyId: '', status: '', page: 1 })
}

watch([selectedDriveId, selectedCompanyId, selectedStatus], applyFilters)

function handleViewStudent(app) {
  if (app.student_id) {
    router.push('/admin/students/' + app.student_id)
  } else {
    console.log('TODO: student_id not returned by backend for application', app.id)
  }
}

function handleExport() {
  exportLoading.value = true
  console.log('TODO: implement export once /api/admin/applications/export endpoint exists')
  setTimeout(() => {
    exportLoading.value = false
    showFeedback('Export started. Check your downloads.', 'success')
  }, 1000)
}

function showFeedback(message, type = 'success') {
  feedbackMessage.value = message
  feedbackType.value = type
  setTimeout(() => { feedbackMessage.value = '' }, 3000)
}

onMounted(() => {
  adminStore.fetchApplications()
  adminStore.fetchDriveOptions()
  adminStore.fetchCompanyOptions()
})
</script>

<template>
  <div class="applications">
    <Transition name="toast">
      <div v-if="feedbackMessage" :class="['applications__toast', `applications__toast--${feedbackType}`]">
        {{ feedbackMessage }}
      </div>
    </Transition>

    <div class="applications__header">
      <div class="applications__header-text">
        <h1 class="applications__title">All Applications</h1>
        <p class="applications__subtitle">Read-only view of all student applications across placement drives.</p>
      </div>
      <AppButton variant="outline" :loading="exportLoading" @click="handleExport">
        <i class="bi bi-download"></i> Export to CSV
      </AppButton>
    </div>

    <div class="applications__filters card">
      <div class="applications__filter-group">
        <label class="applications__filter-label">Drive Name</label>
        <select v-model="selectedDriveId" class="applications__select">
          <option value="">All Drives</option>
          <option v-for="opt in adminStore.driveOptions" :key="opt.id" :value="opt.id">
            {{ opt.label }}
          </option>
        </select>
      </div>

      <div class="applications__filter-group">
        <label class="applications__filter-label">Company</label>
        <select v-model="selectedCompanyId" class="applications__select">
          <option value="">All Companies</option>
          <option v-for="opt in adminStore.companyOptions" :key="opt.id" :value="opt.id">
            {{ opt.label }}
          </option>
        </select>
      </div>

      <div class="applications__filter-group">
        <label class="applications__filter-label">Status</label>
        <select v-model="selectedStatus" class="applications__select">
          <option value="">All Statuses</option>
          <option :value="ApplicationStatus.APPLIED">Applied</option>
          <option :value="ApplicationStatus.SHORTLISTED">Shortlisted</option>
          <option :value="ApplicationStatus.SELECTED">Selected</option>
          <option :value="ApplicationStatus.REJECTED">Rejected</option>
        </select>
      </div>

      <AppButton variant="outline" class="applications__clear-btn" @click="clearFilters">
        Clear Filters
      </AppButton>
    </div>

    <div class="applications__body card">
      <div v-if="adminStore.loading" class="applications__spinner-wrap">
        <AppSpinner />
      </div>

      <template v-else-if="adminStore.applications.length === 0">
        <AppEmptyState
          icon="bi bi-file-text"
          title="No applications found"
          subtitle="Try adjusting your filters"
        />
      </template>

      <template v-else>
        <div class="applications__table-wrap">
          <table class="applications__table">
            <thead>
              <tr>
                <th class="applications__th">Student</th>
                <th class="applications__th">Company</th>
                <th class="applications__th">Drive</th>
                <th class="applications__th">Applied On</th>
                <th class="applications__th">Status</th>
                <th class="applications__th">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in adminStore.applications" :key="app.id" class="applications__row">
                <td class="applications__td">
                  <div class="applications__student-cell">
                    <AppAvatar :name="app.student_name" size="sm" />
                    <div class="applications__student-info">
                      <span class="applications__student-name">{{ app.student_name }}</span>
                      <span class="applications__student-meta">
                        {{ app.student_branch }} &bull; {{ app.student_year }} Batch
                      </span>
                    </div>
                  </div>
                </td>
                <td class="applications__td">
                  <div class="applications__company-cell">
                    <i class="bi bi-buildings applications__company-icon"></i>
                    <span>{{ app.company_name }}</span>
                  </div>
                </td>
                <td class="applications__td">{{ app.drive_title }}</td>
                <td class="applications__td">{{ formatDate(app.applied_at, { style: 'short' }) }}</td>
                <td class="applications__td">
                  <AppBadge :status="app.status" />
                </td>
                <td class="applications__td">
                  <button class="applications__action-btn" @click="handleViewStudent(app)" title="View student">
                    <i class="bi bi-eye"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="applications__pagination">
          <AppPagination
            variant="text"
            :total="adminStore.applicationsTotal"
            :perPage="10"
            :currentPage="adminStore.applicationFilters.page"
            @page-change="(page) => adminStore.fetchApplications({ page })"
          />
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.applications {
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
  position: relative;
}

.applications__toast {
  position: fixed;
  top: var(--space-5);
  right: var(--space-5);
  z-index: 1000;
  padding: var(--space-3) var(--space-5);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  box-shadow: var(--shadow-md);
}

.applications__toast--success {
  background-color: var(--color-success-light);
  color: var(--color-success-dark);
  border: var(--border-width) solid var(--color-success);
}

.applications__toast--error {
  background-color: var(--color-danger-light);
  color: var(--color-danger-dark);
  border: var(--border-width) solid var(--color-danger);
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity var(--transition-normal), transform var(--transition-normal);
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(calc(-1 * var(--space-2)));
}

.applications__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
}

.applications__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-1) 0;
}

.applications__subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin: 0;
}

.applications__filters {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.applications__filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.applications__filter-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.applications__select {
  min-width: 180px;
  padding: var(--space-2) var(--space-3);
  border: var(--border-width) solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-family: var(--font-family-base);
  color: var(--color-text-primary);
  background-color: var(--color-surface);
  cursor: pointer;
  outline: none;
}

.applications__select:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.applications__clear-btn {
  align-self: flex-end;
}

.applications__body {
  min-height: 200px;
}

.applications__spinner-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: var(--space-10);
}

.applications__table-wrap {
  overflow-x: auto;
}

.applications__table {
  width: 100%;
  border-collapse: collapse;
}

.applications__th {
  padding: var(--space-3) var(--space-4);
  text-align: left;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: var(--border-width) solid var(--border-color);
  white-space: nowrap;
}

.applications__row {
  border-bottom: var(--border-width) solid var(--border-color);
  transition: background-color var(--transition-fast);
}

.applications__row:last-child {
  border-bottom: none;
}

.applications__row:hover {
  background-color: var(--color-surface-hover);
}

.applications__td {
  padding: var(--space-3) var(--space-4);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  vertical-align: middle;
}

.applications__student-cell {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.applications__student-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.applications__student-name {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.applications__student-meta {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.applications__company-cell {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.applications__company-icon {
  color: var(--color-text-muted);
  font-size: var(--font-size-base);
}

.applications__action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
  font-size: var(--font-size-base);
  transition: color var(--transition-fast), background-color var(--transition-fast);
  line-height: 1;
}

.applications__action-btn:hover {
  color: var(--color-text-primary);
  background-color: var(--color-surface-hover);
}

.applications__pagination {
  padding: var(--space-4) var(--space-4) var(--space-2);
  border-top: var(--border-width) solid var(--border-color);
}
</style>
