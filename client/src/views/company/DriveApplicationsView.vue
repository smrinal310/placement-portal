<template>
  <div class="drive-applications">

    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toast.message" :class="['drive-applications__toast', `drive-applications__toast--${toast.type}`]">
        {{ toast.message }}
      </div>
    </Transition>

    <!-- Back link -->
    <router-link to="/company/drives" class="drive-applications__back">
      <i class="bi bi-arrow-left"></i> Back to My Drives
    </router-link>

    <!-- Header -->
    <div class="drive-applications__header">
      <div class="drive-applications__header-left">
        <template v-if="driveLoading">
          <div class="drive-applications__title-skeleton"></div>
        </template>
        <template v-else-if="drive">
          <h1 class="drive-applications__title">{{ drive.job_title }}</h1>
          <AppBadge :status="driveBadgeStatus" />
        </template>
      </div>
      <div class="drive-applications__header-actions">
        <AppButton
          variant="outline"
          iconLeft="bi bi-x-circle"
          :disabled="selectedIdsArray.length === 0"
          @click="bulkRejectModalOpen = true"
        >
          Reject Selected
        </AppButton>
        <AppButton
          variant="primary"
          iconLeft="bi bi-check2-all"
          :disabled="selectedIdsArray.length === 0"
          :loading="bulkLoading"
          @click="handleShortlistSelected"
        >
          Shortlist Selected
        </AppButton>
      </div>
    </div>

    <!-- Stat Cards -->
    <div class="drive-applications__stats" v-if="drive && !driveLoading">
      <StatCard label="Total Applied" :value="drive.applicant_count ?? 0" />
      <StatCard label="Shortlisted" :value="drive.shortlisted_count ?? 0" />
      <StatCard label="Selected" :value="drive.selected_count ?? 0" />
    </div>
    <div class="drive-applications__stats" v-else-if="driveLoading">
      <div class="card drive-applications__stat-skeleton" v-for="i in 3" :key="i"></div>
    </div>

    <!-- Filter bar -->
    <AppFilterBar v-model="searchQuery" placeholder="Search by name, branch, roll number...">
      <select class="filter-select" v-model="statusFilter">
        <option value="">All Statuses</option>
        <option value="applied">Applied</option>
        <option value="shortlisted">Shortlisted</option>
        <option value="selected">Selected</option>
        <option value="rejected">Rejected</option>
      </select>
    </AppFilterBar>

    <!-- Table card -->
    <div class="card drive-applications__table-card">

      <div v-if="loading" class="drive-applications__spinner-wrap">
        <AppSpinner />
      </div>

      <AppEmptyState
        v-else-if="error"
        icon="bi bi-exclamation-circle"
        title="Failed to load applications"
        :subtitle="error"
        actionLabel="Retry"
        @action="fetchAll"
      />

      <AppEmptyState
        v-else-if="!applications.length"
        icon="bi bi-people"
        title="No applications yet"
        subtitle="Students haven't applied to this drive yet."
      />

      <AppEmptyState
        v-else-if="!filteredApplications.length"
        icon="bi bi-search"
        title="No applications match your filters"
        subtitle="Try adjusting your search or status filter."
      />

      <template v-else>
        <div class="drive-applications__table-wrap">
          <table>
            <thead>
              <tr>
                <th class="drive-applications__th-check">
                  <input
                    type="checkbox"
                    :checked="isAllSelected"
                    :indeterminate.prop="isIndeterminate"
                    @change="toggleSelectAll"
                  />
                </th>
                <th>Student Name</th>
                <th>Branch</th>
                <th>CGPA</th>
                <th>Applied On</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in filteredApplications" :key="app.application_id">
                <td class="drive-applications__td-check">
                  <input
                    type="checkbox"
                    :value="app.application_id"
                    v-model="selectedIdsArray"
                  />
                </td>

                <td>
                  <div class="drive-applications__student-cell">
                    <AppAvatar :name="app.student_name" size="sm" />
                    <div class="drive-applications__student-info">
                      <span
                        class="drive-applications__student-name table-link"
                        @click="router.push('/company/students/' + app.roll_number)"
                      >{{ app.student_name }}</span>
                      <span class="drive-applications__student-meta">{{ app.email || 'Roll: ' + app.roll_number }}</span>
                    </div>
                  </div>
                </td>

                <td>{{ app.branch || '—' }}</td>
                <td>{{ formatCGPA(app.cgpa) }}</td>
                <td>{{ formatDate(app.applied_at) }}</td>

                <td>
                  <div class="drive-applications__status-cell">
                    <AppBadge :status="statuses[app.application_id]" />
                    <span
                      v-if="interviews[app.application_id]?.interview_date"
                      class="drive-applications__interview-chip"
                    >
                      <i class="bi bi-calendar2-check"></i>
                      {{ formatDate(interviews[app.application_id].interview_date) }}
                    </span>
                  </div>
                </td>

                <td>
                  <div class="drive-applications__actions-cell">
                    <button
                      v-if="app.resume_filename"
                      class="drive-applications__action-btn"
                      title="Download Resume"
                      @click="handleDownloadResume(app)"
                    >
                      <i class="bi bi-file-earmark-pdf"></i>
                    </button>
                    <a
                      v-if="app.linkedin_url"
                      :href="app.linkedin_url"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="drive-applications__action-btn"
                      title="LinkedIn Profile"
                    >
                      <i class="bi bi-linkedin"></i>
                    </a>

                    <div
                      class="drive-applications__kebab-wrap"
                      :ref="el => setKebabRef(el, app.application_id)"
                    >
                      <button
                        class="drive-applications__action-btn"
                        title="More actions"
                        @click.stop="toggleKebab(app.application_id, $event)"
                      >
                        <i class="bi bi-three-dots-vertical"></i>
                      </button>
                      <div v-if="openKebabId === app.application_id" class="drive-applications__kebab-menu" :style="menuStyle">
                        <template v-if="statuses[app.application_id] === 'applied'">
                          <button class="drive-applications__kebab-item drive-applications__kebab-item--shortlist" :disabled="actionPending[app.application_id]" @click="handleStatusChange(app, 'shortlisted'); openKebabId = null">
                            Shortlist
                          </button>
                          <button class="drive-applications__kebab-item drive-applications__kebab-item--reject" :disabled="actionPending[app.application_id]" @click="handleStatusChange(app, 'rejected'); openKebabId = null">
                            Reject
                          </button>
                        </template>
                        <template v-else-if="statuses[app.application_id] === 'shortlisted'">
                          <button class="drive-applications__kebab-item drive-applications__kebab-item--select" :disabled="actionPending[app.application_id]" @click="handleStatusChange(app, 'selected'); openKebabId = null">
                            Select
                          </button>
                          <button class="drive-applications__kebab-item" :disabled="actionPending[app.application_id]" @click="openInterviewModal(app); openKebabId = null">
                            {{ interviews[app.application_id]?.interview_date ? 'Reschedule Interview' : 'Schedule Interview' }}
                          </button>
                          <button class="drive-applications__kebab-item drive-applications__kebab-item--reject" :disabled="actionPending[app.application_id]" @click="handleStatusChange(app, 'rejected'); openKebabId = null">
                            Reject
                          </button>
                        </template>
                        <template v-else-if="statuses[app.application_id] === 'selected'">
                          <button class="drive-applications__kebab-item drive-applications__kebab-item--reject" :disabled="actionPending[app.application_id]" @click="handleStatusChange(app, 'rejected'); openKebabId = null">
                            Reject
                          </button>
                        </template>
                        <template v-else>
                          <span class="drive-applications__kebab-empty">No actions available</span>
                        </template>
                      </div>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </template>

    </div>

    <!-- ── Interview scheduling modal ── -->
    <AppModal
      :show="interviewModal.show"
      title="Schedule Interview"
      headerIcon="bi bi-calendar2-check"
      confirmLabel="Save Interview"
      :loading="interviewSaving"
      @confirm="saveInterview"
      @cancel="closeInterviewModal"
    >
      <div class="interview-form">
        <div class="interview-form__field">
          <label class="interview-form__label">Date &amp; Time <span class="interview-form__required">*</span></label>
          <input type="datetime-local" v-model="interviewForm.interview_date" :min="minInterviewDatetime" />
        </div>
        <div class="interview-form__field">
          <label class="interview-form__label">Mode</label>
          <select v-model="interviewForm.interview_mode">
            <option value="Online">Online</option>
            <option value="Offline">Offline</option>
          </select>
        </div>
        <div v-if="interviewForm.interview_mode === 'Online'" class="interview-form__field">
          <label class="interview-form__label">Interview Link <span class="interview-form__required">*</span></label>
          <input type="url" v-model="interviewForm.interview_link" placeholder="https://meet.google.com/..." />
        </div>
        <div v-if="interviewError" class="interview-form__error">
          <i class="bi bi-exclamation-circle"></i> {{ interviewError }}
        </div>
      </div>
    </AppModal>

    <!-- ── Bulk reject confirm modal ── -->
    <AppModal
      :show="bulkRejectModalOpen"
      title="Reject Selected Applicants"
      headerIcon="bi bi-x-circle"
      confirmLabel="Reject"
      confirmVariant="danger"
      :loading="bulkRejectLoading"
      warningMessage="Rejected applications cannot be restored."
      @confirm="handleBulkReject"
      @cancel="bulkRejectModalOpen = false"
    >
      <p>You are about to reject <strong>{{ selectedIdsArray.length }}</strong> selected applicant(s).</p>
    </AppModal>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as companyApi from '@/api/company'
