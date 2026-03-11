<template>
  <div class="auth-page">

    <!-- Left panel – branding -->
    <div class="auth-page__brand">
      <div class="auth-page__brand-inner">
        <h1 class="auth-page__brand-name">PlacementPortal</h1>
        <p class="auth-page__brand-tagline">
          Connecting students with their dream careers. Streamlined placement management for colleges, companies, and students.
        </p>
        <div class="auth-page__features">
          <div class="auth-page__feature"><i class="bi bi-check-circle-fill"></i> Browse & apply to live placement drives</div>
          <div class="auth-page__feature"><i class="bi bi-check-circle-fill"></i> Track your application status in real time</div>
          <div class="auth-page__feature"><i class="bi bi-check-circle-fill"></i> Companies manage hiring end-to-end</div>
        </div>
      </div>
    </div>

    <!-- Right panel – form -->
    <div class="auth-page__form-panel">
      <div class="auth-page__card">

        <!-- Tab switcher -->
        <div class="auth-tabs">
          <button
            class="auth-tab"
            :class="{ 'auth-tab--active': activeTab === 'login' }"
            @click="setTab('login')"
          >Sign In</button>
          <button
            class="auth-tab"
            :class="{ 'auth-tab--active': activeTab === 'student' }"
            @click="setTab('student')"
          >Student Register</button>
          <button
            class="auth-tab"
            :class="{ 'auth-tab--active': activeTab === 'company' }"
            @click="setTab('company')"
          >Company Register</button>
        </div>

        <!-- Error / success banner -->
        <Transition name="banner">
          <div v-if="banner.message" class="auth-banner" :class="`auth-banner--${banner.type}`">
            <i :class="banner.type === 'error' ? 'bi bi-exclamation-circle-fill' : 'bi bi-check-circle-fill'"></i>
            {{ banner.message }}
          </div>
        </Transition>

        <!-- ── Login ── -->
        <form v-if="activeTab === 'login'" class="auth-form" @submit.prevent="handleLogin">
          <div class="auth-form__header">
            <h2 class="auth-form__title">Welcome back</h2>
            <p class="auth-form__subtitle">Sign in to your account to continue.</p>
          </div>

          <div class="auth-field">
            <label class="auth-label">Email Address</label>
            <input class="auth-input" type="email" v-model="login.email" placeholder="ramesh@prasad.com" required autocomplete="email" />
          </div>
          <div class="auth-field">
            <label class="auth-label">Password</label>
            <div class="auth-input-wrap">
              <input class="auth-input" :type="login.showPwd ? 'text' : 'password'" v-model="login.password" placeholder="••••••••" required autocomplete="current-password" />
              <button type="button" class="auth-eye" @click="login.showPwd = !login.showPwd" tabindex="-1">
                <i :class="login.showPwd ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
              </button>
            </div>
          </div>

          <button class="auth-submit" type="submit" :disabled="submitting">
            <span v-if="submitting" class="auth-submit__spinner"></span>
            {{ submitting ? 'Signing in…' : 'Sign In' }}
          </button>

          <p class="auth-switch">New student? <button type="button" class="auth-switch__link" @click="setTab('student')">Create an account</button></p>
        </form>

        <!-- ── Student Register ── -->
        <form v-else-if="activeTab === 'student'" class="auth-form" @submit.prevent="handleStudentRegister">
          <div class="auth-form__header">
            <h2 class="auth-form__title">Student Registration</h2>
            <p class="auth-form__subtitle">Create your account to start applying to drives.</p>
          </div>

          <div class="auth-grid">
            <div class="auth-field auth-field--full">
              <label class="auth-label">Full Name <span class="auth-required">*</span></label>
              <input class="auth-input" type="text" v-model="student.full_name" placeholder="Ram Kumar" required />
            </div>
            <div class="auth-field auth-field--full">
              <label class="auth-label">Email Address <span class="auth-required">*</span></label>
              <input class="auth-input" type="email" v-model="student.email" placeholder="ramesh@prasad.com" required autocomplete="email" />
            </div>
            <div class="auth-field auth-field--full">
              <label class="auth-label">Password <span class="auth-required">*</span></label>
              <div class="auth-input-wrap">
                <input class="auth-input" :type="student.showPwd ? 'text' : 'password'" v-model="student.password" placeholder="Min 8 characters" required autocomplete="new-password" />
                <button type="button" class="auth-eye" @click="student.showPwd = !student.showPwd" tabindex="-1">
                  <i :class="student.showPwd ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                </button>
              </div>
            </div>
            <div class="auth-field">
              <label class="auth-label">Branch <span class="auth-required">*</span></label>
              <select class="auth-input auth-select" v-model="student.branch" required>
                <option value="">Select branch</option>
                <option v-for="b in BRANCH_LIST" :key="b" :value="b">{{ b }}</option>
              </select>
            </div>
            <div class="auth-field">
              <label class="auth-label">Year of Study <span class="auth-required">*</span></label>
              <select class="auth-input auth-select" v-model.number="student.year" required>
                <option value="">Select year</option>
                <option :value="1">1st Year</option>
                <option :value="2">2nd Year</option>
                <option :value="3">3rd Year</option>
                <option :value="4">4th Year</option>
              </select>
            </div>
            <div class="auth-field">
              <label class="auth-label">CGPA (0–10) <span class="auth-required">*</span></label>
              <input class="auth-input" type="number" v-model.number="student.cgpa" step="0.01" min="0" max="10" placeholder="e.g. 8.5" required />
            </div>
            <div class="auth-field">
              <label class="auth-label">Phone Number <span class="auth-required">*</span></label>
              <input class="auth-input" type="tel" v-model="student.phone" placeholder="99121 47714" required />
            </div>
          </div>

          <button class="auth-submit" type="submit" :disabled="submitting">
            <span v-if="submitting" class="auth-submit__spinner"></span>
            {{ submitting ? 'Creating account…' : 'Create Account' }}
          </button>

          <p class="auth-switch">Already have an account? <button type="button" class="auth-switch__link" @click="setTab('login')">Sign in</button></p>
        </form>

        <!-- ── Company Register ── -->
        <form v-else-if="activeTab === 'company'" class="auth-form" @submit.prevent="handleCompanyRegister">
          <div class="auth-form__header">
            <h2 class="auth-form__title">Company Registration</h2>
            <p class="auth-form__subtitle">Register your company to post placement drives. Admin approval required.</p>
          </div>

          <div class="auth-grid">
            <div class="auth-field auth-field--full">
              <label class="auth-label">Company Name <span class="auth-required">*</span></label>
              <input class="auth-input" type="text" v-model="company.company_name" placeholder="Prime Mart" required />
            </div>
            <div class="auth-field auth-field--full">
              <label class="auth-label">Work Email <span class="auth-required">*</span></label>
              <input class="auth-input" type="email" v-model="company.email" placeholder="prime@mart.com" required autocomplete="email" />
            </div>
            <div class="auth-field auth-field--full">
              <label class="auth-label">Password <span class="auth-required">*</span></label>
              <div class="auth-input-wrap">
                <input class="auth-input" :type="company.showPwd ? 'text' : 'password'" v-model="company.password" placeholder="Min 8 characters" required autocomplete="new-password" />
                <button type="button" class="auth-eye" @click="company.showPwd = !company.showPwd" tabindex="-1">
                  <i :class="company.showPwd ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                </button>
              </div>
            </div>
            <div class="auth-field">
              <label class="auth-label">HR Name <span class="auth-required">*</span></label>
              <input class="auth-input" type="text" v-model="company.hr_name" placeholder="Venkat" required />
            </div>
            <div class="auth-field">
              <label class="auth-label">HR Contact <span class="auth-required">*</span></label>
              <input class="auth-input" type="tel" v-model="company.hr_contact" placeholder="99121 47714" required />
            </div>
            <div class="auth-field">
              <label class="auth-label">Industry</label>
              <input class="auth-input" type="text" v-model="company.industry" placeholder="e.g. Retail" />
            </div>
            <div class="auth-field">
              <label class="auth-label">Website</label>
              <input class="auth-input" type="url" v-model="company.website" placeholder="https://prime-mart.com" />
            </div>
          </div>

          <button class="auth-submit" type="submit" :disabled="submitting">
            <span v-if="submitting" class="auth-submit__spinner"></span>
            {{ submitting ? 'Submitting…' : 'Submit Registration' }}
          </button>

          <p class="auth-switch">Already registered? <button type="button" class="auth-switch__link" @click="setTab('login')">Sign in</button></p>
        </form>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { registerStudent, registerCompany } from '@/api/auth'
