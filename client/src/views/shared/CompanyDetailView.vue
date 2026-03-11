<template>
  <div class="company-detail">
    <Transition name="toast">
      <div
        v-if="feedbackMessage"
        class="company-detail__toast"
        :class="feedbackType === 'error' ? 'company-detail__toast--error' : 'company-detail__toast--success'"
      >
        <i :class="feedbackType === 'error' ? 'bi bi-x-circle-fill' : 'bi bi-check-circle-fill'"></i>
        {{ feedbackMessage }}
      </div>
    </Transition>

    <AppSpinner v-if="loading && !company" :fullPage="true" />

    <AppEmptyState
      v-else-if="fetchError"
      icon="bi bi-exclamation-circle"
      title="Failed to load company"
      :subtitle="fetchError"
      actionLabel="Retry"
      @action="loadCompany"
    />

    <template v-else-if="company">
      <button v-if="!isOwnProfile" class="company-detail__back" @click="router.go(-1)">
        <i class="bi bi-arrow-left"></i>
        Back to Companies
      </button>

      <div class="card company-detail__header-card">
        <div class="company-detail__header-inner">
          <img
            v-if="company.logo_filename"
            :src="apiBase + '/static/uploads/logos/' + company.logo_filename"
            :alt="company.company_name"
            class="company-detail__logo"
          />
          <AppAvatar v-else :name="company.company_name" size="lg" />

          <div class="company-detail__header-body">
            <div class="company-detail__name-row">
              <span class="company-detail__name">{{ company.company_name }}</span>
              <span
                v-if="company.approval_status === ApprovalStatus.APPROVED"
                class="company-detail__verified-pill"
              >
                <i class="bi bi-patch-check-fill"></i>
                VERIFIED
              </span>
            </div>

            <p v-if="company.description" class="company-detail__tagline">
              {{ truncate(company.description, 80) }}
            </p>

            <div class="company-detail__meta-row">
              <span v-if="company.industry" class="company-detail__meta-item">
                <i class="bi bi-buildings"></i>
                {{ company.industry }}
              </span>
              <span v-if="company.website" class="company-detail__meta-item">
                <i class="bi bi-globe"></i>
                <a :href="company.website" target="_blank" rel="noopener noreferrer" class="company-detail__website-link">
                  {{ company.website }}
                </a>
              </span>
              <span v-if="company.address" class="company-detail__meta-item">
                <i class="bi bi-geo-alt"></i>
                {{ company.address }}
              </span>
            </div>

            <p v-if="company.employee_count" class="company-detail__employees">
              <i class="bi bi-people"></i>
              {{ company.employee_count }} employees
            </p>
          </div>

          <div class="company-detail__header-actions">
            <template v-if="isAdmin">
              <template v-if="company.approval_status === ApprovalStatus.PENDING">
                <AppButton variant="primary" @click="openModal('approve', company)">Approve</AppButton>
                <AppButton variant="danger" @click="openModal('reject', company)">Reject</AppButton>
              </template>
              <template v-if="company.approval_status === ApprovalStatus.APPROVED && company.account_status === AccountStatus.ACTIVE">
                <AppButton variant="danger" @click="openModal('blacklist', company)">Blacklist</AppButton>
              </template>
              <template v-if="company.account_status === AccountStatus.BLACKLISTED">
                <AppButton variant="primary" @click="openModal('activate', company)">Activate</AppButton>
              </template>
            </template>

            <template v-else-if="isOwnProfile">
              <AppButton variant="outline" @click="router.push('/company/profile/edit')">Edit Profile</AppButton>
            </template>
          </div>
        </div>
      </div>

      <div class="company-detail__tab-nav">
        <button
          class="company-detail__tab-item"
          :class="{ 'company-detail__tab-item--active': activeTab === 'overview' }"
          @click="activeTab = 'overview'"
        >Overview</button>
        <button
          class="company-detail__tab-item"
          :class="{ 'company-detail__tab-item--active': activeTab === 'drives' }"
          @click="activeTab = 'drives'"
        >Active Drives ({{ activeDriveCount }})</button>
        <button
          class="company-detail__tab-item"
          :class="{ 'company-detail__tab-item--active': activeTab === 'placements' }"
          @click="activeTab = 'placements'"
        >Past Placements</button>
        <button
          class="company-detail__tab-item"
          :class="{ 'company-detail__tab-item--active': activeTab === 'feedback' }"
          @click="activeTab = 'feedback'"
        >Feedback</button>
      </div>

      <div v-if="activeTab === 'overview'" class="company-detail__overview">
        <div class="card company-detail__about-card">
          <h2 class="company-detail__card-title">About the Company</h2>
          <p class="company-detail__description">{{ company.description || 'No description provided.' }}</p>

          <div
            v-if="company.founded_on || company.revenue"
            class="company-detail__about-stats"
          >
            <div v-if="company.founded_on" class="company-detail__about-stat">
              <div class="company-detail__about-stat-label">FOUNDED</div>
              <div class="company-detail__about-stat-value">{{ formatDate(company.founded_on, { style: 'short' }) }}</div>
            </div>
            <div v-if="company.revenue" class="company-detail__about-stat">
              <div class="company-detail__about-stat-label">REVENUE</div>
              <div class="company-detail__about-stat-value">{{ company.revenue }}</div>
            </div>
          </div>
        </div>

        <div class="company-detail__right-col">
          <div class="card company-detail__location-card">
            <div class="company-detail__map-placeholder">
              <i class="bi bi-geo-alt-fill company-detail__map-icon"></i>
            </div>
            <div class="company-detail__address-block">
              <div class="company-detail__address-title">Main Headquarters</div>
              <div class="company-detail__address-text">{{ company.address || 'Address not provided' }}</div>
            </div>
          </div>

          <div class="card company-detail__portal-stats-card">
            <div class="company-detail__portal-stats-label">PORTAL STATS</div>
            <div class="company-detail__portal-row">
              <div class="company-detail__portal-left">
                <i class="bi bi-people-fill company-detail__portal-icon company-detail__portal-icon--primary"></i>
                <span class="company-detail__portal-name">Placed Students</span>
              </div>
              <span class="company-detail__portal-value">{{ company.placed_students_count ?? '—' }}</span>
            </div>
            <div class="company-detail__portal-row">
              <div class="company-detail__portal-left">
                <i class="bi bi-star-fill company-detail__portal-icon company-detail__portal-icon--warning"></i>
                <span class="company-detail__portal-name">Avg. Package</span>
              </div>
              <span class="company-detail__portal-value">{{ company.avg_package ?? '—' }}</span>
            </div>
            <div class="company-detail__portal-row company-detail__portal-row--last">
              <div class="company-detail__portal-left">
                <i class="bi bi-briefcase-fill company-detail__portal-icon company-detail__portal-icon--success"></i>
                <span class="company-detail__portal-name">Total Drives</span>
              </div>
              <span class="company-detail__portal-value">{{ allDrives.length }}</span>
            </div>
          </div>

          <div class="card company-detail__contact-card">
            <h2 class="company-detail__card-title">Contact Person</h2>
            <div class="company-detail__contact-row">
              <AppAvatar :name="company.hr_name || ''" size="sm" />
              <div class="company-detail__contact-info">
                <div class="company-detail__contact-name">{{ company.hr_name || '—' }}</div>
                <div class="company-detail__contact-title">Lead Talent Acquisition</div>
              </div>
            </div>
            <AppButton
              variant="outline"
              iconLeft="bi bi-envelope"
              class="company-detail__message-btn"
              @click="handleMessageHR"
            >Message {{ company.hr_name }}</AppButton>
          </div>
        </div>
      </div>

      <template v-else-if="activeTab === 'drives'">
        <AppEmptyState
          v-if="!activeDrives.length"
          icon="bi bi-briefcase"
          title="No active drives"
          subtitle="There are no open recruitment drives for this company right now."
        />
        <div v-else class="company-detail__drives-list">
          <div
            v-for="drive in activeDrives"
            :key="drive.id"
            class="card company-detail__drive-card"
          >
            <div class="company-detail__drive-header">
              <span class="company-detail__drive-title">{{ drive.job_title }}</span>
              <span class="company-detail__open-pill">OPEN</span>
            </div>
            <div class="company-detail__drive-meta">
              <span class="company-detail__drive-meta-item">
                <i class="bi bi-briefcase"></i>
                {{ drive.job_type || '—' }}
              </span>
              <span class="company-detail__drive-meta-item">
                <i class="bi bi-currency-rupee"></i>
                {{ drive.salary_package || 'Not disclosed' }}
              </span>
            </div>
            <div class="company-detail__drive-footer">
              <span class="company-detail__drive-deadline">
                Deadline: {{ formatDate(drive.application_deadline, { style: 'short' }) || '—' }}
              </span>
              <div class="company-detail__drive-actions">
                <AppButton variant="ghost" size="sm" @click="navigateToDrive(drive.id)">Details</AppButton>
                <AppButton
                  v-if="isStudent"
                  variant="primary"
                  size="sm"
                  @click="navigateToDrive(drive.id)"
                >Apply Now</AppButton>
              </div>
            </div>
          </div>
        </div>
      </template>

      <template v-else-if="activeTab === 'placements'">
        <AppEmptyState
          icon="bi bi-clock-history"
          title="Past placement data coming soon"
          subtitle="Historical placement records will appear here"
        />
      </template>

      <template v-else-if="activeTab === 'feedback'">
        <AppEmptyState
          icon="bi bi-chat-left-text"
          title="Feedback not available"
          subtitle="Student feedback for this company will appear here"
        />
      </template>
    </template>

    <AppModal
      :show="modalState.show && modalState.type === 'approve'"
      title="Approve Company Registration"
      headerIcon="bi bi-shield-check"
      confirmLabel="Confirm Approval"
      confirmVariant="primary"
      warningMessage="This company will be notified and can start posting placement drives immediately."
      :loading="adminStore.actionLoading"
      @confirm="handleApproveConfirm"
      @cancel="closeModal"
    >
      <div class="company-detail__modal-summary">
        <div class="company-detail__modal-grid">
          <div>
            <div class="company-detail__modal-label">Company Name</div>
            <div class="company-detail__modal-value">{{ modalState.company?.company_name }}</div>
          </div>
          <div>
            <div class="company-detail__modal-label">Industry</div>
            <div class="company-detail__modal-value">{{ modalState.company?.industry || '—' }}</div>
          </div>
        </div>
        <div class="company-detail__modal-hr">
          <AppAvatar :name="modalState.company?.hr_name || ''" size="sm" />
          <div>
            <div class="company-detail__modal-value">{{ modalState.company?.hr_name }}</div>
            <div class="company-detail__modal-label">{{ modalState.company?.email }}</div>
          </div>
        </div>
      </div>
    </AppModal>

    <AppModal
      :show="modalState.show && modalState.type === 'reject'"
      title="Reject Company Registration"
      headerIcon="bi bi-shield-x"
      confirmLabel="Confirm Rejection"
      confirmVariant="danger"
      warningMessage="The company will be notified of the rejection."
      :loading="adminStore.actionLoading"
      @confirm="handleRejectConfirm"
      @cancel="closeModal"
    >
      <div>
        <label class="company-detail__modal-label" for="reject-reason">Reason for rejection</label>
        <textarea
          id="reject-reason"
          class="company-detail__reject-textarea"
          v-model="modalState.reason"
          rows="3"
          placeholder="Provide a reason..."
        ></textarea>
        <p v-if="rejectError" class="company-detail__reject-error">{{ rejectError }}</p>
      </div>
    </AppModal>

    <AppModal
      :show="modalState.show && modalState.type === 'blacklist'"
      title="Blacklist Company"
      headerIcon="bi bi-slash-circle"
      confirmLabel="Confirm Blacklist"
      confirmVariant="danger"
      warningMessage="This company will be prevented from creating new drives. Existing drives remain unchanged."
      :loading="adminStore.actionLoading"
      @confirm="handleBlacklistConfirm"
      @cancel="closeModal"
    >
      <div class="company-detail__modal-summary">
        <div class="company-detail__modal-value">{{ modalState.company?.company_name }}</div>
        <div class="company-detail__modal-label">
          Current status:
          <AppBadge v-if="modalState.company" :status="modalState.company.approval_status" />
        </div>
      </div>
    </AppModal>

    <AppModal
      :show="modalState.show && modalState.type === 'activate'"
      title="Activate Company"
      headerIcon="bi bi-building-check"
      confirmLabel="Confirm Activation"
      confirmVariant="primary"
      warningMessage="This company will regain full access and can create new placement drives."
      :loading="adminStore.actionLoading"
      @confirm="handleActivateConfirm"
      @cancel="closeModal"
    >
      <div class="company-detail__modal-summary">
        <div class="company-detail__modal-grid">
          <div>
            <div class="company-detail__modal-label">Company Name</div>
            <div class="company-detail__modal-value">{{ modalState.company?.company_name }}</div>
          </div>
          <div>
            <div class="company-detail__modal-label">Industry</div>
            <div class="company-detail__modal-value">{{ modalState.company?.industry || '—' }}</div>
          </div>
        </div>
        <div class="company-detail__modal-hr">
          <AppAvatar :name="modalState.company?.hr_name || ''" size="sm" />
          <div>
            <div class="company-detail__modal-value">{{ modalState.company?.hr_name }}</div>
            <div class="company-detail__modal-label">{{ modalState.company?.email }}</div>
          </div>
        </div>
      </div>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAdminStore } from '@/stores/admin'
