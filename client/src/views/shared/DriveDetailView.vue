<template>
  <div class="drive-detail">
    <Transition name="toast">
      <div
        v-if="feedbackMessage"
        class="drive-detail__toast"
        :class="feedbackType === 'error' ? 'drive-detail__toast--error' : 'drive-detail__toast--success'"
      >
        <i :class="feedbackType === 'error' ? 'bi bi-x-circle-fill' : 'bi bi-check-circle-fill'"></i>
        {{ feedbackMessage }}
      </div>
    </Transition>

    <AppSpinner v-if="loading && !drive" :fullPage="true" />

    <AppEmptyState
      v-else-if="fetchError"
      icon="bi bi-exclamation-circle"
      title="Failed to load drive"
      :subtitle="fetchError"
      actionLabel="Retry"
      @action="loadDrive"
    />

    <template v-else-if="drive">
      <div class="drive-hero">
        <div class="drive-hero__top">
          <div class="drive-hero__pills">
            <span
              class="drive-hero__pill"
              :class="drive.status === DriveStatus.APPROVED ? 'drive-hero__pill--open' : 'drive-hero__pill--closed'"
            >{{ drive.status === DriveStatus.APPROVED ? 'OPEN' : 'CLOSED' }}</span>
            <span class="drive-hero__pill drive-hero__pill--type">{{ drive.job_type }}</span>
          </div>
        </div>
        <div class="drive-hero__bottom">
          <div class="drive-hero__identity">
            <h1 class="drive-hero__title">{{ drive.job_title }}</h1>
            <p class="drive-hero__company">
              <i class="bi bi-buildings"></i>
              {{ drive.company_name }}
            </p>
          </div>
          <div class="drive-hero__apply-slot">
            <template v-if="isStudent">
              <AppButton
                v-if="drive.is_eligible && !drive.has_applied"
                variant="primary"
                @click="applyModalOpen = true"
              >Apply Now</AppButton>
              <span v-else-if="drive.has_applied" class="drive-hero__applied-pill">
                <i class="bi bi-check-circle"></i>
                Already Applied
              </span>
            </template>
          </div>
        </div>
      </div>

      <div v-if="isAdmin && drive.status === DriveStatus.PENDING" class="drive-detail__admin-bar">
        <AppButton variant="primary" @click="openModal('approve', drive)">Approve Drive</AppButton>
        <AppButton variant="danger" @click="openModal('reject', drive)">Reject Drive</AppButton>
      </div>

      <div class="drive-detail__stats-grid">
        <div class="card drive-detail__stat-card">
          <div class="drive-detail__stat-label">CTC / Stipend</div>
          <div class="drive-detail__stat-value">
            <i class="bi bi-currency-rupee drive-detail__stat-icon"></i>
            <span>{{ drive.salary_package || 'Not disclosed' }}</span>
          </div>
        </div>
        <div class="card drive-detail__stat-card">
          <div class="drive-detail__stat-label">Deadline</div>
          <div class="drive-detail__stat-value">
            <i class="bi bi-calendar drive-detail__stat-icon"></i>
            <span>{{ formatDate(drive.application_deadline, { style: 'short' }) }}</span>
          </div>
        </div>
        <div class="card drive-detail__stat-card">
          <div class="drive-detail__stat-label">Location</div>
          <div class="drive-detail__stat-value">
            <i class="bi bi-geo-alt drive-detail__stat-icon"></i>
            <span>{{ drive.job_location || 'Not specified' }}</span>
          </div>
        </div>
        <div class="card drive-detail__stat-card">
          <div class="drive-detail__stat-label">Total Vacancies</div>
          <div class="drive-detail__stat-value">
            <i class="bi bi-people drive-detail__stat-icon"></i>
            <span>{{ drive.vacancy_count ?? '—' }} Positions</span>
          </div>
        </div>
      </div>

      <div class="drive-detail__content">
        <div class="drive-detail__left">
          <div class="card drive-detail__card">
            <div class="drive-detail__card-header">
              <i class="bi bi-file-text-fill drive-detail__card-icon"></i>
              <h2 class="drive-detail__card-title">Job Description</h2>
            </div>
            <p class="drive-detail__description">{{ drive.description || 'No description provided.' }}</p>
          </div>

          <div v-if="drive.other_criteria" class="card drive-detail__card">
            <div class="drive-detail__card-header">
              <i class="bi bi-shield-check drive-detail__card-icon"></i>
              <h2 class="drive-detail__card-title">Technical Requirements</h2>
            </div>
            <div v-if="parsedSkills.length" class="drive-detail__tags-row">
              <EligibilityTag v-for="skill in parsedSkills" :key="skill" :label="skill" />
            </div>
            <p v-else class="drive-detail__description">{{ drive.other_criteria }}</p>
          </div>
        </div>

        <aside class="drive-detail__right">
          <div class="card drive-detail__card">
            <div class="drive-detail__card-header">
              <i class="bi bi-check-circle drive-detail__card-icon"></i>
              <h2 class="drive-detail__card-title">Eligibility Criteria</h2>
            </div>

            <div class="drive-detail__field">
              <div class="drive-detail__field-label">Minimum CGPA</div>
              <div class="drive-detail__cgpa-row">
                <span class="drive-detail__cgpa-value">{{ drive.min_cgpa ?? '—' }}</span>
                <span class="drive-detail__cgpa-max"> / 10.00</span>
              </div>
            </div>

            <div class="drive-detail__field">
              <div class="drive-detail__field-label">Eligible Branches</div>
              <div class="drive-detail__tags-row">
                <EligibilityTag
                  v-for="branch in eligibleBranches"
                  :key="branch"
                  :label="branch"
                />
              </div>
            </div>

            <div class="drive-detail__field">
              <div class="drive-detail__field-label">Batch / Year</div>
              <div class="drive-detail__field-value">{{ batchLabel }}</div>
            </div>

            <div v-if="selectionSteps.length" class="drive-detail__field">
              <div class="drive-detail__field-label">Selection Process</div>
              <div class="drive-detail__steps">
                <div
                  v-for="(step, idx) in selectionSteps"
                  :key="idx"
                  class="drive-detail__step-item"
                >
                  <span class="drive-detail__step-number">{{ idx + 1 }}</span>
                  <span class="drive-detail__step-text">{{ step }}</span>
                </div>
              </div>
            </div>

            <div class="drive-detail__divider"></div>

            <template v-if="isStudent">
              <AppButton
                v-if="drive.is_eligible && !drive.has_applied"
                variant="primary"
                class="drive-detail__apply-btn"
                @click="applyModalOpen = true"
              >Apply Now</AppButton>
              <div v-else-if="drive.has_applied" class="drive-detail__applied-text">
                <i class="bi bi-check-circle-fill"></i>
                Application Submitted
              </div>
            </template>

            <p class="drive-detail__disclaimer">
              By applying, you agree to the portal terms and conditions.
            </p>
          </div>

          <div class="card drive-detail__card">
            <div class="drive-detail__card-header">
              <i class="bi bi-buildings drive-detail__card-icon"></i>
              <h2 class="drive-detail__card-title">About {{ drive.company_name }}</h2>
            </div>
            <p class="drive-detail__company-desc">
              {{ truncate(drive.description || drive.company_description || '', 120) || 'No company description available.' }}
            </p>
            <AppButton variant="ghost" @click="navigateToCompany">View Company Profile →</AppButton>
          </div>
        </aside>
      </div>

      <div v-if="isAdmin && drive.applications?.length" class="card drive-detail__card drive-detail__apps-card">
        <div class="drive-detail__apps-header">
          <h2 class="drive-detail__card-title">Applications</h2>
          <span class="drive-detail__apps-count">{{ drive.applications.length }}</span>
        </div>
        <div class="drive-detail__table-wrap">
          <table>
            <thead>
              <tr>
                <th>Student Name</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in drive.applications" :key="app.id">
                <td>{{ app.student_name }}</td>
                <td><AppBadge :status="app.status" /></td>
                <td>
                  <button
                    class="drive-detail__action-btn"
                    title="View student"
                    @click="router.push('/admin/students/' + app.student_id)"
                  >
                    <i class="bi bi-eye"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <footer class="drive-detail__footer">
        <span>© 2023 University Placement Cell. All rights reserved.</span>
        <div class="drive-detail__footer-links">
          <span>Help Center</span>
          <span>Privacy Policy</span>
          <span>Guidelines</span>
        </div>
      </footer>
    </template>

    <AppModal
      :show="applyModalOpen"
      title="Apply for this Position"
      headerIcon="bi bi-briefcase-fill"
      confirmLabel="Confirm Application"
      confirmVariant="primary"
      warningMessage="You cannot withdraw your application once submitted."
      :loading="applying"
      @confirm="handleApply"
      @cancel="applyModalOpen = false"
    >
      <div class="drive-detail__apply-modal-body">
        <div class="drive-detail__apply-modal-title">{{ drive?.job_title }}</div>
        <div class="drive-detail__apply-modal-company">{{ drive?.company_name }}</div>
        <div class="drive-detail__apply-modal-meta">
          <span>{{ drive?.salary_package || 'Not disclosed' }}</span>
          <span>•</span>
          <span>Deadline: {{ formatDate(drive?.application_deadline, { style: 'short' }) }}</span>
        </div>
      </div>
    </AppModal>

    <AppModal
      :show="modalState.show && modalState.type === 'approve'"
      title="Approve Placement Drive"
      headerIcon="bi bi-briefcase-fill"
      confirmLabel="Approve Drive"
      confirmVariant="primary"
      warningMessage="Students will be able to see and apply to this drive immediately."
      :loading="actionLoading"
      @confirm="handleApproveConfirm"
      @cancel="closeModal"
    >
      <div class="drive-detail__modal-summary">
        <div class="drive-detail__modal-title">{{ modalState.drive?.job_title }}</div>
        <div class="drive-detail__modal-company">{{ modalState.drive?.company_name }}</div>
        <div class="drive-detail__modal-grid">
          <div>
            <div class="drive-detail__modal-label">Deadline</div>
            <div class="drive-detail__modal-value">
              {{ modalState.drive ? formatDate(modalState.drive.application_deadline, { style: 'short' }) : '' }}
            </div>
          </div>
          <div v-if="modalState.drive?.vacancy_count">
            <div class="drive-detail__modal-label">Vacancies</div>
            <div class="drive-detail__modal-value">{{ modalState.drive.vacancy_count }}</div>
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
      :loading="actionLoading"
      @confirm="handleRejectConfirm"
      @cancel="closeModal"
    >
      <div>
        <div class="drive-detail__modal-title">{{ modalState.drive?.job_title }}</div>
        <div class="drive-detail__modal-company">{{ modalState.drive?.company_name }}</div>
        <label class="drive-detail__modal-label drive-detail__modal-label--mt" for="reject-reason">
          Reason for rejection
        </label>
        <textarea
          id="reject-reason"
          class="drive-detail__reject-textarea"
          v-model="modalState.reason"
          rows="3"
          placeholder="Provide a reason..."
        ></textarea>
        <p v-if="modalState.rejectError" class="drive-detail__reject-error">{{ modalState.rejectError }}</p>
      </div>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { formatDate, truncate } from '@/utils/formatters'
