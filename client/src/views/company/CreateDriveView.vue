<template>
  <div class="create-drive">

    <Transition name="toast">
      <div v-if="toast.message" :class="['create-drive__toast', `create-drive__toast--${toast.type}`]">
        <i :class="toast.type === 'error' ? 'bi bi-x-circle-fill' : 'bi bi-check-circle-fill'"></i>
        {{ toast.message }}
      </div>
    </Transition>

    <div class="create-drive__header">
      <div>
        <router-link to="/company/drives" class="create-drive__back">
          <i class="bi bi-arrow-left"></i> Back to Drives
        </router-link>
        <h1 class="create-drive__title">{{ isEditMode ? 'Edit Drive' : 'Create Placement Drive' }}</h1>
        <p class="create-drive__subtitle">
          {{ isEditMode
            ? 'Update the drive details below. Note: title, type, eligibility and deadline cannot be changed after creation.'
            : 'Fill in the details below. The drive will be submitted for admin approval before students can apply.'
          }}
        </p>
      </div>
    </div>

    <AppSpinner v-if="loadingDrive" />

    <AppEmptyState
      v-else-if="loadError"
      icon="bi bi-exclamation-circle"
      title="Failed to load drive"
      :subtitle="loadError"
      actionLabel="Retry"
      @action="loadDrive"
    />

    <form v-if="!loadingDrive && !loadError" class="create-drive__form" @submit.prevent="handleSubmit">

      <!-- ── Job Details ── -->
      <div class="card create-drive__section">
        <h2 class="create-drive__section-title">
          <i class="bi bi-briefcase create-drive__section-icon"></i>
          Job Details
        </h2>

        <div class="create-drive__grid">
          <div class="create-drive__field create-drive__field--full">
            <label class="create-drive__label">
              Job Title <span class="create-drive__required">*</span>
              <span v-if="isEditMode" class="create-drive__locked"><i class="bi bi-lock-fill"></i> locked</span>
            </label>
            <input
              type="text"
              class="create-drive__input"
              :class="{ 'create-drive__input--error': errors.job_title, 'create-drive__input--locked': isEditMode }"
              v-model="form.job_title"
              :disabled="isEditMode"
              placeholder="e.g. Software Engineer, Data Analyst"
              maxlength="120"
            />
            <span v-if="errors.job_title" class="create-drive__error">{{ errors.job_title }}</span>
          </div>

          <div class="create-drive__field">
            <label class="create-drive__label">
              Job Type
              <span v-if="isEditMode" class="create-drive__locked"><i class="bi bi-lock-fill"></i> locked</span>
            </label>
            <select class="create-drive__select" v-model="form.job_type" :disabled="isEditMode"
              :class="{ 'create-drive__input--locked': isEditMode }">
              <option value="">Select type</option>
              <option v-for="t in JOB_TYPES" :key="t" :value="t">{{ t }}</option>
            </select>
          </div>

          <div class="create-drive__field">
            <label class="create-drive__label">Location</label>
            <input
              type="text"
              class="create-drive__input"
              v-model="form.job_location"
              placeholder="e.g. Bangalore, Remote"
            />
          </div>

          <div class="create-drive__field">
            <label class="create-drive__label">CTC / Stipend</label>
            <input
              type="text"
              class="create-drive__input"
              v-model="form.salary_package"
              placeholder="e.g. 12 LPA, ₹30,000/month"
            />
          </div>

          <div class="create-drive__field">
            <label class="create-drive__label">Total Vacancies</label>
            <input
              type="number"
              class="create-drive__input"
              :class="{ 'create-drive__input--error': errors.vacancy_count }"
              v-model.number="form.vacancy_count"
              min="0"
              placeholder="0"
            />
            <span v-if="errors.vacancy_count" class="create-drive__error">{{ errors.vacancy_count }}</span>
          </div>

          <div class="create-drive__field create-drive__field--full">
            <label class="create-drive__label">
              Job Description <span class="create-drive__required">*</span>
            </label>
            <textarea
              class="create-drive__textarea"
              :class="{ 'create-drive__input--error': errors.job_description }"
              v-model="form.job_description"
              rows="5"
              placeholder="Describe the role, responsibilities, and what the candidate will be doing..."
            ></textarea>
            <span v-if="errors.job_description" class="create-drive__error">{{ errors.job_description }}</span>
          </div>

          <div class="create-drive__field create-drive__field--full">
            <label class="create-drive__label">
              Other / Technical Criteria
              <span class="create-drive__hint-inline"> — one item per line, shown as tags</span>
            </label>
            <textarea
              class="create-drive__textarea"
              v-model="form.other_criteria"
              rows="3"
              placeholder="e.g.&#10;Strong DSA skills&#10;Knowledge of React&#10;No active backlogs"
            ></textarea>
          </div>
        </div>
      </div>

      <!-- ── Eligibility ── -->
      <div class="card create-drive__section">
        <h2 class="create-drive__section-title">
          <i class="bi bi-patch-check create-drive__section-icon"></i>
          Eligibility Criteria
        </h2>

        <div class="create-drive__grid">
          <div class="create-drive__field">
            <label class="create-drive__label">Minimum CGPA
              <span v-if="isEditMode" class="create-drive__locked"><i class="bi bi-lock-fill"></i> locked</span>
            </label>
            <input
              type="number"
              class="create-drive__input"
              :class="{ 'create-drive__input--error': errors.min_cgpa, 'create-drive__input--locked': isEditMode }"
              v-model.number="form.min_cgpa"
              :disabled="isEditMode"
              min="0" max="10" step="0.1"
              placeholder="0.0"
            />
            <span v-if="errors.min_cgpa" class="create-drive__error">{{ errors.min_cgpa }}</span>
          </div>

          <div class="create-drive__field">
            <label class="create-drive__label">
              Eligible Graduation Years
              <span v-if="isEditMode" class="create-drive__locked"><i class="bi bi-lock-fill"></i> locked</span>
            </label>
            <div class="create-drive__year-range">
              <select class="create-drive__select" v-model.number="form.min_year" :disabled="isEditMode"
                :class="{ 'create-drive__input--locked': isEditMode }">
                <option v-for="y in YEARS" :key="y" :value="y">Year {{ y }}</option>
              </select>
              <span class="create-drive__year-sep">to</span>
              <select class="create-drive__select" v-model.number="form.max_year" :disabled="isEditMode"
                :class="{ 'create-drive__input--locked': isEditMode }">
                <option v-for="y in YEARS" :key="y" :value="y">Year {{ y }}</option>
              </select>
            </div>
            <span v-if="errors.year_range" class="create-drive__error">{{ errors.year_range }}</span>
          </div>

          <div class="create-drive__field create-drive__field--full">
            <label class="create-drive__label">
              Eligible Branches
              <span v-if="isEditMode" class="create-drive__locked"><i class="bi bi-lock-fill"></i> locked</span>
            </label>
            <div class="create-drive__branches">
              <label
                v-for="branch in BRANCH_LIST"
                :key="branch"
                class="create-drive__branch-option"
                :class="{ 'create-drive__branch-option--locked': isEditMode }"
              >
                <input
                  type="checkbox"
                  :value="branch"
                  v-model="form.eligible_branches"
                  :disabled="isEditMode"
                  class="create-drive__checkbox"
                />
                <span>{{ branch }}</span>
              </label>
            </div>
            <button
              v-if="!isEditMode"
              type="button"
              class="create-drive__select-all"
              @click="toggleAllBranches"
            >
              {{ form.eligible_branches.length === BRANCH_LIST.length ? 'Deselect All' : 'Select All' }}
            </button>
          </div>
        </div>
      </div>

      <!-- ── Schedule ── -->
      <div class="card create-drive__section">
        <h2 class="create-drive__section-title">
          <i class="bi bi-calendar3 create-drive__section-icon"></i>
          Schedule
        </h2>

        <div class="create-drive__grid">
          <div class="create-drive__field">
            <label class="create-drive__label">
              Application Deadline <span class="create-drive__required">*</span>
              <span v-if="isEditMode" class="create-drive__locked"><i class="bi bi-lock-fill"></i> locked</span>
            </label>
            <input
              type="datetime-local"
              class="create-drive__input"
              :class="{ 'create-drive__input--error': errors.application_deadline, 'create-drive__input--locked': isEditMode }"
              v-model="form.application_deadline"
              :min="minDatetime"
              :disabled="isEditMode"
            />
            <span v-if="errors.application_deadline" class="create-drive__error">{{ errors.application_deadline }}</span>
          </div>

          <div class="create-drive__field">
            <label class="create-drive__label">Drive Date <span class="create-drive__hint-inline">(optional)</span></label>
            <input
              type="datetime-local"
              class="create-drive__input"
              v-model="form.drive_date"
            />
          </div>
        </div>
      </div>

      <!-- ── Form Error + Actions ── -->
      <div v-if="formError" class="create-drive__form-error">
        <i class="bi bi-exclamation-circle"></i> {{ formError }}
      </div>

      <div class="create-drive__actions">
        <AppButton variant="outline" type="button" @click="router.push('/company/drives')">
          Cancel
        </AppButton>
        <AppButton variant="primary" type="submit" :loading="submitting"
          :iconLeft="isEditMode ? 'bi bi-check-lg' : 'bi bi-send'"
        >
          {{ isEditMode ? 'Save Changes' : 'Submit for Approval' }}
        </AppButton>
      </div>

    </form>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import * as companyApi from '@/api/company'