import { formatDate, truncate } from '@/utils/formatters'
import { ApprovalStatus, AccountStatus, DriveStatus } from '@/utils/constants'
import * as adminApi from '@/api/admin'
import * as companyApi from '@/api/company'
import * as studentApi from '@/api/student'

import AppButton from '@/components/common/AppButton.vue'
import AppAvatar from '@/components/common/AppAvatar.vue'
import AppBadge from '@/components/common/AppBadge.vue'
import AppSpinner from '@/components/common/AppSpinner.vue'
import AppEmptyState from '@/components/common/AppEmptyState.vue'
import AppModal from '@/components/common/AppModal.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const adminStore = useAdminStore()
const apiBase = import.meta.env.VITE_API_BASE_URL || ''

const isAdmin = computed(() => authStore.isAdmin)
const isStudent = computed(() => authStore.isStudent)
const isCompany = computed(() => authStore.isCompany)
const isOwnProfile = computed(() => isCompany.value)

const company = ref(null)
const drives = ref([])
const loading = ref(false)
const fetchError = ref('')
const activeTab = ref('overview')
const feedbackMessage = ref('')
const feedbackType = ref('success')
const rejectError = ref('')

const modalState = reactive({
  show: false,
  type: null,
  company: null,
  reason: ''
})

let feedbackTimer = null