import { formatDate, formatCGPA } from '@/utils/formatters'
import { ApplicationStatus } from '@/utils/constants'

import AppBadge from '@/components/common/AppBadge.vue'
import AppAvatar from '@/components/common/AppAvatar.vue'
import AppFilterBar from '@/components/common/AppFilterBar.vue'
import AppSpinner from '@/components/common/AppSpinner.vue'
import AppEmptyState from '@/components/common/AppEmptyState.vue'
import AppModal from '@/components/common/AppModal.vue'
import StatCard from '@/components/admin/StatCard.vue'

const route = useRoute()
const router = useRouter()

const driveId = computed(() => route.params.id)

// ── Drive data (header + stat cards) ──
const drive = ref(null)
const driveLoading = ref(false)

const driveBadgeStatus = computed(() => {
  const s = drive.value?.status
  if (!s) return 'pending'
  return s === 'approved' ? 'active' : s
})

// ── Applications list ──
const applications = ref([])
const loading = ref(false)
const error = ref(null)

// Status map for inline editing: { [application_id]: status }
const statuses = ref({})

// ── Filters ──
const searchQuery = ref('')
const statusFilter = ref('')

// ── Selection ──
const selectedIdsArray = ref([])
// ── Async loading flags ──
const bulkLoading = ref(false)
const bulkRejectLoading = ref(false)
const bulkRejectModalOpen = ref(false)

