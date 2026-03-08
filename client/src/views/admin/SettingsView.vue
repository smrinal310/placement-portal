<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { validatePassword, validateConfirmPassword } from '@/utils/validators'
import AppButton from '@/components/common/AppButton.vue'
import AppToggle from '@/components/common/AppToggle.vue'

const authStore = useAuthStore()

const form = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const formErrors = reactive({
  newPassword: '',
  confirmPassword: ''
})

const preferences = reactive({
  newCompanyRegistrations: true,
  applicationDigest: false
})

const saving = ref(false)
const saveSuccess = ref(false)

function loadPreferences() {
  const saved = localStorage.getItem('admin_preferences')
  if (saved) {
    try {
      Object.assign(preferences, JSON.parse(saved))
    } catch {
      // ignore malformed data
    }
  }
}

onMounted(loadPreferences)

function validatePasswordFields() {
  const pwResult = validatePassword(form.newPassword)
  const confirmResult = validateConfirmPassword(form.newPassword, form.confirmPassword)
  formErrors.newPassword = pwResult.valid ? '' : pwResult.message
  formErrors.confirmPassword = confirmResult.valid ? '' : confirmResult.message
  return pwResult.valid && confirmResult.valid
}

function handleBlurNewPassword() {
  if (form.newPassword) {
    const result = validatePassword(form.newPassword)
    formErrors.newPassword = result.valid ? '' : result.message
  }
}

function handleBlurConfirmPassword() {
  if (form.confirmPassword) {
    const result = validateConfirmPassword(form.newPassword, form.confirmPassword)
    formErrors.confirmPassword = result.valid ? '' : result.message
  }
}

function handleCancel() {
  form.currentPassword = ''
  form.newPassword = ''
  form.confirmPassword = ''
  formErrors.newPassword = ''
  formErrors.confirmPassword = ''
  loadPreferences()
}

async function handleSave() {
  saving.value = true

  if (form.newPassword) {
    const valid = validatePasswordFields()
    if (!valid) {
      saving.value = false
      return
    }
  }

  localStorage.setItem('admin_preferences', JSON.stringify(preferences))

  if (form.newPassword) {
    console.log('TODO: POST /api/admin/settings not implemented yet')
  }

  saveSuccess.value = true
  form.currentPassword = ''
  form.newPassword = ''
  form.confirmPassword = ''
  setTimeout(() => { saveSuccess.value = false }, 3000)
  saving.value = false
}
</script>