const allDrives = computed(() => isOwnProfile.value ? drives.value : (company.value?.drives || []))
const activeDrives = computed(() => allDrives.value.filter(d => d.status === DriveStatus.APPROVED))
const activeDriveCount = computed(() => activeDrives.value.length)

const hrContactIsEmail = computed(() => company.value?.hr_contact?.includes('@') ?? false)

const showFeedback = (message, type = 'success') => {
  feedbackMessage.value = message
  feedbackType.value = type
  clearTimeout(feedbackTimer)
  feedbackTimer = setTimeout(() => { feedbackMessage.value = '' }, 3000)
}

const loadCompany = async () => {
  loading.value = true
  fetchError.value = ''
  try {
    if (isOwnProfile.value) {
      const [profileRes, drivesRes] = await Promise.all([
        companyApi.getProfile(),
        companyApi.getDrives()
      ])
      company.value = profileRes.data
      drives.value = drivesRes.data || []
    } else if (isStudent.value) {
      const response = await studentApi.getCompany(route.params.id)
      company.value = response.data
    } else {
      const response = await adminApi.getCompany(route.params.id)
      company.value = response.data
    }
  } catch (e) {
    fetchError.value = e.message || 'Failed to load company.'
  } finally {
    loading.value = false
  }
}

const openModal = (type, c) => {
  modalState.type = type
  modalState.company = c
  modalState.reason = ''
  rejectError.value = ''
  modalState.show = true
}