import { DriveStatus } from '@/utils/constants'
import * as adminApi from '@/api/admin'
import * as studentApi from '@/api/student'
import * as companyApi from '@/api/company'

import AppButton from '@/components/common/AppButton.vue'
import AppBadge from '@/components/common/AppBadge.vue'
import AppSpinner from '@/components/common/AppSpinner.vue'
import AppEmptyState from '@/components/common/AppEmptyState.vue'
import AppModal from '@/components/common/AppModal.vue'
import EligibilityTag from '@/components/admin/EligibilityTag.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isAdmin = computed(() => authStore.isAdmin)
const isStudent = computed(() => authStore.isStudent)
const isCompany = computed(() => authStore.isCompany)

const drive = ref(null)
const loading = ref(false)
const actionLoading = ref(false)
const fetchError = ref('')
const feedbackMessage = ref('')
const feedbackType = ref('success')
const applyModalOpen = ref(false)
const applying = ref(false)

const driveId = computed(() => drive.value?.drive_id ?? drive.value?.id)

const modalState = reactive({
  show: false,
  type: null,
  drive: null,
  reason: '',
  rejectError: ''
})

let feedbackTimer = null

const showFeedback = (message, type = 'success') => {
  feedbackMessage.value = message
  feedbackType.value = type
  clearTimeout(feedbackTimer)
  feedbackTimer = setTimeout(() => { feedbackMessage.value = '' }, 3000)
}

