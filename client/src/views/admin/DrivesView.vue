<template>
  <div class="drives">
    <Transition name="toast">
      <div
        v-if="feedbackMessage"
        class="drives__toast"
        :class="feedbackType === 'error' ? 'drives__toast--error' : 'drives__toast--success'"
      >
        <i :class="feedbackType === 'error' ? 'bi bi-x-circle-fill' : 'bi bi-check-circle-fill'"></i>
        {{ feedbackMessage }}
      </div>
    </Transition>

    <header class="drives__header">
      <div>
        <h1 class="drives__title">Placement Drives</h1>
        <p class="drives__subtitle">Review and manage company placement drive requests.</p>
      </div>
      <AppButton variant="primary" iconLeft="bi bi-plus-lg" @click="router.push('/admin/drives/create')">
        Create Drive
      </AppButton>
    </header>

    <AppFilterBar v-model="searchQuery" placeholder="Search by job title, company...">
      <select class="filter-select" v-model="activeStatusFilter">
        <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </option>
      </select>
    </AppFilterBar>

    <div class="card drives__table-card">
      <AppSpinner v-if="adminStore.loading" />

      <AppEmptyState
        v-else-if="adminStore.error"
        icon="bi bi-exclamation-circle"
        title="Failed to load drives"
        :subtitle="adminStore.error"
        actionLabel="Retry"
        @action="loadDrives"
      />

      <AppEmptyState
        v-else-if="!adminStore.drives.length"
        icon="bi bi-briefcase"
        title="No drives found"
        subtitle="No placement drives match your current filters."
      />

      <template v-else>
        <div class="drives__table-wrap">
          <table>
            <thead>
              <tr>
                <th>Job Title / Role</th>
                <th>Company</th>
                <th>Deadline</th>
                <th>Eligibility</th>
                <th>Applicants</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="drive in adminStore.drives" :key="drive.id">
                <td>
                  <div class="drives__job-title table-link" @click="router.push('/admin/drives/' + drive.id)">{{ drive.job_title }}</div>
                  <div class="drives__job-meta">
                    {{ drive.job_type }}<template v-if="drive.salary_package"> • {{ drive.salary_package }}</template>
                  </div>
                </td>
                <td>
                  <div class="drives__company-cell">
                    <AppAvatar :name="drive.company_name" size="sm" />
                    <span class="table-link" @click="router.push('/admin/companies/' + drive.company_id)">{{ drive.company_name }}</span>
                  </div>
                </td>
                <td>
                  <DeadlineCell :deadline="drive.application_deadline" />
                </td>
                <td>
                  <div class="drives__eligibility-cell">
                    <EligibilityTag
                      v-if="drive.min_cgpa > 0"
                      :label="'CGPA > ' + drive.min_cgpa"
                    />
                    <template v-if="parsedBranches(drive).length">
                      <EligibilityTag
                        v-for="branch in parsedBranches(drive)"
                        :key="branch"
                        :label="branch"
                      />
                    </template>
                    <EligibilityTag v-if="drive.other_criteria" :label="drive.other_criteria" />
                  </div>
                </td>
                <td>
                  <span
                    v-if="drive.applicant_count > 0"
                    class="drives__applicant-count"
                  >{{ formatNumber(drive.applicant_count) }}</span>
                  <span v-else class="drives__applicant-none">–</span>
                </td>
                <td>
                  <AppBadge :status="drive.status" />
                </td>
                <td>
                  <div class="drives__actions">
                    <div class="drives__kebab-wrap" :ref="el => setKebabRef(el, drive.id)">
                      <button
                        class="drives__action-btn"
                        title="More actions"
                        @click.stop="toggleKebab(drive.id, $event)"
                      >
                        <i class="bi bi-three-dots-vertical"></i>
                      </button>
                      <div v-if="openKebabId === drive.id" class="drives__kebab-menu" :style="menuStyle">
                        <button class="drives__kebab-item" @click="navigateAndClose(drive.id)">
                          View Details
                        </button>
                        <template v-if="drive.status === DriveStatus.PENDING">
                          <button class="drives__kebab-item drives__kebab-item--success" @click="openModalAndClose('approve', drive)">
                            Approve Drive
                          </button>
                          <button class="drives__kebab-item drives__kebab-item--danger" @click="openModalAndClose('reject', drive)">
                            Reject Drive
                          </button>
                        </template>
                        <template v-else-if="drive.status === DriveStatus.APPROVED">
                          <button class="drives__kebab-item drives__kebab-item--danger" @click="openModalAndClose('reject', drive)">
                            Reject Drive
                          </button>
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

    <AppModal
      :show="modalState.show && modalState.type === 'approve'"
      title="Approve Placement Drive"
      headerIcon="bi bi-briefcase-fill"
      confirmLabel="Approve Drive"
      confirmVariant="primary"
      warningMessage="Students will be able to see and apply to this drive immediately."
      :loading="adminStore.actionLoading"
      @confirm="handleApproveConfirm"
      @cancel="closeModal"
    >
      <div class="drives__modal-summary">
        <div class="drives__modal-title">{{ modalState.drive?.job_title }}</div>
        <div class="drives__modal-company">{{ modalState.drive?.company_name }}</div>
        <div class="drives__modal-grid">
          <div>
            <div class="drives__modal-label">Deadline</div>
            <div class="drives__modal-value">
              {{ modalState.drive ? formatDate(modalState.drive.application_deadline, { style: 'short' }) : '' }}
            </div>
          </div>
          <div v-if="modalState.drive?.vacancy_count">
            <div class="drives__modal-label">Vacancies</div>
            <div class="drives__modal-value">{{ modalState.drive.vacancy_count }}</div>
          </div>
        </div>
      </div>
    </AppModal>

    <AppModal
      :show="modalState.show && modalState.type === 'reject'"
      title="Reject Placement Drive"
      headerIcon="bi bi-x-circle"
      confirmLabel="Reject Drive"
      confirmVariant="danger"
      warningMessage="The company will be notified of the rejection."
      :loading="adminStore.actionLoading"
      @confirm="handleRejectConfirm"
      @cancel="closeModal"
    >
      <div>
        <div class="drives__modal-title">{{ modalState.drive?.job_title }}</div>
        <div class="drives__modal-company">{{ modalState.drive?.company_name }}</div>
        <label class="drives__modal-label drives__modal-label--mt" for="reject-reason">
          Reason for rejection
        </label>
        <textarea
          id="reject-reason"
          class="drives__reject-textarea"
          v-model="modalState.reason"
          rows="3"
          placeholder="Provide a reason..."
        ></textarea>
        <p v-if="modalState.rejectError" class="drives__reject-error">{{ modalState.rejectError }}</p>
      </div>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { formatDate, formatNumber } from '@/utils/formatters'