import { BRANCH_LIST, JOB_TYPES } from '@/utils/constants'
import AppButton from '@/components/common/AppButton.vue'
import AppSpinner from '@/components/common/AppSpinner.vue'
import AppEmptyState from '@/components/common/AppEmptyState.vue'

const router = useRouter()
const route = useRoute()

const YEARS = [1, 2, 3, 4]

// ── Mode detection ──
const driveId = computed(() => route.params.id ?? null)
const isEditMode = computed(() => !!driveId.value)

// ── Load state (edit mode only) ──
const loadingDrive = ref(false)
const loadError = ref('')

// ── Helpers ──
function toLocalDatetimeString(date) {
  if (!date) return ''
  const d = new Date(date)
  d.setMinutes(d.getMinutes() - d.getTimezoneOffset())
  return d.toISOString().slice(0, 16)
}

const minDatetime = computed(() => toLocalDatetimeString(Date.now() + 60_000))

// ── State ──
const submitting = ref(false)
const formError = ref('')
const errors = ref({})
const toast = ref({ message: '', type: 'success' })
let toastTimer = null

const form = ref({
  job_title: '',
  job_description: '',
  job_location: '',
  job_type: '',
  salary_package: '',
  vacancy_count: '',
  other_criteria: '',
  min_cgpa: '',
  min_year: 1,
  max_year: 4,
  eligible_branches: [],
  application_deadline: '',
  drive_date: '',
})

