<template>
  <div class="dashboard">

    <!-- ── Toast ── -->
    <Transition name="toast">
      <div
        v-if="toast.message"
        class="dashboard__toast"
        :class="toast.type === 'error' ? 'dashboard__toast--error' : 'dashboard__toast--success'"
      >
        <i :class="toast.type === 'error' ? 'bi bi-x-circle-fill' : 'bi bi-check-circle-fill'"></i>
        {{ toast.message }}
      </div>
    </Transition>

    <!-- ── Welcome banner (auto-dismisses after 5s) ── -->
    <Transition
      @before-leave="(el) => { el.style.height = el.scrollHeight + 'px'; el.style.overflow = 'hidden' }"
      @leave="(el) => { el.style.transition = 'height 0.4s ease, opacity 0.4s ease'; el.style.height = '0'; el.style.opacity = '0' }"
    >
      <div v-if="showWelcome" class="dashboard__welcome">
        <div class="dashboard__welcome-inner">
          <div class="dashboard__greeting-block">
            <h2 class="dashboard__greeting">Good {{ timeOfDay }}, {{ firstName }}</h2>
            <p class="dashboard__greeting-sub">
              <template v-if="studentStore.dashboardLoading">Loading your stats…</template>
              <template v-else-if="eligibleCount > 0">
                You have <strong>{{ eligibleCount }}</strong> eligible drive{{ eligibleCount !== 1 ? 's' : '' }} waiting for you.
              </template>
              <template v-else>
                No new drives right now — check back soon.
              </template>
            </p>
          </div>

          <div class="dashboard__completion">
            <div class="dashboard__completion-header">
              <span class="dashboard__completion-label">Profile Completion</span>
              <span class="dashboard__completion-pct">{{ completionPct }}%</span>
            </div>
            <div class="dashboard__completion-track">
              <div class="dashboard__completion-fill" :style="{ width: completionPct + '%' }"></div>
            </div>
            <RouterLink v-if="completionPct < 100" to="/student/profile" class="dashboard__completion-hint">
              <i class="bi bi-info-circle"></i>
              {{ completionHint }}
            </RouterLink>
          </div>

          <button class="dashboard__welcome-close" @click="dismissWelcome" aria-label="Dismiss">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
      </div>
    </Transition>

    <!-- ── Shortlisted & Interview Invites ── -->
    <div v-if="shortlistedDrives.length" class="card dashboard__shortlisted">
      <h3 class="dashboard__section-heading">
        Shortlisted &amp; Interview Invites
      </h3>
      <div class="dashboard__shortlisted-list">
        <div
          v-for="item in shortlistedDrives"
          :key="item.application_id"
          class="dashboard__shortlisted-item"
        >
          <AppAvatar size="sm" :name="item.company_name" />
          <div class="dashboard__shortlisted-info">
            <span class="dashboard__shortlisted-role">{{ item.job_title }}</span>
            <span class="dashboard__shortlisted-company">{{ item.company_name }}</span>
          </div>
          <div class="dashboard__shortlisted-right">
            <span
              class="dashboard__shortlisted-badge"
              :class="item.status === 'selected' ? 'dashboard__shortlisted-badge--selected' : 'dashboard__shortlisted-badge--shortlisted'"
            >
              {{ item.status === 'selected' ? 'Selected' : 'Shortlisted' }}
            </span>
            <span v-if="item.interview_date" class="dashboard__shortlisted-date">
              {{ formatDate(item.interview_date) }}
            </span>
            <span
              v-if="item.interview_mode"
              class="dashboard__shortlisted-mode"
              :class="item.interview_mode === 'Online' ? 'dashboard__shortlisted-mode--online' : 'dashboard__shortlisted-mode--offline'"
            >
              {{ item.interview_mode }}
            </span>
            <a
              v-if="item.interview_link"
              :href="item.interview_link"
              target="_blank"
              rel="noopener noreferrer"
              class="dashboard__shortlisted-join"
            >
              <i class="bi bi-box-arrow-up-right"></i> Join
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Browse Drives ── -->
    <header class="dashboard__header">
      <div>
        <h1 class="dashboard__title">Browse Drives</h1>
        <p class="dashboard__subtitle">Discover and apply to placement opportunities matching your profile.</p>
      </div>
    </header>

    <!-- Filter bar -->
    <AppFilterBar
      v-model="searchQuery"
      placeholder="Search by company or role…"
      @update:modelValue="handleSearchDebounced"
    >
      <select class="filter-select" v-model="selectedJobType" @change="loadDrives">
        <option value="">All Types</option>
        <option v-for="t in JOB_TYPES" :key="t" :value="t">{{ t }}</option>
      </select>
      <label class="dashboard__eligible-toggle">
        <input type="checkbox" v-model="eligibleOnly" @change="loadDrives" />
        <span>Eligible Only</span>
      </label>
    </AppFilterBar>

    <!-- Drive cards -->
    <AppSpinner v-if="studentStore.drivesLoading" />

    <AppEmptyState
      v-else-if="studentStore.drivesError"
      icon="bi bi-exclamation-circle"
      title="Failed to load drives"
      :subtitle="studentStore.drivesError"
      actionLabel="Retry"
      @action="loadDrives"
    />

    <AppEmptyState
      v-else-if="!studentStore.drives.length"
      icon="bi bi-briefcase"
      title="No drives available"
      subtitle="There are no active placement drives at the moment. Check back soon!"
    />

    <div v-else class="dashboard__drives-grid">
      <StudentDriveCard
        v-for="drive in studentStore.drives.slice(0, displayCount)"
        :key="drive.drive_id"
        :drive="drive"
        :applying="studentStore.applyingDriveId === drive.drive_id"
        @apply="handleApply"
        @view="router.push('/student/drives/' + drive.drive_id)"
      />
    </div>
    <div v-if="studentStore.drives.length > displayCount" class="dashboard__drives-more">
      <button class="dashboard__load-more" @click="loadMore">
        Load more drives
        <i class="bi bi-chevron-down"></i>
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppAvatar from '@/components/common/AppAvatar.vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useStudentStore } from '@/stores/student'
import { formatDate } from '@/utils/formatters'
import { JOB_TYPES } from '@/utils/constants'
import AppFilterBar from '@/components/common/AppFilterBar.vue'
import AppSpinner from '@/components/common/AppSpinner.vue'
import AppEmptyState from '@/components/common/AppEmptyState.vue'
import StudentDriveCard from '@/components/student/StudentDriveCard.vue'