import { DriveStatus } from '@/utils/constants'

import AppButton from '@/components/common/AppButton.vue'
import AppFilterBar from '@/components/common/AppFilterBar.vue'
import AppBadge from '@/components/common/AppBadge.vue'
import AppAvatar from '@/components/common/AppAvatar.vue'
import AppSpinner from '@/components/common/AppSpinner.vue'
import AppEmptyState from '@/components/common/AppEmptyState.vue'
import AppModal from '@/components/common/AppModal.vue'
import EligibilityTag from '@/components/admin/EligibilityTag.vue'
import DeadlineCell from '@/components/admin/DeadlineCell.vue'

const router = useRouter()
const route = useRoute()
const adminStore = useAdminStore()

const searchQuery = ref('')
const activeStatusFilter = ref('all')
const openKebabId = ref(null)
const menuStyle = ref({})
const feedbackMessage = ref('')
const feedbackType = ref('success')

const kebabRefs = {}

const statusOptions = [
  { label: 'All', value: 'all' },
  { label: 'Pending', value: DriveStatus.PENDING },
  { label: 'Approved', value: DriveStatus.APPROVED },
  { label: 'Closed', value: DriveStatus.CLOSED }
]

const modalState = reactive({
  show: false,
  type: null,
  drive: null,
  reason: '',
  rejectError: ''
})

let searchTimer = null
let feedbackTimer = null

const showFeedback = (message, type = 'success') => {
  feedbackMessage.value = message
  feedbackType.value = type
  clearTimeout(feedbackTimer)
  feedbackTimer = setTimeout(() => { feedbackMessage.value = '' }, 3000)
}

const parsedBranches = (drive) => {
  const raw = drive.eligible_branches?.split(',').map(b => b.trim()).filter(Boolean) ?? []
  if (!raw.length || raw[0].toLowerCase() === 'all') return ['Any Branch']
  return raw
}

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

const navigateAndClose = (id) => {
  openKebabId.value = null
  router.push('/admin/drives/' + id)
}

const openModalAndClose = (type, drive) => {
  openKebabId.value = null
  openModal(type, drive)
}