import { BRANCH_LIST } from '@/utils/constants'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Determine initial tab from route
const initialTab = route.path.includes('company') ? 'company' : route.path.includes('student') ? 'student' : 'login'
const activeTab = ref(initialTab)
const submitting = ref(false)
const banner = reactive({ message: '', type: 'error' })

let bannerTimer = null
function showBanner(message, type = 'error') {
  banner.message = message
  banner.type = type
  clearTimeout(bannerTimer)
  if (type !== 'success') return
  bannerTimer = setTimeout(() => { banner.message = '' }, 4000)
}

function setTab(tab) {
  activeTab.value = tab
  banner.message = ''
}

// ── Login state ──
const login = reactive({ email: '', password: '', showPwd: false })

async function handleLogin() {
  submitting.value = true
  banner.message = ''
  try {
    await authStore.login(login.email, login.password)
    if (authStore.isAdmin) router.push('/admin/dashboard')
    else if (authStore.isCompany) router.push('/company/dashboard')
    else if (authStore.isStudent) router.push('/student/dashboard')
  } catch {
    showBanner(authStore.error || 'Invalid email or password.')
  } finally {
    submitting.value = false
  }
}

// ── Student register state ──
const student = reactive({ full_name: '', email: '', password: '', branch: '', year: '', cgpa: '', phone: '', showPwd: false })