const router = useRouter()
const authStore = useAuthStore()
const studentStore = useStudentStore()

// ── Filters ──
const searchQuery = ref('')
const selectedJobType = ref('')
const eligibleOnly = ref(false)

let searchTimer = null
function handleSearchDebounced() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => loadDrives(), 350)
}

function loadDrives() {
  studentStore.fetchDrives({
    search: searchQuery.value,
    job_type: selectedJobType.value,
    eligible_only: eligibleOnly.value ? 'true' : '',
  })
}

// ── Dashboard data helpers ──
const dashboard = computed(() => studentStore.dashboard)

const breakdown = computed(() => ({
  applied: dashboard.value?.applications_breakdown?.applied ?? 0,
  shortlisted: dashboard.value?.applications_breakdown?.shortlisted ?? 0,
  selected: dashboard.value?.applications_breakdown?.selected ?? 0,
  rejected: dashboard.value?.applications_breakdown?.rejected ?? 0,
}))

const upcomingInterviews = computed(() => dashboard.value?.upcoming_interviews ?? [])
const shortlistedDrives = computed(() => dashboard.value?.shortlisted_drives ?? [])
const eligibleCount = computed(() => dashboard.value?.eligible_drives_not_applied ?? 0)

// ── Greeting ──
const firstName = computed(() => {
  const name = authStore.user?.name || dashboard.value?.profile?.full_name || 'there'
  return name.split(' ')[0]
})

const timeOfDay = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'morning'
  if (h < 18) return 'afternoon'
  return 'evening'
})

// ── Profile completion ──
const completionPct = computed(() => {
  const p = studentStore.profile
  if (!p) return 0

  const checks = [
    !!p.full_name,
    !!p.branch,
    !!p.year,
    p.cgpa !== null && p.cgpa !== undefined,
    !!p.phone,
    !!p.skills,
    !!p.resume_filename,
  ]
  const done = checks.filter(Boolean).length
  return Math.round((done / checks.length) * 100)
})

const completionHint = computed(() => {
  const p = studentStore.profile
  if (!p) return 'Complete your profile'
  if (!p.resume_filename) return 'Upload your resume to boost visibility'
  if (!p.skills) return 'Add your skills to improve matching'
  if (!p.phone) return 'Add your phone number to complete your profile'
  return 'Your profile looks great!'
})

// ── Welcome banner ──
const showWelcome = ref(true)
let welcomeTimer = null

function dismissWelcome() {
  showWelcome.value = false
  clearTimeout(welcomeTimer)
}

// ── Load More ──
const displayCount = ref(6)
function loadMore() {
  displayCount.value += 6
}

// ── Apply ──
const toast = ref({ message: '', type: 'success' })
let toastTimer = null

function showToast(message, type = 'success') {
  toast.value = { message, type }
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toast.value = { message: '', type: 'success' } }, 3500)
}

async function handleApply(driveId) {
  const result = await studentStore.applyToDrive(driveId)
  if (result.success) {
    showToast('Application submitted successfully!')
  } else {
    showToast(result.message || 'Failed to apply', 'error')
  }
}