// ── Validation ──
function validate() {
  const e = {}

  if (!form.value.job_title.trim()) {
    e.job_title = 'Job title is required.'
  }

  if (!form.value.job_description.trim()) {
    e.job_description = 'Job description is required.'
  }

  if (!isEditMode.value) {
    if (!form.value.application_deadline) {
      e.application_deadline = 'Application deadline is required.'
    } else if (new Date(form.value.application_deadline) <= new Date()) {
      e.application_deadline = 'Deadline must be a future date and time.'
    }
  }

  const cgpa = form.value.min_cgpa
  if (cgpa !== '' && cgpa !== null) {
    const n = Number(cgpa)
    if (isNaN(n) || n < 0 || n > 10) {
      e.min_cgpa = 'CGPA must be between 0.0 and 10.0.'
    }
  }

  if (form.value.vacancy_count !== '' && form.value.vacancy_count !== null) {
    const n = Number(form.value.vacancy_count)
    if (!Number.isInteger(n) || n < 0) {
      e.vacancy_count = 'Vacancies must be a non-negative whole number.'
    }
  }

  if (form.value.min_year > form.value.max_year) {
    e.year_range = 'Min year cannot be greater than max year.'
  }

  errors.value = e
  return Object.keys(e).length === 0
}

// ── Submit ──
async function handleSubmit() {
  formError.value = ''

  if (!validate()) return

  if (isEditMode.value) {
    // Edit mode: only send editable fields
    const payload = {
      job_description: form.value.job_description.trim(),
    }
    if (form.value.job_location.trim()) payload.job_location = form.value.job_location.trim()
    else payload.job_location = null
    if (form.value.salary_package.trim()) payload.salary_package = form.value.salary_package.trim()
    else payload.salary_package = null
    if (form.value.other_criteria.trim()) payload.other_criteria = form.value.other_criteria.trim()
    else payload.other_criteria = null
    payload.vacancy_count = form.value.vacancy_count !== '' && form.value.vacancy_count !== null
      ? Number(form.value.vacancy_count) : 0
    payload.drive_date = form.value.drive_date ? new Date(form.value.drive_date).toISOString() : null

    submitting.value = true
    try {
      await companyApi.updateDrive(driveId.value, payload)
      showToast('Drive updated successfully.')
      setTimeout(() => router.push('/company/drives'), 1200)
    } catch (e) {
      formError.value = e.response?.data?.message || e.message || 'Failed to update drive.'
    } finally {
      submitting.value = false
    }
    return
  }

  // Create mode
  const payload = {
    job_title: form.value.job_title.trim(),
    job_description: form.value.job_description.trim(),
    application_deadline: new Date(form.value.application_deadline).toISOString(),
    min_year: form.value.min_year,
    max_year: form.value.max_year,
  }

  if (form.value.job_type) payload.job_type = form.value.job_type
  if (form.value.job_location.trim()) payload.job_location = form.value.job_location.trim()
  if (form.value.salary_package.trim()) payload.salary_package = form.value.salary_package.trim()
  if (form.value.other_criteria.trim()) payload.other_criteria = form.value.other_criteria.trim()
  if (form.value.vacancy_count !== '' && form.value.vacancy_count !== null) {
    payload.vacancy_count = Number(form.value.vacancy_count)
  }
  if (form.value.min_cgpa !== '' && form.value.min_cgpa !== null) {
    payload.min_cgpa = Number(form.value.min_cgpa)
  }
  if (form.value.eligible_branches.length > 0) {
    payload.eligible_branches = form.value.eligible_branches
  }
  if (form.value.drive_date) {
    payload.drive_date = new Date(form.value.drive_date).toISOString()
  }

  submitting.value = true
  try {
    const res = await companyApi.createDrive(payload)
    showToast('Drive submitted for approval!')
    const id = res.data?.data?.id
    setTimeout(() => {
      if (id) {
        router.push(`/company/drives/${id}/applications`)
      } else {
        router.push('/company/drives')
      }
    }, 1200)
  } catch (e) {
    formError.value = e.response?.data?.message || e.message || 'Failed to create drive.'
  } finally {
    submitting.value = false
  }
}