const eligibleBranches = computed(() => {
  const raw = drive.value?.eligible_branches?.split(',').map(b => b.trim()).filter(Boolean) ?? []
  if (!raw.length || raw[0].toLowerCase() === 'all') return ['Any Branch']
  return raw
})

const batchLabel = computed(() => {
  const min = drive.value?.min_year
  const max = drive.value?.max_year
  if (min && max && min !== max) return `${min} - ${max}`
  if (max) return `${max} Graduating Batch`
  if (min) return `${min} Graduating Batch`
  return '—'
})

const parsedSkills = computed(() => {
  const criteria = drive.value?.other_criteria || ''
  const lines = criteria.split('\n').map(l => l.trim()).filter(Boolean)
  const skills = lines
    .filter(l => !l.match(/^\d+[\.\)]/))
    .map(l => l.replace(/^[-•*]\s*/, '').trim())
    .filter(l => l.length > 0 && l.length < 40)
  return skills.length ? skills : []
})

const selectionSteps = computed(() => {
  const criteria = drive.value?.other_criteria || ''
  const lines = criteria.split('\n').map(l => l.trim()).filter(Boolean)
  return lines
    .filter(l => l.match(/^\d+[\.\)]/))
    .map(l => l.replace(/^\d+[\.\)]\s*/, '').trim())
})