const closeModal = () => {
  modalState.show = false
  setTimeout(() => {
    modalState.type = null
    modalState.company = null
    modalState.reason = ''
    rejectError.value = ''
  }, 300)
}

const handleApproveConfirm = async () => {
  try {
    await adminStore.approveCompany(modalState.company.id)
    company.value = { ...company.value, approval_status: ApprovalStatus.APPROVED }
    closeModal()
    showFeedback('Company approved successfully.')
  } catch {
    showFeedback(adminStore.error || 'Failed to approve company.', 'error')
  }
}

const handleRejectConfirm = async () => {
  if (!modalState.reason.trim()) {
    rejectError.value = 'Please provide a reason for rejection.'
    return
  }
  try {
    await adminStore.rejectCompany(modalState.company.id, modalState.reason)
    company.value = { ...company.value, approval_status: ApprovalStatus.REJECTED }
    closeModal()
    showFeedback('Company rejected.')
  } catch {
    showFeedback(adminStore.error || 'Failed to reject company.', 'error')
  }
}

const handleBlacklistConfirm = async () => {
  try {
    await adminStore.blacklistCompany(modalState.company.id)
    company.value = { ...company.value, account_status: AccountStatus.BLACKLISTED }
    closeModal()
    showFeedback('Company blacklisted.')
  } catch {
    showFeedback(adminStore.error || 'Failed to blacklist company.', 'error')
  }
}