// ── Load drive for edit mode ──
async function loadDrive() {
  if (!isEditMode.value) return
  loadingDrive.value = true
  loadError.value = ''
  try {
    const res = await companyApi.getDrive(driveId.value)
    const d = res.data
    form.value = {
      job_title: d.job_title || '',
      job_description: d.job_description || '',
      job_location: d.job_location || '',
      job_type: d.job_type || '',
      salary_package: d.salary_package || '',
      vacancy_count: d.vacancy_count ?? '',
      other_criteria: d.other_criteria || '',
      min_cgpa: d.min_cgpa ?? '',
      min_year: d.min_year ?? 1,
      max_year: d.max_year ?? 4,
      eligible_branches: d.eligible_branches
        ? d.eligible_branches.split(',').map(b => b.trim()).filter(Boolean)
        : [],
      application_deadline: toLocalDatetimeString(d.application_deadline),
      drive_date: toLocalDatetimeString(d.drive_date),
    }
  } catch (e) {
    loadError.value = e.response?.data?.message || e.message || 'Failed to load drive.'
  } finally {
    loadingDrive.value = false
  }
}

onMounted(loadDrive)

// ── Branch helpers ──
function toggleAllBranches() {
  if (form.value.eligible_branches.length === BRANCH_LIST.length) {
    form.value.eligible_branches = []
  } else {
    form.value.eligible_branches = [...BRANCH_LIST]
  }
}

// ── Toast ──
function showToast(message, type = 'success') {
  toast.value = { message, type }
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toast.value = { message: '', type: 'success' }
  }, 3500)
}
</script>

