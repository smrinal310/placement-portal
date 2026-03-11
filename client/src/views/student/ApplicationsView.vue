<template>
  <div class="applications">

    <!-- ── Header ── -->
    <header class="applications__header">
      <div>
        <h1 class="applications__title">My Applications</h1>
        <p class="applications__subtitle">Track all your placement drive applications in one place.</p>
      </div>
      <button
        class="applications__export-btn"
        :disabled="exportLoading"
        @click="triggerExport"
      >
        <i v-if="exportLoading" class="bi bi-hourglass-split applications__export-spin"></i>
        <i v-else class="bi bi-download"></i>
        {{ exportLoading ? 'Preparing…' : 'Export CSV' }}
      </button>
    </header>

    <!-- ── Status filter tabs ── -->
    <div class="applications__tabs">
      <button
        v-for="tab in TABS"
        :key="tab.value"
        class="applications__tab"
        :class="{ 'applications__tab--active': activeStatus === tab.value }"
        @click="setStatus(tab.value)"
      >
        {{ tab.label }}
        <span v-if="tab.count !== null" class="applications__tab-count">{{ tab.count }}</span>
      </button>
    </div>

    <!-- ── Content ── -->
    <div class="card applications__card">

      <AppSpinner v-if="loading" />

      <AppEmptyState
        v-else-if="error"
        icon="bi bi-exclamation-circle"
        title="Failed to load applications"
        :subtitle="error"
        actionLabel="Retry"
        @action="loadApplications"
      />

      <AppEmptyState
        v-else-if="!allApplications.length"
        icon="bi bi-file-earmark-text"
        title="No applications yet"
        subtitle="You haven't applied to any placement drives. Browse drives to get started!"
      />

      <template v-else>
        <div class="applications__table-wrap">
          <table class="applications__table">
            <thead>
              <tr>
                <th>Company</th>
                <th>Job Title</th>
                <th>Applied On</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in filteredApplications" :key="app.application_id">
                <td>
                  <div class="applications__company-cell">
                    <div class="applications__logo-wrap">
                      <img
                        v-if="app.company_logo"
                        :src="`${apiBase}/static/uploads/logos/${app.company_logo}`"
                        :alt="app.company_name"
                        class="applications__logo"
                      />
                      <AppAvatar v-else :name="app.company_name" size="sm" />
                    </div>
                    <span class="applications__company-name table-link" @click="router.push('/student/companies/' + app.company_id)">{{ app.company_name }}</span>
                  </div>
                </td>
                <td class="applications__job-title table-link" @click="router.push('/student/drives/' + app.drive_id)">{{ app.job_title }}</td>
                <td class="applications__date">{{ formatDate(app.applied_at) }}</td>
                <td><AppBadge :status="app.status" /></td>
                <td>
                  <div class="applications__actions">
                    <a
                      v-if="app.interview_link && app.interview_date"
                      :href="app.interview_link"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="applications__action-btn applications__action-btn--primary"
                    >
                      Join Interview
                    </a>
                    <span v-else class="applications__no-actions">No actions available</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import * as studentApi from '@/api/student'
import { formatDate } from '@/utils/formatters'
import AppAvatar from '@/components/common/AppAvatar.vue'
import AppBadge from '@/components/common/AppBadge.vue'
import AppSpinner from '@/components/common/AppSpinner.vue'
import AppEmptyState from '@/components/common/AppEmptyState.vue'

const router = useRouter()
const apiBase = import.meta.env.VITE_API_BASE_URL || ''

const loading = ref(false)
const error = ref('')
const allApplications = ref([])
const activeStatus = ref('')

const TABS = computed(() => {
  const counts = { applied: 0, shortlisted: 0, selected: 0, rejected: 0 }
  allApplications.value.forEach((a) => {
    if (a.status in counts) counts[a.status]++
  })
  return [
    { label: 'All',         value: '',            count: allApplications.value.length || null },
    { label: 'Applied',     value: 'applied',     count: counts.applied || null },
    { label: 'Shortlisted', value: 'shortlisted', count: counts.shortlisted || null },
    { label: 'Selected',    value: 'selected',    count: counts.selected || null },
    { label: 'Rejected',    value: 'rejected',    count: counts.rejected || null },
  ]
})

const filteredApplications = computed(() =>
  activeStatus.value
    ? allApplications.value.filter((a) => a.status === activeStatus.value)
    : allApplications.value
)

function setStatus(status) {
  activeStatus.value = status
}