// ── Per-row action pending (prevents double-clicks) ──
const actionPending = ref({})

// ── Interview data: { [applicationId]: { interview_date, interview_mode, interview_link } } ──
const interviews = ref({})

// ── Interview modal ──
const interviewModal = ref({ show: false, app: null })
const interviewForm = ref({ interview_date: '', interview_mode: 'Online', interview_link: '' })
const interviewSaving = ref(false)
const interviewError = ref('')

const minInterviewDatetime = computed(() => {
  const d = new Date(Date.now() + 60_000)
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset())
  return d.toISOString().slice(0, 16)
})

// ── Toast ──
const toast = ref({ message: '', type: 'success' })
let toastTimer = null

// ── Data fetching ──

async function fetchDrive() {
  driveLoading.value = true
  try {
    const res = await companyApi.getDrive(driveId.value)
    drive.value = res.data
  } catch {
    // Non-critical — header just shows empty
  } finally {
    driveLoading.value = false
  }
}

async function fetchApplications() {
  loading.value = true
  error.value = null
  try {
    const res = await companyApi.getDriveApplications(driveId.value)
    applications.value = res.data || []
    const statusMap = {}
    const interviewMap = {}
    for (const app of applications.value) {
      statusMap[app.application_id] = app.status
      interviewMap[app.application_id] = {
        interview_date: app.interview_date ?? null,
        interview_mode: app.interview_mode ?? null,
        interview_link: app.interview_link ?? null,
      }
    }
    statuses.value = statusMap
    interviews.value = interviewMap
  } catch (e) {
    error.value = e.response?.data?.message || e.message || 'Failed to load applications.'
  } finally {
    loading.value = false
  }
}