const handleActivateConfirm = async () => {
  try {
    await adminStore.activateCompany(modalState.company.id)
    company.value = { ...company.value, account_status: AccountStatus.ACTIVE }
    closeModal()
    showFeedback('Company activated successfully.')
  } catch {
    showFeedback(adminStore.error || 'Failed to activate company.', 'error')
  }
}

const handleMessageHR = () => {
  if (hrContactIsEmail.value) {
    window.location.href = 'mailto:' + company.value.hr_contact
  } else {
    console.log('Message HR: not implemented')
  }
}

const navigateToDrive = (driveId) => {
  if (isAdmin.value) router.push('/admin/drives/' + driveId)
  else if (isStudent.value) router.push('/student/drives/' + driveId)
  else router.push('/company/drives/' + driveId)
}

onMounted(() => {
  loadCompany()
})
</script>

<style scoped>
.company-detail {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.company-detail__toast {
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

.company-detail__toast--success {
  background-color: var(--color-success);
}

.company-detail__toast--error {
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

.company-detail__back {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  background: none;
  border: none;
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-muted);
  padding: 0;
  transition: color var(--transition-fast);
}

.company-detail__back:hover {
  color: var(--color-text-primary);
}

.company-detail__header-card {
  padding: var(--card-padding);
}

.company-detail__header-inner {
  display: flex;
  gap: var(--space-5);
  align-items: flex-start;
}

.company-detail__logo {
  flex-shrink: 0;
  width: 80px;
  height: 80px;
  border-radius: var(--border-radius-md);
  object-fit: cover;
  border: var(--border-width) solid var(--border-color);
}

.company-detail__header-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  min-width: 0;
}

.company-detail__name-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.company-detail__name {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

/* rgba exception: verified pill uses semi-transparent primary blue background */
.company-detail__verified-pill {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  background: rgba(59, 130, 246, 0.1);
  color: var(--color-primary);
  border-radius: var(--border-radius-pill);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  padding-block: var(--space-1);
  padding-inline: var(--space-3);
  letter-spacing: 0.04em;
}

.company-detail__tagline {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin: 0;
}

.company-detail__meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  align-items: center;
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

.company-detail__meta-item {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.company-detail__website-link {
  color: var(--color-primary);
  text-decoration: none;
}

.company-detail__website-link:hover {
  text-decoration: underline;
}

.company-detail__employees {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin: 0;
}

.company-detail__header-actions {
  flex-shrink: 0;
  display: flex;
  gap: var(--space-3);
  align-items: center;
  flex-wrap: wrap;
}

.company-detail__tab-nav {
  display: flex;
  border-bottom: var(--border-width) solid var(--border-color);
  margin-bottom: 0;
}

.company-detail__tab-item {
  padding: var(--space-3) var(--space-4);
  cursor: pointer;
  border: none;
  border-bottom: 2px solid transparent;
  background: none;
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-normal);
  transition: all var(--transition-fast);
  margin-bottom: -1px;
}

.company-detail__tab-item:hover {
  color: var(--color-text-primary);
}

.company-detail__tab-item--active {
  border-bottom-color: var(--color-primary);
  color: var(--color-primary);
  font-weight: var(--font-weight-semibold);
}

.company-detail__overview {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--space-5);
  align-items: flex-start;
}

.company-detail__about-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.company-detail__card-title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.company-detail__description {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: var(--line-height-base);
  margin: 0;
  white-space: pre-line;
}

.company-detail__about-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
  padding-top: var(--space-4);
  border-top: var(--border-width) solid var(--border-color);
}