async function handleStudentRegister() {
  submitting.value = true
  banner.message = ''
  try {
    await registerStudent({
      full_name: student.full_name,
      email: student.email,
      password: student.password,
      branch: student.branch,
      year: student.year,
      cgpa: student.cgpa,
      phone: student.phone,
    })
    showBanner('Account created! You can now sign in.', 'success')
    Object.assign(student, { full_name: '', email: '', password: '', branch: '', year: '', cgpa: '', phone: '', showPwd: false })
    setTimeout(() => setTab('login'), 1800)
  } catch (e) {
    showBanner(e.message || 'Registration failed. Please try again.')
  } finally {
    submitting.value = false
  }
}

// ── Company register state ──
const company = reactive({ company_name: '', email: '', password: '', hr_name: '', hr_contact: '', industry: '', website: '', showPwd: false })

async function handleCompanyRegister() {
  submitting.value = true
  banner.message = ''
  try {
    await registerCompany({
      company_name: company.company_name,
      email: company.email,
      password: company.password,
      hr_name: company.hr_name,
      hr_contact: company.hr_contact,
      industry: company.industry || undefined,
      website: company.website || undefined,
    })
    showBanner('Registration submitted! Awaiting admin approval. You can sign in once approved.', 'success')
    Object.assign(company, { company_name: '', email: '', password: '', hr_name: '', hr_contact: '', industry: '', website: '', showPwd: false })
  } catch (e) {
    showBanner(e.message || 'Registration failed. Please try again.')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
/* ── Page layout ── */
.auth-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
}

/* ── Left brand panel ── */
.auth-page__brand {
  background: linear-gradient(145deg, var(--color-primary) 0%, #1e40af 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
}

.auth-page__brand-inner {
  max-width: 420px;
  color: var(--color-white);
}

.auth-page__logo {
  width: 56px;
  height: 56px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: var(--border-radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin-bottom: var(--space-6);
}

.auth-page__brand-name {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  margin: 0 0 var(--space-4);
  color: var(--color-white);
}

.auth-page__brand-tagline {
  font-size: var(--font-size-md);
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  margin: 0 0 var(--space-8);
}

.auth-page__features {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.auth-page__feature {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--font-size-sm);
  color: rgba(255, 255, 255, 0.9);
}

.auth-page__feature i {
  color: #86efac;
  font-size: var(--font-size-base);
  flex-shrink: 0;
}

/* ── Right form panel ── */
.auth-page__form-panel {
  background-color: var(--color-gray-50);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-8);
  overflow-y: auto;
}

.auth-page__card {
  width: 100%;
  max-width: 480px;
  background: var(--color-white);
  border-radius: var(--border-radius-xl);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

/* ── Tabs ── */
.auth-tabs {
  display: flex;
  border-bottom: 1px solid var(--color-border);
}

.auth-tab {
  flex: 1;
  padding: var(--space-4) var(--space-2);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-muted);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-bottom: -1px;
}

.auth-tab:hover { color: var(--color-primary); }

.auth-tab--active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

/* ── Banner ── */
.auth-banner {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-5);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.auth-banner--error {
  background-color: var(--color-danger-light);
  color: var(--color-danger);
}

.auth-banner--success {
  background-color: var(--color-success-light);
  color: var(--color-success);
}

.banner-enter-active, .banner-leave-active { transition: all 0.2s ease; }
.banner-enter-from, .banner-leave-to { opacity: 0; transform: translateY(-6px); }

/* ── Form ── */
.auth-form {
  padding: var(--space-6) var(--space-8);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.auth-form__header {
  margin-bottom: var(--space-2);
}

.auth-form__title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-1);
}

.auth-form__subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin: 0;
}