const loadDrive = async () => {
  loading.value = true
  fetchError.value = ''
  try {
    let response
    if (isAdmin.value) {
      response = await adminApi.getDrive(route.params.id)
    } else if (isStudent.value) {
      response = await studentApi.getDrive(route.params.id)
    } else {
      response = await companyApi.getDrive(route.params.id)
    }
    drive.value = response.data
  } catch (e) {
    fetchError.value = e.message || 'Failed to load drive.'
  } finally {
    loading.value = false
  }
}

const openModal = (type, d) => {
  modalState.type = type
  modalState.drive = d
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
  actionLoading.value = true
  try {
    await adminApi.approveDrive(modalState.drive.id)
    drive.value = { ...drive.value, status: DriveStatus.APPROVED }
    closeModal()
    showFeedback('Drive approved successfully.')
  } catch (e) {
    showFeedback(e.message || 'Failed to approve drive.', 'error')
  } finally {
    actionLoading.value = false
  }
}

const handleRejectConfirm = async () => {
  if (!modalState.reason.trim()) {
    modalState.rejectError = 'Rejection reason is required.'
    return
  }
  actionLoading.value = true
  try {
    await adminApi.rejectDrive(modalState.drive.id, { reason: modalState.reason })
    drive.value = { ...drive.value, status: 'rejected' }
    closeModal()
    showFeedback('Drive rejected.')
  } catch (e) {
    showFeedback(e.message || 'Failed to reject drive.', 'error')
  } finally {
    actionLoading.value = false
  }
}

const handleApply = async () => {
  applying.value = true
  try {
    await studentApi.applyToDrive(driveId.value)
    applyModalOpen.value = false
    drive.value = { ...drive.value, has_applied: true }
    showFeedback('Application submitted successfully!')
  } catch (e) {
    showFeedback(e.message || 'Failed to submit application.', 'error')
  } finally {
    applying.value = false
  }
}

const navigateToCompany = () => {
  const companyId = drive.value?.company_id
  if (isAdmin.value && companyId) {
    router.push('/admin/companies/' + companyId)
  } else if (isStudent.value && companyId) {
    router.push('/student/companies/' + companyId)
  } else if (isCompany.value) {
    router.push('/company/profile')
  }
}

onMounted(() => {
  loadDrive()
})
</script>

