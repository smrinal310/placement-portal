<template>
  <div class="profile-edit">

    <!-- ── Toast ── -->
    <Transition name="toast">
      <div
        v-if="toast.message"
        class="profile-edit__toast"
        :class="`profile-edit__toast--${toast.type}`"
      >
        <i :class="toast.type === 'error' ? 'bi bi-x-circle-fill' : 'bi bi-check-circle-fill'"></i>
        {{ toast.message }}
      </div>
    </Transition>

    <AppSpinner v-if="loading && !form.full_name" />

    <AppEmptyState
      v-else-if="fetchError"
      icon="bi bi-exclamation-circle"
      title="Failed to load profile"
      :subtitle="fetchError"
      actionLabel="Retry"
      @action="loadProfile"
    />

    <template v-else>
      <!-- ── Header ── -->
      <header class="profile-edit__header">
        <div class="profile-edit__header-left">
          <RouterLink to="/student/profile" class="profile-edit__back">
            <i class="bi bi-arrow-left"></i> Back to Profile
          </RouterLink>
          <h1 class="profile-edit__title">Edit Profile</h1>
          <p class="profile-edit__subtitle">Keep your information up to date to improve your placement chances.</p>
        </div>
      </header>

      <div class="profile-edit__layout">

        <!-- ── Main form ── -->
        <div class="profile-edit__main">

          <!-- Personal Details -->
          <form class="card profile-edit__section-card" @submit.prevent="handleSave">
            <h2 class="profile-edit__section-title">Personal Details</h2>

            <div class="profile-edit__fields-grid">
              <div class="profile-edit__field">
                <label class="profile-edit__label">Full Name <span class="profile-edit__required">*</span></label>
                <input
                  type="text"
                  class="profile-edit__input"
                  v-model="form.full_name"
                  placeholder="Your full name"
                  required
                />
              </div>
              <div class="profile-edit__field">
                <label class="profile-edit__label">Phone Number</label>
                <input
                  type="tel"
                  class="profile-edit__input"
                  v-model="form.phone"
                  placeholder="+91 00000 00000"
                />
              </div>
              <div class="profile-edit__field">
                <label class="profile-edit__label">Gender</label>
                <select class="profile-edit__input profile-edit__select" v-model="form.gender">
                  <option value="">Select gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                  <option value="Prefer not to say">Prefer not to say</option>
                </select>
              </div>
              <div class="profile-edit__field">
                <label class="profile-edit__label">Date of Birth</label>
                <input
                  type="date"
                  class="profile-edit__input"
                  v-model="form.date_of_birth"
                />
              </div>
              <div class="profile-edit__field profile-edit__field--full">
                <label class="profile-edit__label">Address</label>
                <textarea
                  class="profile-edit__input profile-edit__textarea"
                  v-model="form.address"
                  placeholder="Your address"
                  rows="2"
                ></textarea>
              </div>
              <div class="profile-edit__field">
                <label class="profile-edit__label">LinkedIn URL</label>
                <input
                  type="url"
                  class="profile-edit__input"
                  v-model="form.linkedin_url"
                  placeholder="https://linkedin.com/in/yourprofile"
                />
              </div>
              <div class="profile-edit__field">
                <label class="profile-edit__label">GitHub URL</label>
                <input
                  type="url"
                  class="profile-edit__input"
                  v-model="form.github_url"
                  placeholder="https://github.com/yourusername"
                />
              </div>
              <div class="profile-edit__field profile-edit__field--full">
                <label class="profile-edit__label">Skills</label>
                <textarea
                  class="profile-edit__input profile-edit__textarea"
                  v-model="form.skills"
                  placeholder="e.g. Java, Python, React, SQL"
                  rows="2"
                ></textarea>
              </div>
            </div>

            <h2 class="profile-edit__section-title profile-edit__section-title--mt">Academic Details</h2>
            <div class="profile-edit__fields-grid">
              <div class="profile-edit__field">
                <label class="profile-edit__label">Branch / Degree Program <span class="profile-edit__required">*</span></label>
                <select class="profile-edit__input profile-edit__select" v-model="form.branch" required>
                  <option value="">Select branch</option>
                  <option v-for="b in BRANCH_LIST" :key="b" :value="b">{{ b }}</option>
                </select>
              </div>
              <div class="profile-edit__field">
                <label class="profile-edit__label">Year of Study <span class="profile-edit__required">*</span></label>
                <select class="profile-edit__input profile-edit__select" v-model.number="form.year" required>
                  <option value="">Select year</option>
                  <option :value="1">1st Year</option>
                  <option :value="2">2nd Year</option>
                  <option :value="3">3rd Year</option>
                  <option :value="4">4th Year</option>
                </select>
              </div>
              <div class="profile-edit__field">
                <label class="profile-edit__label">CGPA (0 – 10) <span class="profile-edit__required">*</span></label>
                <input
                  type="number"
                  class="profile-edit__input"
                  v-model.number="form.cgpa"
                  step="0.01"
                  min="0"
                  max="10"
                  placeholder="e.g. 8.5"
                  required
                />
              </div>
            </div>

            <div class="profile-edit__form-actions">
              <AppButton type="submit" variant="primary" :loading="saving">Save Changes</AppButton>
              <RouterLink to="/student/profile">
                <AppButton type="button" variant="outline">Cancel</AppButton>
              </RouterLink>
            </div>
          </form>
        </div>

        <!-- ── Sidebar ── -->
        <div class="profile-edit__sidebar">

          <!-- Resume -->
          <div class="card profile-edit__section-card">
            <h2 class="profile-edit__section-title">Resume &amp; Documents</h2>

            <div v-if="resumeFilename" class="profile-edit__resume-row">
              <div class="profile-edit__resume-icon">
                <i class="bi bi-file-pdf"></i>
              </div>
              <div class="profile-edit__resume-info">
                <span class="profile-edit__resume-name">{{ truncate(resumeFilename, 22) }}</span>
                <span class="profile-edit__resume-meta">Current resume</span>
              </div>
              <button class="profile-edit__resume-dl" @click="handleDownloadResume" title="Download">
                <i class="bi bi-download"></i>
              </button>
            </div>
            <AppEmptyState
              v-else
              icon="bi bi-file-earmark"
              title="No resume uploaded"
              subtitle=""
            />

            <input
              ref="fileInputRef"
              type="file"
              accept=".pdf,.docx"
              class="profile-edit__file-hidden"
              @change="handleResumeUpload"
            />
            <AppButton
              variant="outline"
              iconLeft="bi bi-upload"
              :loading="resumeUploading"
              class="profile-edit__resume-btn"
              @click="fileInputRef.click()"
            >
              {{ resumeFilename ? 'Replace Resume' : 'Upload Resume' }}
            </AppButton>
            <p class="profile-edit__hint">PDF or DOCX · Max 5MB</p>
          </div>

          <!-- Placement status (read-only) -->
          <div class="card profile-edit__section-card">
            <div class="profile-edit__placement-label">Placement Status</div>
            <div class="profile-edit__placement-row">
              <span class="profile-edit__placement-key">Profile Completion</span>
              <span class="profile-edit__placement-pct">{{ completionPct }}%</span>
            </div>
            <div class="profile-edit__progress-track">
              <div
                class="profile-edit__progress-fill"
                :style="{ width: completionPct + '%' }"
              ></div>
            </div>
          </div>

        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStudentStore } from '@/stores/student'