// ── Init ──
onMounted(() => {
  studentStore.fetchDashboard()
  studentStore.fetchProfile()
  loadDrives()
  welcomeTimer = setTimeout(dismissWelcome, 5000)
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  position: relative;
}

/* ── Toast ── */
.dashboard__toast {
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

.dashboard__toast--success { background-color: var(--color-success); }
.dashboard__toast--error   { background-color: var(--color-danger); }

.toast-enter-active,
.toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from,
.toast-leave-to { opacity: 0; transform: translateX(20px); }

/* Welcome card */
.dashboard__welcome {
  background: linear-gradient(135deg, var(--color-primary) 0%, #1d4ed8 100%);
  border-radius: var(--border-radius-lg);
  padding: var(--space-4) var(--card-padding);
  box-shadow: var(--shadow-sm);
  color: var(--color-white);
}

.dashboard__welcome-close {
  background: rgba(255, 255, 255, 0.15);
  border: none;
  color: var(--color-white);
  width: 28px;
  height: 28px;
  min-width: 28px;
  border-radius: var(--border-radius-pill);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-xs);
  cursor: pointer;
  transition: background-color var(--transition-fast);
  align-self: center;
}

.dashboard__welcome-close:hover {
  background: rgba(255, 255, 255, 0.3);
}

.welcome-enter-active,
.welcome-leave-active {
  overflow: hidden;
}
.welcome-enter-from {
  opacity: 0;
}

.dashboard__welcome-inner {
  display: flex;
  align-items: center;
  gap: var(--space-8);
}

.dashboard__greeting {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-white);
  margin: 0 0 var(--space-2) 0;
}

.dashboard__greeting-sub {
  font-size: var(--font-size-sm);
  color: rgba(255, 255, 255, 0.85);
  margin: 0;
}

.dashboard__greeting-sub strong {
  color: var(--color-white);
  font-weight: var(--font-weight-bold);
}

/* Profile completion */
.dashboard__completion {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  flex: 1;
  min-width: 200px;
}

.dashboard__completion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dashboard__completion-label {
  font-size: var(--font-size-sm);
  color: rgba(255, 255, 255, 0.9);
  font-weight: var(--font-weight-medium);
}

.dashboard__completion-pct {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  color: var(--color-white);
}

.dashboard__completion-track {
  height: 8px;
  background-color: rgba(255, 255, 255, 0.25);
  border-radius: var(--border-radius-pill);
  overflow: hidden;
}

.dashboard__completion-fill {
  height: 100%;
  background-color: var(--color-white);
  border-radius: var(--border-radius-pill);
  transition: width 0.6s ease;
}

.dashboard__completion-hint {
  font-size: var(--font-size-xs);
  color: rgba(255, 255, 255, 0.75);
  display: flex;
  align-items: center;
  gap: var(--space-1);
  text-decoration: none;
}

.dashboard__completion-hint:hover {
  color: var(--color-white);
}

/* ── Shortlisted & Interview Invites ── */
.dashboard__shortlisted {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.dashboard__section-heading {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.dashboard__section-heading i {
  color: var(--color-warning);
}

.dashboard__shortlisted-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.dashboard__shortlisted-item {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-3) var(--space-4);
  background-color: var(--color-gray-50);
  border-radius: var(--border-radius-md);
  flex-wrap: wrap;
}

.dashboard__shortlisted-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.dashboard__shortlisted-role {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dashboard__shortlisted-company {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.dashboard__shortlisted-right {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-shrink: 0;
  flex-wrap: wrap;
}

.dashboard__shortlisted-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  padding: 3px var(--space-2);
  border-radius: var(--border-radius-pill);
}

.dashboard__shortlisted-badge--shortlisted {
  background-color: var(--color-warning-light);
  color: var(--color-warning);
}

.dashboard__shortlisted-badge--selected {
  background-color: var(--color-success-light);
  color: var(--color-success);
}

.dashboard__shortlisted-date {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.dashboard__shortlisted-mode {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  padding: 2px var(--space-2);
  border-radius: var(--border-radius-pill);
}

.dashboard__shortlisted-mode--online {
  background-color: var(--color-success-light);
  color: var(--color-success);
}

.dashboard__shortlisted-mode--offline {
  background-color: var(--color-warning-light);
  color: var(--color-warning);
}

.dashboard__shortlisted-join {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-primary);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--border-radius-sm);
  transition: background-color var(--transition-fast);
}

.dashboard__shortlisted-join:hover {
  background-color: var(--color-primary-light);
}

/* ── Browse Drives section ── */
.dashboard__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.dashboard__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-1) 0;
}

.dashboard__subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

/* Eligible-only toggle in filter bar */
.dashboard__eligible-toggle {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}

.dashboard__eligible-toggle input {
  accent-color: var(--color-primary);
  width: 15px;
  height: 15px;
  cursor: pointer;
}

/* Drive cards grid */
.dashboard__drives-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-6);
}

.dashboard__drives-more {
  text-align: center;
  padding-top: var(--space-2);
}

.dashboard__load-more {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-6);
  background: var(--color-content-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.dashboard__load-more:hover {
  background-color: var(--color-gray-50);
  color: var(--color-text-primary);
  border-color: var(--color-primary);
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .dashboard__welcome-inner {
    flex-direction: column;
    gap: var(--space-4);
  }

  .dashboard__drives-grid {
    grid-template-columns: 1fr;
  }
}
</style>