function fetchAll() {
  fetchDrive()
  fetchApplications()
}

// ── Kebab menu ──
const openKebabId = ref(null)
const menuStyle = ref({})
const kebabRefs = {}

const setKebabRef = (el, id) => {
  if (el) kebabRefs[id] = el
  else delete kebabRefs[id]
}

const toggleKebab = (id, event) => {
  if (openKebabId.value === id) {
    openKebabId.value = null
    return
  }
  const rect = event.currentTarget.getBoundingClientRect()
  const right = window.innerWidth - rect.right
  if (window.innerHeight - rect.bottom < 150) {
    menuStyle.value = { bottom: (window.innerHeight - rect.top) + 'px', right: right + 'px', top: 'auto' }
  } else {
    menuStyle.value = { top: rect.bottom + 'px', right: right + 'px', bottom: 'auto' }
  }
  openKebabId.value = id
}

const handleOutsideClick = (e) => {
  if (openKebabId.value === null) return
  const el = kebabRefs[openKebabId.value]
  if (el && !el.contains(e.target)) openKebabId.value = null
}

onMounted(() => {
  fetchAll()
  document.addEventListener('click', handleOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick)
})

// ── Filtered list ──

const filteredApplications = computed(() => {
  let list = applications.value
  const q = searchQuery.value.trim().toLowerCase()
  const s = statusFilter.value

  if (q) {
    list = list.filter(
      (app) =>
        app.student_name?.toLowerCase().includes(q) ||
        app.branch?.toLowerCase().includes(q) ||
        String(app.roll_number).toLowerCase().includes(q)
    )
  }
  if (s) {
    list = list.filter((app) => statuses.value[app.application_id] === s)
  }
  return list
})

watch([searchQuery, statusFilter], () => {
  selectedIdsArray.value = []
})

// ── Bulk select ──

const isAllSelected = computed(
  () =>
    filteredApplications.value.length > 0 &&
    filteredApplications.value.every((a) => selectedIdsArray.value.includes(a.application_id))
)

const isIndeterminate = computed(
  () =>
    !isAllSelected.value &&
    filteredApplications.value.some((a) => selectedIdsArray.value.includes(a.application_id))
)

function toggleSelectAll() {
  if (isAllSelected.value) {
    selectedIdsArray.value = []
  } else {
    selectedIdsArray.value = filteredApplications.value.map((a) => a.application_id)
  }
}

// ── Status update (single row) ──

async function handleStatusChange(app, newStatus) {
  const id = app.application_id
  const prevStatus = statuses.value[id]
  if (prevStatus === newStatus || actionPending.value[id]) return
  statuses.value[id] = newStatus
  actionPending.value[id] = true
  try {
    await companyApi.updateApplicationStatus(id, { status: newStatus })
    showToast(`${app.student_name}'s status updated to ${newStatus}.`)
    fetchDrive()
  } catch (e) {
    statuses.value[id] = prevStatus
    showToast(e.response?.data?.message || 'Failed to update status.', 'error')
  } finally {
    actionPending.value[id] = false
  }
}

// ── Bulk shortlist ──

async function handleShortlistSelected() {
  const eligibleIds = selectedIdsArray.value.filter(
    (id) => statuses.value[id] === ApplicationStatus.APPLIED
  )
  if (!eligibleIds.length) {
    showToast('No "Applied" applicants selected to shortlist.', 'error')
    return
  }
  bulkLoading.value = true
  let successCount = 0
  let failCount = 0
  await Promise.allSettled(
    eligibleIds.map(async (id) => {
      try {
        await companyApi.updateApplicationStatus(id, { status: ApplicationStatus.SHORTLISTED })
        statuses.value[id] = ApplicationStatus.SHORTLISTED
        successCount++
      } catch {
        failCount++
      }
    })
  )
  bulkLoading.value = false
  selectedIdsArray.value = []
  if (successCount) showToast(`${successCount} applicant(s) shortlisted successfully.`)
  if (failCount) showToast(`${failCount} update(s) failed.`, 'error')
  if (successCount) fetchDrive()
}

