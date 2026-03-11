<template>
  <div class="student-profile">
    <Transition name="toast">
      <div
        v-if="feedbackMessage"
        class="student-profile__toast"
        :class="feedbackType === 'error' ? 'student-profile__toast--error' : 'student-profile__toast--success'"
      >
        <i :class="feedbackType === 'error' ? 'bi bi-x-circle-fill' : 'bi bi-check-circle-fill'"></i>
        {{ feedbackMessage }}
      </div>
    </Transition>

    <AppSpinner v-if="loading && !student" :fullPage="true" />

    <AppEmptyState
      v-else-if="fetchError"
      icon="bi bi-exclamation-circle"
      title="Failed to load student profile"
      :subtitle="fetchError"
      actionLabel="Retry"
      @action="loadProfile"
    />

    <template v-else-if="student">
      <header class="student-profile__header">
        <div class="student-profile__identity">
          <img
            v-if="student.profile_picture"
            :src="student.profile_picture"
            :alt="displayName"
            class="student-profile__avatar-img"
          />
          <AppAvatar v-else :name="displayName" size="lg" />
          <div class="student-profile__identity-info">
            <h1 class="student-profile__name">{{ displayName }}</h1>
            <div class="student-profile__meta">
              <span class="student-profile__branch">{{ student.branch }}</span>
            </div>
          </div>
        </div>

        <div v-if="isAdmin || isOwnProfile" class="student-profile__header-actions">
          <template v-if="isAdmin">
            <AppButton
              v-if="student.account_status === AccountStatus.ACTIVE"
              variant="danger"
              @click="openModal('blacklist', student)"
            >Blacklist</AppButton>
            <AppButton
              v-if="student.account_status === AccountStatus.BLACKLISTED"
              variant="primary"
              @click="openModal('activate', student)"
            >Activate</AppButton>
          </template>
          <template v-if="isOwnProfile">
            <AppButton variant="outline" @click="handleEditProfile">Edit Profile</AppButton>
            <AppButton
              variant="primary"
              @click="router.push('/student/drives')"
            >Apply for Jobs</AppButton>
          </template>
        </div>
      </header>

      <div class="student-profile__body">
        <div class="student-profile__left">
          <div class="card student-profile__card">
            <h2 class="student-profile__card-title">Personal Details</h2>
            <div class="student-profile__fields-grid">
              <div class="student-profile__field">
                <div class="student-profile__field-label">Email Address</div>
                <div class="student-profile__field-value">{{ student.email || '—' }}</div>
              </div>
              <div class="student-profile__field">
                <div class="student-profile__field-label">Phone Number</div>
                <div class="student-profile__field-value">{{ student.phone || '—' }}</div>
              </div>
            </div>

            <template v-if="isAdmin || isOwnProfile">
              <div class="student-profile__fields-grid student-profile__fields-grid--mt">
                <div class="student-profile__field">
                  <div class="student-profile__field-label">Date of Birth</div>
                  <div class="student-profile__field-value">{{ student.date_of_birth || '—' }}</div>
                </div>
                <div class="student-profile__field">
                  <div class="student-profile__field-label">Gender</div>
                  <div class="student-profile__field-value">{{ student.gender || '—' }}</div>
                </div>
                <div class="student-profile__field">
                  <div class="student-profile__field-label">LinkedIn</div>
                  <div class="student-profile__field-value">{{ student.linkedin_url || '—' }}</div>
                </div>
                <div class="student-profile__field">
                  <div class="student-profile__field-label">GitHub</div>
                  <div class="student-profile__field-value">{{ student.github_url || '—' }}</div>
                </div>
              </div>
              <div class="student-profile__field student-profile__field--full">
                <div class="student-profile__field-label">Address</div>
                <div class="student-profile__field-value">{{ student.address || '—' }}</div>
              </div>
            </template>
          </div>

          <div class="card student-profile__card">
            <h2 class="student-profile__card-title">Academic Summary</h2>
            <div class="student-profile__fields-grid">
              <div class="student-profile__field">
                <div class="student-profile__field-label">University</div>
                <div class="student-profile__field-value">{{ student.university || 'Not specified' }}</div>
              </div>
              <div class="student-profile__field">
                <div class="student-profile__field-label">Current CGPA</div>
                <div class="student-profile__cgpa">
                  <span class="student-profile__cgpa-value">{{ formatCGPA(student.cgpa) }}</span>
                  <span class="student-profile__cgpa-max">&nbsp;/ 10.0</span>
                </div>
              </div>
              <div class="student-profile__field">
                <div class="student-profile__field-label">Degree Program</div>
                <div class="student-profile__field-value">{{ student.degree_program || student.branch || '—' }}</div>
              </div>
              <div class="student-profile__field">
                <div class="student-profile__field-label">Graduation Year</div>
                <div class="student-profile__field-value">{{ student.year || '—' }}</div>
              </div>
            </div>
          </div>

          <div v-if="isAdmin" class="card student-profile__card">
            <h2 class="student-profile__card-title">Application History</h2>
            <AppEmptyState
              v-if="!student.applications || !student.applications.length"
              icon="bi bi-file-earmark-text"
              title="No applications yet"
              subtitle="This student has not applied to any placement drives."
            />
            <div v-else class="student-profile__table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Drive Title</th>
                    <th>Company</th>
                    <th>Status</th>
                    <th>Applied On</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="app in student.applications" :key="app.id">
                    <td>{{ app.drive_title }}</td>
                    <td>{{ app.company_name }}</td>
                    <td><AppBadge :status="app.status" /></td>
                    <td>{{ formatDate(app.applied_at, { style: 'short' }) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="student-profile__right">
          <div class="card student-profile__card">
            <h2 class="student-profile__card-title">Resume &amp; Documents</h2>

            <div v-if="student.resume_filename" class="student-profile__resume-row">
              <div class="student-profile__resume-icon">
                <i class="bi bi-file-pdf"></i>
              </div>
              <div class="student-profile__resume-info">
                <span class="student-profile__resume-name">{{ truncate(student.resume_filename, 24) }}</span>
                <span class="student-profile__resume-meta">Updated recently</span>
              </div>
              <button class="student-profile__resume-download" @click="handleDownloadResume" title="Download resume">
                <i class="bi bi-download"></i>
              </button>
            </div>
            <AppEmptyState
              v-else
              icon="bi bi-file-earmark"
              title="No resume uploaded"
              subtitle=""
            />

            <template v-if="isOwnProfile">
              <div class="student-profile__resume-actions">
                <input
                  ref="fileInputRef"
                  type="file"
                  accept=".pdf,.docx"
                  class="student-profile__file-input"
                  @change="handleResumeUpload"
                />
                <AppButton
                  variant="outline"
                  :loading="resumeUploading"
                  @click="fileInputRef.click()"
                  class="student-profile__resume-btn"
                >Update Resume</AppButton>
                <p class="student-profile__resume-hint">PDF format, max 5MB</p>
              </div>
            </template>
          </div>

          <div class="card student-profile__card">
            <div class="student-profile__placement-label">Placement Status</div>
            <div class="student-profile__placement-row">
              <span class="student-profile__placement-key">Eligibility</span>
              <span
                class="student-profile__placement-eligible"
                :class="student.account_status === AccountStatus.ACTIVE
                  ? 'student-profile__placement-eligible--yes'
                  : 'student-profile__placement-eligible--no'"
              >
                {{ student.account_status === AccountStatus.ACTIVE ? 'Eligible' : 'Ineligible' }}
              </span>
            </div>
            <div class="student-profile__placement-row">
              <span class="student-profile__placement-key">Profile Completion</span>
              <span class="student-profile__placement-pct">{{ completionPct }}%</span>
            </div>
            <div class="student-profile__progress-track">
              <div
                class="student-profile__progress-track__fill"
                :style="{ width: completionPct + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <AppModal
      :show="modalState.show && modalState.type === 'blacklist'"
      title="Blacklist Student"
      headerIcon="bi bi-person-slash"
      confirmLabel="Confirm Blacklist"
      confirmVariant="danger"
      warningMessage="This student will be unable to apply for any placement drives."
      :loading="actionLoading"
      @confirm="handleBlacklistConfirm"
      @cancel="closeModal"
    >
      <div class="student-profile__modal-summary">
        <div class="student-profile__modal-row">
          <AppAvatar :name="displayName" size="sm" />
          <div>
            <div class="student-profile__modal-name">{{ displayName }}</div>
            <div class="student-profile__modal-meta">{{ student?.branch }}</div>
          </div>
          <div class="student-profile__modal-cgpa">
            CGPA <span>{{ formatCGPA(student?.cgpa) }}</span>
          </div>
        </div>
      </div>
    </AppModal>

    <AppModal
      :show="modalState.show && modalState.type === 'activate'"
      title="Activate Student"
      headerIcon="bi bi-person-check"
      confirmLabel="Confirm Activation"
      confirmVariant="primary"
      warningMessage="This student will regain access to apply for placement drives."
      :loading="actionLoading"
      @confirm="handleActivateConfirm"
      @cancel="closeModal"
    >
      <div class="student-profile__modal-summary">
        <div class="student-profile__modal-row">
          <AppAvatar :name="displayName" size="sm" />
          <div>
            <div class="student-profile__modal-name">{{ displayName }}</div>
            <div class="student-profile__modal-meta">{{ student?.branch }}</div>
          </div>
          <div class="student-profile__modal-cgpa">
            CGPA <span>{{ formatCGPA(student?.cgpa) }}</span>
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
import { formatDate, formatCGPA, truncate } from '@/utils/formatters'
import { AccountStatus } from '@/utils/constants'
import * as adminApi from '@/api/admin'
import * as studentApi from '@/api/student'
import * as companyApi from '@/api/company'

import AppAvatar from '@/components/common/AppAvatar.vue'
import AppBadge from '@/components/common/AppBadge.vue'
import AppButton from '@/components/common/AppButton.vue'
import AppSpinner from '@/components/common/AppSpinner.vue'
import AppEmptyState from '@/components/common/AppEmptyState.vue'
import AppModal from '@/components/common/AppModal.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isAdmin = computed(() => authStore.isAdmin)
const isStudent = computed(() => authStore.isStudent)
const isCompany = computed(() => authStore.isCompany)

const student = ref(null)
const loading = ref(false)
const actionLoading = ref(false)
const fetchError = ref('')
const resumeUploading = ref(false)
const feedbackMessage = ref('')
const feedbackType = ref('success')
const fileInputRef = ref(null)

const isOwnProfile = computed(() =>
  isStudent.value && !route.params.id
)

const displayName = computed(() =>
  student.value?.full_name ?? student.value?.name ?? ''
)

const completionPct = computed(() => {
  if (!student.value) return 0
  const s = student.value
  let pts = 0
  if (s.full_name || s.name) pts += 15
  if (s.email) pts += 15
  if (s.phone) pts += 10
  if (s.branch) pts += 10
  if (s.cgpa) pts += 10
  if (s.year) pts += 10
  if (s.resume_filename) pts += 20
  if (s.address) pts += 10
  return Math.min(pts, 100)
})

const modalState = reactive({
  show: false,
  type: null,
  student: null
})

let feedbackTimer = null

const showFeedback = (message, type = 'success') => {
  feedbackMessage.value = message
  feedbackType.value = type
  clearTimeout(feedbackTimer)
  feedbackTimer = setTimeout(() => { feedbackMessage.value = '' }, 3000)
}

const loadProfile = async () => {
  loading.value = true
  fetchError.value = ''
  try {
    if (isAdmin.value) {
      const response = await adminApi.getStudent(route.params.id)
      student.value = response.data
    } else if (isCompany.value) {
      const response = await companyApi.getStudent(route.params.id)
      student.value = response.data
    } else {
      const response = await studentApi.getProfile()
      student.value = response.data
    }
  } catch (e) {
    fetchError.value = e.message || 'Failed to load student profile.'
  } finally {
    loading.value = false
  }
}

const openModal = (type, s) => {
  modalState.type = type
  modalState.student = s
  modalState.show = true
}

const closeModal = () => {
  modalState.show = false
  setTimeout(() => {
    modalState.type = null
    modalState.student = null
  }, 300)
}

const handleBlacklistConfirm = async () => {
  try {
    await adminApi.blacklistStudent(modalState.student.id)
    student.value = { ...student.value, account_status: AccountStatus.BLACKLISTED }
    closeModal()
    showFeedback('Student blacklisted successfully.')
  } catch (e) {
    showFeedback(e.message || 'Failed to blacklist student.', 'error')
  } finally {
    actionLoading.value = false
  }
}

const handleActivateConfirm = async () => {
  try {
    await adminApi.activateStudent(modalState.student.id)
    student.value = { ...student.value, account_status: AccountStatus.ACTIVE }
    closeModal()
    showFeedback('Student activated successfully.')
  } catch (e) {
    showFeedback(e.message || 'Failed to activate student.', 'error')
  } finally {
    actionLoading.value = false
  }
}

const handleEditProfile = () => {
  if (isOwnProfile.value) {
    router.push('/student/profile/edit')
  }
}

const handleDownloadResume = async () => {
  if (!student.value?.resume_filename) return
  try {
    await studentApi.downloadResume(student.value.resume_filename)
  } catch (e) {
    showFeedback('Failed to download resume.', 'error')
  }
}

const handleResumeUpload = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  resumeUploading.value = true
  try {
    await studentApi.uploadResume(file)
    student.value = { ...student.value, resume_filename: file.name }
    showFeedback('Resume updated successfully.')
  } catch (e) {
    showFeedback(e.message || 'Failed to upload resume.', 'error')
  } finally {
    resumeUploading.value = false
    event.target.value = ''
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.student-profile {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.student-profile__toast {
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

.student-profile__toast--success {
  background-color: var(--color-success);
}

.student-profile__toast--error {
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

.student-profile__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: var(--space-4);
}

.student-profile__identity {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.student-profile__avatar-img {
  width: var(--space-12);
  height: var(--space-12);
  border-radius: var(--border-radius-pill);
  object-fit: cover;
  flex-shrink: 0;
}

.student-profile__identity-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.student-profile__name {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
  line-height: var(--line-height-tight);
}

.student-profile__meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.student-profile__roll-badge {
  display: inline-flex;
  align-items: center;
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  border-radius: var(--border-radius-pill);
  padding-block: var(--space-1);
  padding-inline: var(--space-3);
  white-space: nowrap;
}

.student-profile__meta-dot {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

.student-profile__branch {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.student-profile__header-actions {
  display: flex;
  gap: var(--space-3);
  align-items: center;
  flex-wrap: wrap;
}

.student-profile__body {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--space-5);
  align-items: flex-start;
}

.student-profile__left {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.student-profile__right {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.student-profile__card {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.student-profile__card-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.student-profile__fields-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.student-profile__fields-grid--mt {
  margin-top: var(--space-2);
}

.student-profile__field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.student-profile__field--full {
  grid-column: 1 / -1;
  margin-top: var(--space-2);
}

.student-profile__field-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-1);
}

.student-profile__field-value {
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
}

.student-profile__field-value--bio {
  color: var(--color-text-secondary);
  line-height: var(--line-height-base);
}

.student-profile__cgpa {
  display: flex;
  align-items: baseline;
  margin-top: var(--space-1);
}

.student-profile__cgpa-value {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
}

.student-profile__cgpa-max {
  font-size: var(--font-size-base);
  color: var(--color-text-muted);
}

.student-profile__table-wrap {
  overflow-x: auto;
}

.student-profile__resume-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background-color: var(--color-gray-50);
  border-radius: var(--border-radius-lg);
  border: var(--border-width) solid var(--color-border);
}

.student-profile__resume-icon {
  font-size: var(--font-size-xl);
  color: var(--color-danger);
  flex-shrink: 0;
  line-height: 1;
}

.student-profile__resume-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  flex: 1;
  min-width: 0;
}

.student-profile__resume-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.student-profile__resume-meta {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.student-profile__resume-download {
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
  flex-shrink: 0;
}

.student-profile__resume-download:hover {
  background-color: var(--color-gray-100);
  color: var(--color-text-primary);
}

.student-profile__resume-actions {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: var(--space-2);
}

.student-profile__file-input {
  display: none;
}

.student-profile__resume-btn {
  width: 100%;
}

.student-profile__resume-hint {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  text-align: center;
  margin: 0;
}

.student-profile__placement-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-3);
}

.student-profile__placement-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.student-profile__placement-key {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.student-profile__placement-eligible {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
}

.student-profile__placement-eligible--yes {
  color: var(--color-success);
}

.student-profile__placement-eligible--no {
  color: var(--color-danger);
}

.student-profile__placement-pct {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-primary);
}

.student-profile__progress-track {
  width: 100%;
  height: 6px;
  background: var(--color-gray-200);
  border-radius: var(--border-radius-pill);
  margin-top: var(--space-2);
  overflow: hidden;
}

.student-profile__progress-track__fill {
  height: 100%;
  border-radius: var(--border-radius-pill);
  background: var(--color-primary);
  transition: width var(--transition-base);
}

.student-profile__modal-summary {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.student-profile__modal-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.student-profile__modal-name {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
}

.student-profile__modal-meta {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.student-profile__modal-cgpa {
  margin-left: auto;
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.student-profile__modal-cgpa span {
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
}

@media (max-width: 767px) {
  .student-profile__body {
    grid-template-columns: 1fr;
  }

  .student-profile__fields-grid {
    grid-template-columns: 1fr;
  }

  .student-profile__header-actions {
    width: 100%;
  }
}
</style>
