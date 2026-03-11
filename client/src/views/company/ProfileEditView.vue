<template>
  <div class="profile-edit">

    <Transition name="toast">
      <div v-if="toast.message" :class="['profile-edit__toast', `profile-edit__toast--${toast.type}`]">
        <i :class="toast.type === 'error' ? 'bi bi-x-circle-fill' : 'bi bi-check-circle-fill'"></i>
        {{ toast.message }}
      </div>
    </Transition>

    <div class="profile-edit__header">
      <div>
        <router-link to="/company/profile" class="profile-edit__back">
          <i class="bi bi-arrow-left"></i> Back to Profile
        </router-link>
        <h1 class="profile-edit__title">Edit Company Profile</h1>
        <p class="profile-edit__subtitle">Keep your company info up to date for students and admins.</p>
      </div>
    </div>

    <AppSpinner v-if="loading && !form.company_name" />

    <AppEmptyState
      v-else-if="fetchError"
      icon="bi bi-exclamation-circle"
      title="Failed to load profile"
      :subtitle="fetchError"
      actionLabel="Retry"
      @action="loadProfile"
    />

    <template v-else>
      <div class="profile-edit__layout">

        <!-- Left: Logo card -->
        <div class="profile-edit__sidebar">
          <div class="card profile-edit__logo-card">
            <h2 class="profile-edit__section-title">Company Logo</h2>

            <div class="profile-edit__logo-wrap">
              <img
                v-if="logoPreview || currentLogo"
                :src="logoPreview || (apiBase + '/static/uploads/logos/' + currentLogo)"
                alt="Company logo"
                class="profile-edit__logo-img"
              />
              <div v-else class="profile-edit__logo-placeholder">
                <i class="bi bi-building profile-edit__logo-placeholder-icon"></i>
              </div>
            </div>

            <input
              ref="logoInputRef"
              type="file"
              accept="image/png,image/jpeg,image/jpg,image/webp"
              class="profile-edit__file-input"
              @change="handleLogoSelect"
            />

            <AppButton
              variant="outline"
              iconLeft="bi bi-upload"
              :loading="logoUploading"
              class="profile-edit__logo-btn"
              @click="logoInputRef.click()"
            >
              {{ currentLogo || logoPreview ? 'Change Logo' : 'Upload Logo' }}
            </AppButton>
            <p class="profile-edit__logo-hint">PNG, JPG or WEBP · Max 2MB</p>
          </div>
        </div>

        <!-- Right: Form -->
        <div class="profile-edit__main">
          <form class="card profile-edit__form-card" @submit.prevent="handleSave">

            <h2 class="profile-edit__section-title">Company Details</h2>

            <div class="profile-edit__field">
              <label class="profile-edit__label">Company Name</label>
              <input
                type="text"
                class="profile-edit__input profile-edit__input--disabled"
                :value="form.company_name"
                disabled
                title="Company name cannot be changed. Contact admin if needed."
              />
              <span class="profile-edit__hint">Contact an admin to change the company name.</span>
            </div>

            <div class="profile-edit__field">
              <label class="profile-edit__label">Industry</label>
              <input
                type="text"
                class="profile-edit__input"
                v-model="form.industry"
                placeholder="e.g. Software, Finance, Manufacturing"
              />
            </div>

            <div class="profile-edit__field">
              <label class="profile-edit__label">Website</label>
              <input
                type="url"
                class="profile-edit__input"
                v-model="form.website"
                placeholder="https://yourcompany.com"
              />
            </div>

            <div class="profile-edit__field profile-edit__field--full">
              <label class="profile-edit__label">About the Company</label>
              <textarea
                class="profile-edit__textarea"
                v-model="form.description"
                rows="4"
                placeholder="Brief description of your company, what you do, your culture..."
              ></textarea>
            </div>

            <div class="profile-edit__field profile-edit__field--full">
              <label class="profile-edit__label">Office Address</label>
              <textarea
                class="profile-edit__textarea"
                v-model="form.address"
                rows="2"
                placeholder="Enter your office address"
              ></textarea>
            </div>

            <div class="profile-edit__divider"></div>
            <h2 class="profile-edit__section-title">HR / Contact Person</h2>

            <div class="profile-edit__field">
              <label class="profile-edit__label">HR Name</label>
              <input
                type="text"
                class="profile-edit__input"
                v-model="form.hr_name"
                placeholder="Full name of HR contact"
              />
            </div>

            <div class="profile-edit__field">
              <label class="profile-edit__label">HR Contact (Email or Phone)</label>
              <input
                type="text"
                class="profile-edit__input"
                v-model="form.hr_contact"
                placeholder="hr@company.com or +91 xxxxxxxxxx"
              />
            </div>

            <div v-if="formError" class="profile-edit__form-error">
              <i class="bi bi-exclamation-circle"></i> {{ formError }}
            </div>

            <div class="profile-edit__actions">
              <AppButton variant="outline" type="button" @click="router.push('/company/profile')">
                Cancel
              </AppButton>
              <AppButton variant="primary" type="submit" :loading="saving" iconLeft="bi bi-check-lg">
                Save Changes
              </AppButton>
            </div>

          </form>
        </div>

      </div>
    </template>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import * as companyApi from '@/api/company'

import AppButton from '@/components/common/AppButton.vue'
import AppSpinner from '@/components/common/AppSpinner.vue'
import AppEmptyState from '@/components/common/AppEmptyState.vue'

const router = useRouter()
const apiBase = import.meta.env.VITE_API_BASE_URL || ''