.company-detail__about-stat-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-1);
}

.company-detail__about-stat-value {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.company-detail__right-col {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.company-detail__location-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.company-detail__map-placeholder {
  height: 160px;
  background-color: var(--color-gray-100);
  border-radius: var(--border-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.company-detail__map-icon {
  font-size: var(--font-size-3xl);
  color: var(--color-text-muted);
}

.company-detail__address-block {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.company-detail__address-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.company-detail__address-text {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.company-detail__portal-stats-card {
  display: flex;
  flex-direction: column;
}

.company-detail__portal-stats-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-3);
}

.company-detail__portal-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) 0;
  border-bottom: var(--border-width) solid var(--border-color);
}

.company-detail__portal-row--last {
  border-bottom: none;
}

.company-detail__portal-left {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.company-detail__portal-icon {
  font-size: var(--font-size-base);
}

.company-detail__portal-icon--primary {
  color: var(--color-primary);
}

.company-detail__portal-icon--warning {
  color: var(--color-warning);
}

.company-detail__portal-icon--success {
  color: var(--color-success);
}

.company-detail__portal-name {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.company-detail__portal-value {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.company-detail__contact-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.company-detail__contact-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.company-detail__contact-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.company-detail__contact-name {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.company-detail__contact-title {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.company-detail__message-btn {
  width: 100%;
}

.company-detail__drives-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.company-detail__drive-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.company-detail__drive-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
}

.company-detail__drive-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

/* rgba exception: OPEN pill uses semi-transparent green on card background */
.company-detail__open-pill {
  display: inline-flex;
  align-items: center;
  background: rgba(34, 197, 94, 0.1);
  color: rgba(34, 197, 94, 1);
  border-radius: var(--border-radius-pill);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  padding-block: var(--space-1);
  padding-inline: var(--space-3);
  flex-shrink: 0;
}

.company-detail__drive-meta {
  display: flex;
  gap: var(--space-4);
  flex-wrap: wrap;
}

.company-detail__drive-meta-item {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.company-detail__drive-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.company-detail__drive-deadline {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.company-detail__drive-actions {
  display: flex;
  gap: var(--space-2);
  align-items: center;
}

.company-detail__modal-summary {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.company-detail__modal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.company-detail__modal-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  font-weight: var(--font-weight-medium);
  margin-bottom: var(--space-1);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.company-detail__modal-value {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.company-detail__modal-hr {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.company-detail__reject-textarea {
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

.company-detail__reject-textarea:focus {
  border-color: var(--color-primary);
}

.company-detail__reject-error {
  margin-top: var(--space-2);
  font-size: var(--font-size-xs);
  color: var(--color-danger);
}

@media (max-width: 991px) {
  .company-detail__overview {
    grid-template-columns: 1fr;
  }

  .company-detail__right-col {
    order: -1;
  }
}

@media (max-width: 575px) {
  .company-detail__header-inner {
    flex-wrap: wrap;
  }

  .company-detail__header-actions {
    width: 100%;
  }

  .company-detail__tab-item {
    padding: var(--space-2) var(--space-3);
    font-size: var(--font-size-xs);
  }
}
</style>