// ── Bulk reject ──

async function handleBulkReject() {
  const eligibleIds = selectedIdsArray.value.filter(
    (id) => statuses.value[id] !== ApplicationStatus.REJECTED
  )
  if (!eligibleIds.length) {
    showToast('No eligible applicants to reject.', 'error')
    bulkRejectModalOpen.value = false
    bulkRejectLoading.value = false
    return
  }
  bulkRejectLoading.value = true
  let successCount = 0
  let failCount = 0
  await Promise.allSettled(
    eligibleIds.map(async (id) => {
      try {
        await companyApi.updateApplicationStatus(id, { status: ApplicationStatus.REJECTED })
        statuses.value[id] = ApplicationStatus.REJECTED
        successCount++
      } catch {
        failCount++
      }
    })
  )
  bulkRejectLoading.value = false
  bulkRejectModalOpen.value = false
  selectedIdsArray.value = []
  if (successCount) showToast(`${successCount} applicant(s) rejected.`)
  if (failCount) showToast(`${failCount} update(s) failed.`, 'error')
  if (successCount) fetchDrive()
}

// ── Interview scheduling ──

function toLocalDatetimeString(isoString) {
  if (!isoString) return ''
  const d = new Date(isoString)
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset())
  return d.toISOString().slice(0, 16)
}

function openInterviewModal(app) {
  const existing = interviews.value[app.application_id]
  interviewForm.value = {
    interview_date: toLocalDatetimeString(existing?.interview_date),
    interview_mode: existing?.interview_mode || 'Online',
    interview_link: existing?.interview_link || '',
  }
  interviewError.value = ''
  interviewModal.value = { show: true, app }
}

function closeInterviewModal() {
  interviewModal.value = { show: false, app: null }
  interviewError.value = ''
}

async function saveInterview() {
  interviewError.value = ''
  const { interview_date, interview_mode, interview_link } = interviewForm.value
  if (!interview_date) {
    interviewError.value = 'Interview date and time is required.'
    return
  }
  if (interview_mode === 'Online' && !interview_link.trim()) {
    interviewError.value = 'Interview link is required for Online mode.'
    return
  }
  const payload = {
    interview_date: new Date(interview_date).toISOString(),
    interview_mode,
    interview_link: interview_mode === 'Online' ? interview_link.trim() : null,
  }
  const app = interviewModal.value.app
  interviewSaving.value = true
  try {
    await companyApi.updateApplicationInterview(app.application_id, payload)
    interviews.value[app.application_id] = {
      interview_date: payload.interview_date,
      interview_mode: payload.interview_mode,
      interview_link: payload.interview_link,
    }
    showToast(`Interview scheduled for ${app.student_name}.`)
    closeInterviewModal()
  } catch (e) {
    interviewError.value = e.response?.data?.message || 'Failed to save interview details.'
  } finally {
    interviewSaving.value = false
  }
}

// ── Resume download ──

function handleDownloadResume(app) {
  companyApi.downloadResume(app.application_id, app.resume_filename)
}

// ── Toast helper ──

function showToast(message, type = 'success') {
  toast.value = { message, type }
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toast.value = { message: '', type: 'success' }
  }, 3500)
}
</script>

<style scoped>
.drive-applications {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  position: relative;
}

/* ── Toast ── */
.drive-applications__toast {
  position: fixed;
  top: var(--space-5);
  right: var(--space-5);
  z-index: var(--z-tooltip);
  padding: var(--space-3) var(--space-5);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  box-shadow: var(--shadow-md);
  max-width: 360px;
}

.drive-applications__toast--success {
  background-color: var(--color-success-light);
  color: var(--color-success);
  border: var(--border-width) solid var(--color-success);
}

.drive-applications__toast--error {
  background-color: var(--color-danger-light);
  color: var(--color-danger-dark);
  border: var(--border-width) solid var(--color-danger);
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity var(--transition-base), transform var(--transition-base);
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(calc(-1 * var(--space-2)));
}