// ── State ──
const loading = ref(false)
const fetchError = ref('')
const saving = ref(false)
const formError = ref('')
const logoUploading = ref(false)
const logoInputRef = ref(null)
const currentLogo = ref('')
const logoPreview = ref('')
const toast = ref({ message: '', type: 'success' })
let toastTimer = null

const form = ref({
  company_name: '',
  industry: '',
  website: '',
  description: '',
  address: '',
  hr_name: '',
  hr_contact: '',
})

// ── Load ──
async function loadProfile() {
  loading.value = true
  fetchError.value = ''
  try {
    const res = await companyApi.getProfile()
    const d = res.data
    form.value = {
      company_name: d.company_name || '',
      industry: d.industry || '',
      website: d.website || '',
      description: d.description || '',
      address: d.address || '',
      hr_name: d.hr_name || '',
      hr_contact: d.hr_contact || '',
    }
    currentLogo.value = d.logo_filename || ''
  } catch (e) {
    fetchError.value = e.response?.data?.message || e.message || 'Failed to load profile.'
  } finally {
    loading.value = false
  }
}

onMounted(loadProfile)

// ── Save ──
async function handleSave() {
  formError.value = ''
  saving.value = true
  try {
    await companyApi.updateProfile({
      industry: form.value.industry,
      website: form.value.website,
      description: form.value.description,
      address: form.value.address,
      hr_name: form.value.hr_name,
      hr_contact: form.value.hr_contact,
    })
    showToast('Profile updated successfully.')
    setTimeout(() => router.push('/company/profile'), 1200)
  } catch (e) {
    formError.value = e.response?.data?.message || e.message || 'Failed to save changes.'
  } finally {
    saving.value = false
  }
}

// ── Logo ──
function handleLogoSelect(e) {
  const file = e.target.files?.[0]
  if (!file) return

  const MAX = 2 * 1024 * 1024
  if (file.size > MAX) {
    showToast('Logo must be under 2MB.', 'error')
    return
  }

  logoPreview.value = URL.createObjectURL(file)
  uploadLogo(file)
}

async function uploadLogo(file) {
  logoUploading.value = true
  try {
    await companyApi.uploadLogo(file)
    showToast('Logo updated successfully.')
    // Refresh to get new timestamped filename, then clear the blob preview
    const res = await companyApi.getProfile()
    currentLogo.value = res.data.logo_filename || ''
    // Now safe to drop the blob URL — the HTTP URL is unique (timestamped filename)
    logoPreview.value = ''
  } catch (e) {
    showToast(e.response?.data?.message || 'Logo upload failed.', 'error')
    logoPreview.value = ''
  } finally {
    logoUploading.value = false
    if (logoInputRef.value) logoInputRef.value.value = ''
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
.profile-edit {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  position: relative;
}

/* ── Toast ── */
.profile-edit__toast {
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

.profile-edit__toast--success {
  background-color: var(--color-success-light);
  color: var(--color-success);
  border: var(--border-width) solid var(--color-success);
}

.profile-edit__toast--error {
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
.profile-edit__back {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  text-decoration: none;
  margin-bottom: var(--space-2);
  transition: color var(--transition-fast);
}

.profile-edit__back:hover {
  color: var(--color-primary);
}

.profile-edit__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-1);
}

.profile-edit__subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* ── Layout ── */
.profile-edit__layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: var(--space-6);
  align-items: start;
}

/* ── Logo card ── */
.profile-edit__logo-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  text-align: center;
}

.profile-edit__logo-wrap {
  width: 120px;
  height: 120px;
  border-radius: var(--border-radius-xl);
  overflow: hidden;
  border: var(--border-width) solid var(--border-color);
  flex-shrink: 0;
}

.profile-edit__logo-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: var(--color-white);
}

.profile-edit__logo-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-gray-100);
}

.profile-edit__logo-placeholder-icon {
  font-size: 48px;
  color: var(--color-gray-400);
}

.profile-edit__file-input {
  display: none;
}

.profile-edit__logo-btn {
  width: 100%;
}

.profile-edit__logo-hint {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

/* ── Form card ── */
.profile-edit__form-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.profile-edit__section-title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.profile-edit__divider {
  border: none;
  border-top: var(--border-width) solid var(--border-color);
  margin-block: var(--space-1);
}

/* ── Fields ── */
.profile-edit__field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.profile-edit__label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.profile-edit__input {
  padding: var(--space-2) var(--space-3);
  border: var(--border-width) solid var(--border-color);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  background: var(--color-white);
  transition: border-color var(--transition-fast);
  outline: none;
  font-family: var(--font-family-base);
}

.profile-edit__input:focus {
  border-color: var(--color-primary);
}

.profile-edit__input--disabled {
  background: var(--color-gray-100);
  color: var(--color-text-muted);
  cursor: not-allowed;
}

.profile-edit__textarea {
  padding: var(--space-2) var(--space-3);
  border: var(--border-width) solid var(--border-color);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  background: var(--color-white);
  resize: vertical;
  min-height: 80px;
  font-family: var(--font-family-base);
  transition: border-color var(--transition-fast);
  outline: none;
}

.profile-edit__textarea:focus {
  border-color: var(--color-primary);
}

.profile-edit__hint {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

/* ── Form error ── */
.profile-edit__form-error {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-sm);
  color: var(--color-danger);
  background: var(--color-danger-light);
  border: var(--border-width) solid var(--color-danger);
  border-radius: var(--border-radius-md);
  padding: var(--space-2) var(--space-3);
}

/* ── Actions ── */
.profile-edit__actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding-top: var(--space-2);
  border-top: var(--border-width) solid var(--border-color);
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .profile-edit__layout {
    grid-template-columns: 1fr;
  }
}
</style>