<template>
  <div class="settings">
    <div class="settings__header">
      <div>
        <h1 class="settings__title">Settings</h1>
        <p class="settings__subtitle">Manage your admin profile, security settings, and system preferences.</p>
      </div>
    </div>

    <div class="settings__sections">
      <section class="settings__section card">
        <h2 class="settings__section-title">Profile Information</h2>
        <div class="settings__profile-grid">
          <div class="settings__field-group">
            <label class="settings__label">Admin Name</label>
            <div class="settings__field-display">
              <i class="bi bi-person settings__field-icon"></i>
              <span>{{ authStore.user?.name || '—' }}</span>
            </div>
          </div>

          <div class="settings__field-group">
            <label class="settings__label">Email Address</label>
            <div class="settings__field-display">
              <i class="bi bi-envelope settings__field-icon"></i>
              <span>{{ authStore.user?.email || '—' }}</span>
            </div>
          </div>

          <div class="settings__field-group settings__field-group--full">
            <label class="settings__label">Role</label>
            <div class="settings__field-display">
              <i class="bi bi-briefcase settings__field-icon"></i>
              <span>Super Administrator</span>
            </div>
          </div>
        </div>
      </section>

      <section class="settings__section card">
        <div class="settings__section-header">
          <i class="bi bi-lock-fill settings__section-icon"></i>
          <h2 class="settings__section-title">Security</h2>
        </div>

        <div class="settings__form">
          <div class="settings__field-group">
            <label class="settings__label" for="currentPassword">Current Password</label>
            <input
              id="currentPassword"
              v-model="form.currentPassword"
              type="password"
              class="settings__input"
              placeholder="••••••••"
              autocomplete="current-password"
            />
          </div>

          <div class="settings__two-col">
            <div class="settings__field-group">
              <label class="settings__label" for="newPassword">New Password</label>
              <input
                id="newPassword"
                v-model="form.newPassword"
                type="password"
                class="settings__input"
                :class="{ 'settings__input--error': formErrors.newPassword }"
                placeholder="Enter new password"
                autocomplete="new-password"
                @blur="handleBlurNewPassword"
              />
              <span v-if="formErrors.newPassword" class="settings__field-error">
                {{ formErrors.newPassword }}
              </span>
            </div>

            <div class="settings__field-group">
              <label class="settings__label" for="confirmPassword">Confirm New Password</label>
              <input
                id="confirmPassword"
                v-model="form.confirmPassword"
                type="password"
                class="settings__input"
                :class="{ 'settings__input--error': formErrors.confirmPassword }"
                placeholder="Confirm new password"
                autocomplete="new-password"
                @blur="handleBlurConfirmPassword"
              />
              <span v-if="formErrors.confirmPassword" class="settings__field-error">
                {{ formErrors.confirmPassword }}
              </span>
            </div>
          </div>

          <p class="settings__hint">
            <i class="bi bi-info-circle settings__hint-icon"></i>
            Password must be at least 8 characters long and include a number.
          </p>
        </div>
      </section>

      <section class="settings__section card">
        <div class="settings__section-header">
          <i class="bi bi-sliders settings__section-icon"></i>
          <h2 class="settings__section-title">Portal Preferences</h2>
        </div>

        <div class="settings__prefs">
          <div class="settings__pref-row">
            <div class="settings__pref-text">
              <span class="settings__pref-label">New Company Registrations</span>
              <span class="settings__pref-desc">Receive email notifications when a new company registers.</span>
            </div>
            <AppToggle v-model="preferences.newCompanyRegistrations" />
          </div>

          <div class="settings__pref-row settings__pref-row--last">
            <div class="settings__pref-text">
              <span class="settings__pref-label">Student Application Digest</span>
              <span class="settings__pref-desc">Get a daily summary of new student applications.</span>
            </div>
            <AppToggle v-model="preferences.applicationDigest" />
          </div>
        </div>
      </section>
    </div>

    <Transition name="toast">
      <div v-if="saveSuccess" class="settings__success-bar">
        <i class="bi bi-check-circle-fill"></i>
        Settings saved successfully.
      </div>
    </Transition>

    <div class="settings__footer">
      <AppButton variant="outline" @click="handleCancel">Cancel</AppButton>
      <AppButton variant="primary" :loading="saving" @click="handleSave">Save Changes</AppButton>
    </div>
  </div>
</template>

<style scoped>
.settings {
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
  padding-bottom: 0;
}

.settings__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.settings__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-1) 0;
}

.settings__subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin: 0;
}

.settings__sections {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.settings__section {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.settings__section-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.settings__section-icon {
  color: var(--color-primary);
  font-size: var(--font-size-lg);
}

.settings__section-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.settings__profile-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.settings__field-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.settings__field-group--full {
  grid-column: 1 / -1;
}

.settings__label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.settings__field-display {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border: var(--border-width) solid var(--border-color);
  border-radius: var(--radius-md);
  background-color: var(--color-gray-50);
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
  cursor: default;
  min-height: 40px;
}

.settings__field-icon {
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.settings__form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.settings__two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.settings__input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  border: var(--border-width) solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-family: var(--font-family-base);
  color: var(--color-text-primary);
  background-color: var(--color-surface);
  outline: none;
  box-sizing: border-box;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.settings__input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.settings__input--error {
  border-color: var(--color-danger);
}

.settings__input--error:focus {
  box-shadow: 0 0 0 3px var(--color-danger-light);
}

.settings__field-error {
  color: var(--color-danger);
  font-size: var(--font-size-xs);
  margin-top: var(--space-1);
}

.settings__hint {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  margin: 0;
}

.settings__hint-icon {
  flex-shrink: 0;
}

.settings__prefs {
  display: flex;
  flex-direction: column;
}

.settings__pref-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) 0;
  border-bottom: var(--border-width) solid var(--border-color);
  gap: var(--space-4);
}

.settings__pref-row--last {
  border-bottom: none;
}

.settings__pref-text {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.settings__pref-label {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.settings__pref-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.settings__success-bar {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--content-padding);
  background-color: var(--color-success-light);
  color: var(--color-success);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  border-top: var(--border-width) solid var(--color-success);
}

.settings__footer {
  position: sticky;
  bottom: 0;
  background-color: var(--color-white);
  border-top: var(--border-width) solid var(--border-color);
  padding: var(--space-4) var(--content-padding);
  margin-top: var(--space-6);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  z-index: calc(var(--z-navbar) - 1);
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity var(--transition-normal), transform var(--transition-normal);
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(var(--space-2));
}

@media (max-width: 640px) {
  .settings__profile-grid,
  .settings__two-col {
    grid-template-columns: 1fr;
  }

  .settings__field-group--full {
    grid-column: 1;
  }
}
</style>