/* ── Back link ── */
.drive-applications__back {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  text-decoration: none;
  width: fit-content;
  transition: color var(--transition-fast);
}

.drive-applications__back:hover {
  color: var(--color-primary);
}

/* ── Header ── */
.drive-applications__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  flex-wrap: wrap;
}

.drive-applications__header-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-height: 36px;
}

.drive-applications__title-skeleton {
  width: 280px;
  height: 30px;
  border-radius: var(--border-radius-md);
  background: var(--color-gray-100);
  animation: pulse 1.4s ease-in-out infinite;
}

.drive-applications__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.drive-applications__header-actions {
  display: flex;
  gap: var(--space-3);
  flex-wrap: wrap;
  align-items: center;
}

/* ── Stat cards ── */
.drive-applications__stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
}

.drive-applications__stat-skeleton {
  height: 90px;
  background: var(--color-card-bg);
  animation: pulse 1.4s ease-in-out infinite;
}

/* ── Table card ── */
.drive-applications__table-card {
  padding: 0;
  overflow: hidden;
}

.drive-applications__spinner-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: var(--space-10);
}

.drive-applications__table-wrap {
  overflow-x: auto;
}

/* Checkbox column */
.drive-applications__th-check,
.drive-applications__td-check {
  width: 48px;
  text-align: center;
  padding-left: var(--space-4);
  padding-right: 0;
}

/* Student cell */
.drive-applications__student-cell {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.drive-applications__student-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.drive-applications__student-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.drive-applications__student-meta {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

/* ── Status cell ── */
.drive-applications__status-cell {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--space-1);
}

.drive-applications__interview-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: var(--font-size-xs);
  color: var(--color-primary);
  background: var(--color-primary-light);
  border-radius: var(--border-radius-pill);
  padding: 2px var(--space-2);
  white-space: nowrap;
}

/* ── Row actions ── */
.drive-applications__actions-cell {
  display: flex;
  flex-direction: row;
  gap: var(--space-1);
  align-items: center;
}

/* ── Kebab menu ── */
.drive-applications__kebab-wrap {
  position: relative;
  display: inline-block;
}

.drive-applications__kebab-menu {
  position: fixed;
  background: var(--color-white);
  border: var(--border-width) solid var(--border-color);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  min-width: 170px;
  z-index: 1000;
}

.drive-applications__kebab-item {
  display: block;
  width: 100%;
  padding-block: var(--space-2);
  padding-inline: var(--space-4);
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  transition: background var(--transition-fast);
  outline: none;
}

.drive-applications__kebab-item:hover:not(:disabled) {
  background: var(--color-gray-50);
}

.drive-applications__kebab-item:disabled {
  opacity: var(--opacity-disabled);
  cursor: not-allowed;
}

.drive-applications__kebab-item--shortlist { color: var(--color-primary); }
.drive-applications__kebab-item--select { color: var(--color-success); }
.drive-applications__kebab-item--reject { color: var(--color-danger); }

.drive-applications__kebab-empty {
  display: block;
  padding: var(--space-2) var(--space-4);
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.drive-applications__action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-1);
  border-radius: var(--border-radius-sm);
  color: var(--color-text-muted);
  font-size: var(--font-size-md);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background-color var(--transition-fast), color var(--transition-fast);
  outline: none;
  text-decoration: none;
  flex-shrink: 0;
}

.drive-applications__action-btn:hover {
  background-color: var(--color-gray-100);
  color: var(--color-text-primary);
}

/* ── Skeleton animation ── */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.5; }
}

/* ── Interview form (inside AppModal slot) ── */
.interview-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding-top: var(--space-2);
}

.interview-form__field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.interview-form__label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.interview-form__required {
  color: var(--color-danger);
}

.interview-form__error {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-sm);
  color: var(--color-danger-dark);
  background: var(--color-danger-light);
  border: var(--border-width) solid var(--color-danger);
  border-radius: var(--border-radius-md);
  padding: var(--space-2) var(--space-3);
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .drive-applications__stats {
    grid-template-columns: 1fr;
  }

  .drive-applications__header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