async function loadApplications() {
  loading.value = true
  error.value = ''
  try {
    const res = await studentApi.getApplications()
    allApplications.value = res.data || []
  } catch (e) {
    error.value = e.message || 'Failed to load applications.'
  } finally {
    loading.value = false
  }
}

loadApplications()

// ── Export CSV ──
const exportLoading = ref(false)
const exportJobId = ref(null)
let exportPollTimer = null

async function triggerExport() {
  if (exportLoading.value) return
  exportLoading.value = true
  try {
    const res = await studentApi.triggerExport()
    exportJobId.value = res.data?.export_job_id
    exportPollTimer = setInterval(pollExport, 2500)
  } catch {
    exportLoading.value = false
  }
}

async function pollExport() {
  if (!exportJobId.value) return
  try {
    const res = await studentApi.getExportStatus(exportJobId.value)
    const status = res.data?.status
    if (status === 'done') {
      clearInterval(exportPollTimer)
      await studentApi.downloadExport(exportJobId.value, 'my-applications.csv')
      exportLoading.value = false
      exportJobId.value = null
    } else if (status === 'failed') {
      clearInterval(exportPollTimer)
      exportLoading.value = false
      exportJobId.value = null
    }
  } catch {
    clearInterval(exportPollTimer)
    exportLoading.value = false
  }
}

onUnmounted(() => {
  if (exportPollTimer) clearInterval(exportPollTimer)
})
</script>

<style scoped>
.applications {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

/* Header */
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
  margin: 0 0 var(--space-1);
}

.applications__subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

/* Tabs */
.applications__tabs {
  display: flex;
  gap: var(--space-1);
  flex-wrap: wrap;
}

.applications__tab {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-pill);
  background: var(--color-content-bg);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.applications__tab:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.applications__tab--active {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
  color: var(--color-white);
}

.applications__tab-count {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  background: rgba(0, 0, 0, 0.1);
  border-radius: var(--border-radius-pill);
  padding: 1px 6px;
  line-height: 1.4;
}

.applications__tab--active .applications__tab-count {
  background: rgba(255, 255, 255, 0.25);
}

/* Card */
.applications__card {
  padding: 0;
  overflow: hidden;
}

/* Table */
.applications__table-wrap {
  overflow-x: auto;
}

.applications__table {
  width: 100%;
  border-collapse: collapse;
}

.applications__table thead tr {
  border-bottom: 1px solid var(--color-border);
}

.applications__table th {
  padding: var(--space-3) var(--space-5);
  text-align: left;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
  background-color: var(--color-gray-50);
}

.applications__table tbody tr {
  border-bottom: 1px solid var(--color-border);
  transition: background-color var(--transition-fast);
}

.applications__table tbody tr:last-child {
  border-bottom: none;
}

.applications__table tbody tr:hover {
  background-color: var(--color-gray-50);
}

.applications__table td {
  padding: var(--space-4) var(--space-5);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  vertical-align: middle;
}

/* Company cell */
.applications__company-cell {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.applications__logo-wrap {
  flex-shrink: 0;
}

.applications__logo {
  width: 32px;
  height: 32px;
  border-radius: var(--border-radius-sm);
  object-fit: contain;
  border: 1px solid var(--color-border);
  background-color: var(--color-white);
  padding: 2px;
}

.applications__company-name {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  white-space: nowrap;
}

.applications__job-title {
  color: var(--color-text-secondary);
  max-width: 220px;
}

.applications__date {
  white-space: nowrap;
  color: var(--color-text-muted);
}

.applications__no-actions {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  white-space: nowrap;
}

/* Actions */
.applications__actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.applications__action-btn {
  padding: var(--space-1) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  background: var(--color-content-bg);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.applications__action-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.applications__action-btn--primary {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
  color: var(--color-white);
}

.applications__action-btn--primary:hover {
  background-color: var(--color-primary-dark, #1d4ed8);
  color: var(--color-white);
}

/* Export button */
.applications__export-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background-color: var(--color-primary);
  color: var(--color-white);
  border: none;
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: opacity var(--transition-fast);
  white-space: nowrap;
  flex-shrink: 0;
  align-self: center;
}

.applications__export-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.applications__export-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.applications__export-spin {
  animation: spin 1s linear infinite;
}

/* Pagination sits inside the card */
:deep(.app-pagination) {
  padding: var(--space-4) var(--space-5);
  border-top: 1px solid var(--color-border);
}
</style>