/* ── Fields ── */
.auth-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
}

.auth-field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.auth-field--full {
  grid-column: 1 / -1;
}

.auth-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-secondary);
}

.auth-required { color: var(--color-danger); }

.auth-input-wrap {
  position: relative;
}

.auth-input {
  width: 100%;
  padding: var(--space-3) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  background: var(--color-white);
  outline: none;
  box-sizing: border-box;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.auth-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.auth-input-wrap .auth-input {
  padding-right: 40px;
}

.auth-select { cursor: pointer; appearance: auto; }

.auth-eye {
  position: absolute;
  right: var(--space-3);
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
}

.auth-eye:hover { color: var(--color-primary); }

/* ── Submit button ── */
.auth-submit {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  width: 100%;
  padding: var(--space-3) var(--space-4);
  background-color: var(--color-primary);
  color: var(--color-white);
  border: none;
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: background-color var(--transition-fast);
  margin-top: var(--space-2);
}

.auth-submit:hover:not(:disabled) { background-color: var(--color-primary-hover); }
.auth-submit:disabled { opacity: var(--opacity-disabled); cursor: not-allowed; }

.auth-submit__spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: white;
  border-radius: 50%;
  animation: spin var(--spinner-speed) linear infinite;
  flex-shrink: 0;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ── Switch link ── */
.auth-switch {
  text-align: center;
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin: 0;
}

.auth-switch__link {
  background: none;
  border: none;
  color: var(--color-primary);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  padding: 0;
  font-size: inherit;
}

.auth-switch__link:hover { text-decoration: underline; }

/* ── Responsive ── */
@media (max-width: 768px) {
  .auth-page {
    grid-template-columns: 1fr;
  }

  .auth-page__brand {
    display: none;
  }

  .auth-page__form-panel {
    padding: var(--space-4);
    align-items: flex-start;
    padding-top: var(--space-8);
  }

  .auth-grid {
    grid-template-columns: 1fr;
  }

  .auth-form {
    padding: var(--space-5) var(--space-5);
  }
}
</style>