import * as studentApi from '@/api/student'
import { truncate } from '@/utils/formatters'
import { BRANCH_LIST } from '@/utils/constants'
import AppButton from '@/components/common/AppButton.vue'
import AppSpinner from '@/components/common/AppSpinner.vue'
import AppEmptyState from '@/components/common/AppEmptyState.vue'

const router = useRouter()
const studentStore = useStudentStore()

const loading = ref(false)
const saving = ref(false)
const fetchError = ref('')
const resumeUploading = ref(false)
const resumeFilename = ref('')
const fileInputRef = ref(null)

const toast = ref({ message: '', type: 'success' })
let toastTimer = null

const form = ref({
  full_name: '',
  phone: '',
  gender: '',
  date_of_birth: '',
  address: '',
  linkedin_url: '',
  github_url: '',
  skills: '',
  branch: '',
  year: '',
  cgpa: '',
})

const completionPct = computed(() => {
  const f = form.value
  const checks = [
    !!f.full_name,
    !!f.branch,
    !!f.year,
    f.cgpa !== '' && f.cgpa !== null && f.cgpa !== undefined,
    !!f.phone,
    !!f.skills,
    !!resumeFilename.value,
  ]
  return Math.round((checks.filter(Boolean).length / checks.length) * 100)
})

function showToast(message, type = 'success') {
  toast.value = { message, type }
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toast.value = { message: '', type: 'success' } }, 3500)
}