const handleOutsideClick = (e) => {
  if (openKebabId.value === null) return
  const el = kebabRefs[openKebabId.value]
  if (el && !el.contains(e.target)) {
    openKebabId.value = null
  }
}

const loadDrives = () => {
  const status = activeStatusFilter.value === 'all' ? '' : activeStatusFilter.value
  adminStore.fetchDrives({ status, search: searchQuery.value, page: 1 })
}

const openModal = (type, drive) => {
  modalState.type = type
  modalState.drive = drive
  modalState.reason = ''
  modalState.rejectError = ''
  modalState.show = true
}

const closeModal = () => {
  modalState.show = false
  setTimeout(() => {
    modalState.type = null
    modalState.drive = null
    modalState.reason = ''
    modalState.rejectError = ''
  }, 300)
}

const handleApproveConfirm = async () => {
  try {
    await adminStore.approveDrive(modalState.drive.id)
    closeModal()
    showFeedback('Drive approved successfully.')
  } catch {
    showFeedback(adminStore.error || 'Failed to approve drive.', 'error')
  }
}

const handleRejectConfirm = async () => {
  if (!modalState.reason.trim()) {
    modalState.rejectError = 'Rejection reason is required.'
    return
  }
  try {
    await adminStore.rejectDrive(modalState.drive.id, modalState.reason)
    closeModal()
    showFeedback('Drive rejected.')
  } catch {
    showFeedback(adminStore.error || 'Failed to reject drive.', 'error')
  }
}

watch(activeStatusFilter, () => { loadDrives() })

watch(searchQuery, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { loadDrives() }, 300)
})

onMounted(() => {
  const q = route.query.status
  const match = statusOptions.find(o => o.value === q)
  if (match) activeStatusFilter.value = match.value
  loadDrives()
  document.addEventListener('click', handleOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick)
})
</script>

<style scoped>
.drives {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.drives__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
}

.drives__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-1) 0;
}

.drives__subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin: 0;
}

.drives__table-card {
  padding: 0;
  overflow: hidden;
}

.drives__table-wrap {
  overflow-x: auto;
}

.drives__job-title {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
}

.drives__job-meta {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  margin-top: var(--space-1);
}

.drives__company-cell {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.drives__eligibility-cell {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
}

.drives__applicant-count {
  color: var(--color-primary);
  font-weight: var(--font-weight-semibold);
}

.drives__applicant-none {
  color: var(--color-text-muted);
}

.drives__actions {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.drives__action-btn {
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
}

.drives__action-btn:hover {
  background-color: var(--color-gray-100);
  color: var(--color-text-primary);
}

.drives__kebab-wrap {
  position: relative;
  display: inline-block;
}

.drives__kebab-menu {
  position: fixed;
  background: var(--color-white);
  border: var(--border-width) solid var(--border-color);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  min-width: 160px;
  z-index: 1000;
}

.drives__kebab-item {
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

.drives__kebab-item:hover {
  background: var(--color-gray-50);
}

.drives__kebab-item--danger {
  color: var(--color-danger);
}

.drives__kebab-item--success {
  color: var(--color-success);
}

.drives__modal-summary {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.drives__modal-title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.drives__modal-company {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.drives__modal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
  margin-top: var(--space-2);
}

.drives__modal-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  font-weight: var(--font-weight-medium);
  margin-bottom: var(--space-1);
}

.drives__modal-label--mt {
  display: block;
  margin-top: var(--space-4);
}

.drives__modal-value {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.drives__reject-textarea {
  width: 100%;
  margin-top: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border: var(--border-width) solid var(--border-color);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  background: var(--color-white);
  resize: vertical;
  outline: none;
  transition: border-color var(--transition-fast);
}

.drives__reject-textarea:focus {
  border-color: var(--color-primary);
}

.drives__reject-error {
  margin-top: var(--space-2);
  font-size: var(--font-size-xs);
  color: var(--color-danger);
}

.drives__toast {
  position: fixed;
  top: var(--space-6);
  right: var(--space-6);
  z-index: var(--z-tooltip);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding-block: var(--space-3);
  padding-inline: var(--space-5);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-white);
}

.drives__toast--success {
  background-color: var(--color-success);
}

.drives__toast--error {
  background-color: var(--color-danger);
}

.toast-enter-active,
.toast-leave-active {
  transition: all var(--transition-base);
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(calc(-1 * var(--space-3)));
}

@media (max-width: 767px) {
  .drives__filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .drives__status-group {
    flex-wrap: wrap;
  }
}
</style>