<style scoped>
.create-drive {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  position: relative;
}

/* ── Toast ── */
.create-drive__toast {
  position: fixed;
  top: var(--space-5);
  right: var(--space-5);
  z-index: var(--z-tooltip);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-5);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  box-shadow: var(--shadow-md);
  max-width: 360px;
}

.create-drive__toast--success {
  background-color: var(--color-success-light);
  color: var(--color-success);
  border: var(--border-width) solid var(--color-success);
}

.create-drive__toast--error {
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

/* ── Header ── */
.create-drive__back {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  text-decoration: none;
  margin-bottom: var(--space-2);
  transition: color var(--transition-fast);
}

.create-drive__back:hover {
  color: var(--color-primary);
}

.create-drive__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-1);
}

.create-drive__subtitle {
  font-size: var(--font-size-base);
  color: var(--color-text-muted);
  margin: 0;
}

/* ── Form layout ── */
.create-drive__form {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.create-drive__section {
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.create-drive__section-title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.create-drive__section-icon {
  color: var(--color-primary);
  font-size: var(--font-size-md);
}

.create-drive__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4) var(--space-5);
}

.create-drive__field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.create-drive__field--full {
  grid-column: 1 / -1;
}

.create-drive__label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.create-drive__required {
  color: var(--color-danger);
}

.create-drive__hint-inline {
  font-weight: var(--font-weight-normal);
  color: var(--color-text-muted);
  font-size: var(--font-size-xs);
}

.create-drive__input,
.create-drive__select,
.create-drive__textarea {
  padding: var(--space-2) var(--space-3);
  border: var(--border-width) solid var(--border-color);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-base);
  font-family: var(--font-family-base);
  color: var(--color-text-primary);
  background: var(--color-white);
  transition: border-color var(--transition-fast);
  outline: none;
}

.create-drive__input:focus,
.create-drive__select:focus,
.create-drive__textarea:focus {
  border-color: var(--color-primary);
}

.create-drive__input--error {
  border-color: var(--color-danger) !important;
}

.create-drive__textarea {
  resize: vertical;
  min-height: 80px;
}

.create-drive__error {
  font-size: var(--font-size-xs);
  color: var(--color-danger);
}

.create-drive__locked {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-normal);
  color: var(--color-text-muted);
  margin-left: var(--space-2);
}

.create-drive__input--locked,
.create-drive__input--locked:focus {
  background: var(--color-gray-100);
  color: var(--color-text-muted);
  cursor: not-allowed;
  border-color: var(--border-color);
}

.create-drive__branch-option--locked {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── Branches ── */
.create-drive__branches {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2) var(--space-4);
}

.create-drive__branch-option {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  cursor: pointer;
  user-select: none;
}

.create-drive__checkbox {
  accent-color: var(--color-primary);
  width: 15px;
  height: 15px;
  cursor: pointer;
}

.create-drive__select-all {
  align-self: flex-start;
  margin-top: var(--space-2);
  background: none;
  border: none;
  padding: 0;
  font-size: var(--font-size-sm);
  color: var(--color-primary);
  cursor: pointer;
  font-family: var(--font-family-base);
}

.create-drive__select-all:hover {
  text-decoration: underline;
}

/* ── Year range ── */
.create-drive__year-range {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.create-drive__year-range .create-drive__select {
  flex: 1;
}

.create-drive__year-sep {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  white-space: nowrap;
}

/* ── Actions ── */
.create-drive__form-error {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background-color: var(--color-danger-light);
  border: var(--border-width) solid var(--color-danger);
  border-radius: var(--border-radius-md);
  color: var(--color-danger-dark);
  font-size: var(--font-size-sm);
}

.create-drive__actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding-top: var(--space-2);
  border-top: var(--border-width) solid var(--border-color);
}

/* ── Responsive ── */
@media (max-width: 640px) {
  .create-drive__grid {
    grid-template-columns: 1fr;
  }

  .create-drive__field--full {
    grid-column: 1;
  }

  .create-drive__year-range {
    flex-direction: column;
    align-items: stretch;
  }

  .create-drive__year-sep {
    text-align: center;
  }
}
</style>