async function loadProfile() {
  loading.value = true
  fetchError.value = ''
  try {
    const res = await studentApi.getProfile()
    const p = res.data
    form.value = {
      full_name: p.full_name ?? '',
      phone: p.phone ?? '',
      gender: p.gender ?? '',
      date_of_birth: p.date_of_birth ?? '',
      address: p.address ?? '',
      linkedin_url: p.linkedin_url ?? '',
      github_url: p.github_url ?? '',
      skills: p.skills ?? '',
      branch: p.branch ?? '',
      year: p.year ?? '',
      cgpa: p.cgpa ?? '',
    }
    resumeFilename.value = p.resume_filename ?? ''
  } catch (e) {
    fetchError.value = e.message || 'Failed to load profile.'
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  saving.value = true
  try {
    const payload = { ...form.value }
    // Remove blank optional strings so the backend ignores them
    Object.keys(payload).forEach((k) => {
      if (payload[k] === '') delete payload[k]
    })
    await studentApi.updateProfile(payload)
    // Invalidate all student store caches so stale eligibility/dashboard data is refreshed
    await Promise.all([
      studentStore.fetchProfile(),
      studentStore.fetchDashboard(),
      studentStore.fetchDrives(),
    ])
    showToast('Profile saved successfully!')
    router.push('/student/profile')
  } catch (e) {
    showToast(e.message || 'Failed to save profile.', 'error')
  } finally {
    saving.value = false
  }
}

async function handleResumeUpload(event) {
  const file = event.target.files?.[0]
  if (!file) return
  resumeUploading.value = true
  try {
    await studentApi.uploadResume(file)
    resumeFilename.value = file.name
    showToast('Resume uploaded successfully!')
  } catch (e) {
    showToast(e.message || 'Failed to upload resume.', 'error')
  } finally {
    resumeUploading.value = false
    event.target.value = ''
  }
}

async function handleDownloadResume() {
  try {
    await studentApi.downloadResume(resumeFilename.value)
  } catch {
    showToast('Failed to download resume.', 'error')
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile-edit {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  position: relative;
}

/* ── Toast ── */
.profile-edit__toast {
  position: fixed;
  top: var(--space-6);
  right: var(--space-6);
  z-index: 100;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-5);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-white);
  box-shadow: var(--shadow-md);
}

.profile-edit__toast--success { background-color: var(--color-success); }
.profile-edit__toast--error   { background-color: var(--color-danger); }

.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(20px); }

/* ── Header ── */
.profile-edit__back {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  text-decoration: none;
  margin-bottom: var(--space-2);
}

.profile-edit__back:hover { color: var(--color-primary); }

.profile-edit__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-1);
}

.profile-edit__subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

/* ── Layout ── */
.profile-edit__layout {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: var(--space-6);
  align-items: start;
}

/* ── Section card ── */
.profile-edit__section-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.profile-edit__section-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--color-border);
}

.profile-edit__section-title--mt {
  margin-top: var(--space-2);
}

/* ── Fields ── */
.profile-edit__fields-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.profile-edit__field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.profile-edit__field--full {
  grid-column: 1 / -1;
}

.profile-edit__label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.profile-edit__required {
  color: var(--color-danger);
}

.profile-edit__input {
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  background-color: var(--color-content-bg);
  outline: none;
  transition: border-color var(--transition-fast);
  width: 100%;
  box-sizing: border-box;
}

.profile-edit__input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.profile-edit__select {
  cursor: pointer;
  appearance: auto;
}

.profile-edit__textarea {
  resize: vertical;
  min-height: 64px;
  font-family: inherit;
}

/* ── Form actions ── */
.profile-edit__form-actions {
  display: flex;
  gap: var(--space-3);
  padding-top: var(--space-2);
  border-top: 1px solid var(--color-border);
}

/* ── Sidebar ── */
.profile-edit__sidebar {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

/* Resume card */
.profile-edit__resume-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  background-color: var(--color-gray-50);
  border-radius: var(--border-radius-md);
}

.profile-edit__resume-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--border-radius-sm);
  background-color: var(--color-danger-light, #fee2e2);
  color: var(--color-danger);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-base);
  flex-shrink: 0;
}

.profile-edit__resume-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.profile-edit__resume-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.profile-edit__resume-meta {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.profile-edit__resume-dl {
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: var(--space-1);
  border-radius: var(--border-radius-sm);
  transition: color var(--transition-fast);
}

.profile-edit__resume-dl:hover { color: var(--color-primary); }

.profile-edit__file-hidden {
  display: none;
}

.profile-edit__resume-btn {
  width: 100%;
}

.profile-edit__hint {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  margin: 0;
  text-align: center;
}

/* Placement status mini-card */
.profile-edit__placement-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: var(--space-3);
}

.profile-edit__placement-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
}

.profile-edit__placement-key {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.profile-edit__placement-pct {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-primary);
}

.profile-edit__progress-track {
  height: 8px;
  background-color: var(--color-gray-100, #f3f4f6);
  border-radius: var(--border-radius-pill);
  overflow: hidden;
}

.profile-edit__progress-fill {
  height: 100%;
  background-color: var(--color-primary);
  border-radius: var(--border-radius-pill);
  transition: width 0.5s ease;
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .profile-edit__layout {
    grid-template-columns: 1fr;
  }

  .profile-edit__sidebar {
    order: -1;
  }
}

@media (max-width: 600px) {
  .profile-edit__fields-grid {
    grid-template-columns: 1fr;
  }
}
</style>