<style scoped>
.drive-detail {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.drive-detail__toast {
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

.drive-detail__toast--success {
  background-color: var(--color-success);
}

.drive-detail__toast--error {
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

/* ── Hero Banner ── */
.drive-hero {
  background-color: var(--color-gray-800);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  height: 220px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: var(--space-5);
}

.drive-hero__top {
  display: flex;
  align-items: flex-start;
}

.drive-hero__pills {
  display: flex;
  gap: var(--space-2);
}

.drive-hero__pill {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  border-radius: var(--border-radius-pill);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  padding-block: var(--space-1);
  padding-inline: var(--space-3);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

/* rgba exception: hero open state uses semi-transparent green for dark bg contrast */
.drive-hero__pill--open {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

/* rgba exception: hero type pill uses semi-transparent white for dark bg overlay */
.drive-hero__pill--type {
  background: rgba(255, 255, 255, 0.15);
  color: var(--color-white);
}

.drive-hero__pill--closed {
  background: var(--color-gray-700);
  color: var(--color-gray-300);
}

.drive-hero__bottom {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--space-4);
}

.drive-hero__identity {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.drive-hero__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-white);
  margin: 0;
  line-height: var(--line-height-tight);
}

.drive-hero__company {
  font-size: var(--font-size-sm);
  /* rgba exception: muted white text on dark hero background */
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.drive-hero__apply-slot {
  flex-shrink: 0;
}

/* rgba exception: already-applied pill on hero dark background */
.drive-hero__applied-pill {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  background: rgba(255, 255, 255, 0.15);
  color: var(--color-white);
  border-radius: var(--border-radius-pill);
  font-size: var(--font-size-sm);
  padding-block: var(--space-2);
  padding-inline: var(--space-4);
}

/* ── Admin Action Bar ── */
.drive-detail__admin-bar {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding-block: var(--space-3);
}

/* ── Stat Cards ── */
.drive-detail__stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
}

.drive-detail__stat-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.drive-detail__stat-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-1);
}

.drive-detail__stat-value {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.drive-detail__stat-icon {
  color: var(--color-primary);
  font-size: var(--font-size-lg);
  flex-shrink: 0;
}

/* ── Two-column content ── */
.drive-detail__content {
  display: flex;
  gap: var(--space-5);
  align-items: flex-start;
}

.drive-detail__left {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
  min-width: 0;
}

.drive-detail__right {
  width: 360px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  position: sticky;
  top: calc(var(--navbar-height) + var(--space-4));
  align-self: flex-start;
}

/* ── Card shared styles ── */
.drive-detail__card {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.drive-detail__card-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.drive-detail__card-icon {
  color: var(--color-primary);
  font-size: var(--font-size-lg);
}

.drive-detail__card-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.drive-detail__description {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: var(--line-height-base);
  margin: 0;
  white-space: pre-line;
}

.drive-detail__tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

/* ── Eligibility fields ── */
.drive-detail__field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.drive-detail__field-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-1);
}

.drive-detail__field-value {
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
}

.drive-detail__cgpa-row {
  display: flex;
  align-items: baseline;
}

.drive-detail__cgpa-value {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.drive-detail__cgpa-max {
  font-size: var(--font-size-base);
  color: var(--color-text-muted);
}

/* ── Selection steps ── */
.drive-detail__steps {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.drive-detail__step-item {
  display: flex;
  gap: var(--space-2);
  align-items: center;
}

.drive-detail__step-number {
  width: 22px;
  height: 22px;
  border-radius: var(--border-radius-pill);
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.drive-detail__step-text {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* ── Sidebar apply states ── */
.drive-detail__divider {
  border-top: var(--border-width) solid var(--color-border);
  margin-block: var(--space-4);
}

.drive-detail__apply-btn {
  width: 100%;
}

.drive-detail__applied-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-success);
}

.drive-detail__disclaimer {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  text-align: center;
  margin: 0;
  margin-top: var(--space-2);
}

/* ── About Company card ── */
.drive-detail__company-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-base);
  margin: 0;
}

/* ── Apply modal body ── */
.drive-detail__apply-modal-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.drive-detail__apply-modal-title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.drive-detail__apply-modal-company {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.drive-detail__apply-modal-meta {
  display: flex;
  gap: var(--space-2);
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  margin-top: var(--space-1);
}

/* ── Admin approve/reject modal ── */
.drive-detail__modal-summary {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.drive-detail__modal-title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.drive-detail__modal-company {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.drive-detail__modal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
  margin-top: var(--space-2);
}

.drive-detail__modal-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  font-weight: var(--font-weight-medium);
  margin-bottom: var(--space-1);
}

.drive-detail__modal-label--mt {
  display: block;
  margin-top: var(--space-4);
}

.drive-detail__modal-value {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.drive-detail__reject-textarea {
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

.drive-detail__reject-textarea:focus {
  border-color: var(--color-primary);
}

.drive-detail__reject-error {
  margin-top: var(--space-2);
  font-size: var(--font-size-xs);
  color: var(--color-danger);
}

/* ── Applications table ── */
.drive-detail__apps-card {
  margin-top: var(--space-4);
}

.drive-detail__apps-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.drive-detail__apps-count {
  display: inline-flex;
  align-items: center;
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  border-radius: var(--border-radius-pill);
  padding-block: var(--space-1);
  padding-inline: var(--space-3);
}

.drive-detail__table-wrap {
  overflow-x: auto;
}

.drive-detail__action-btn {
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

.drive-detail__action-btn:hover {
  background-color: var(--color-gray-100);
  color: var(--color-text-primary);
}

/* ── Page Footer ── */
.drive-detail__footer {
  border-top: var(--border-width) solid var(--color-border);
  padding-block: var(--space-4);
  margin-top: var(--space-8);
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.drive-detail__footer-links {
  display: flex;
  gap: var(--space-4);
}

/* ── Responsive ── */
@media (max-width: 991px) {
  .drive-detail__content {
    flex-direction: column;
  }

  .drive-detail__right {
    width: 100%;
    position: static;
  }

  .drive-detail__stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 575px) {
  .drive-detail__stats-grid {
    grid-template-columns: 1fr 1fr;
  }

  .drive-hero__bottom {
    flex-direction: column;
    align-items: flex-start;
  }

  .drive-detail__footer {
    flex-direction: column;
    gap: var(--space-3);
    align-items: flex-start;
  }
}
</style>
