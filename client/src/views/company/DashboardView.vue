<template>
  <div class="company-dashboard">
    <AppSpinner v-if="companyStore.loading && !companyStore.dashboard" :fullPage="true" />

    <AppEmptyState
      v-else-if="companyStore.error"
      icon="bi bi-exclamation-circle"
      title="Failed to load dashboard"
      :subtitle="companyStore.error"
      actionLabel="Retry"
      @action="companyStore.fetchDashboard()"
    />

    <!-- Pending Approval State -->
    <template v-else-if="companyStore.approvalStatus && companyStore.approvalStatus !== ApprovalStatus.APPROVED">
      <div class="company-dashboard__pending">
        <div class="card company-dashboard__pending-card">
          <i class="bi bi-hourglass-split company-dashboard__pending-icon"></i>
          <h2 class="company-dashboard__pending-title">Account Pending Approval</h2>
          <p class="company-dashboard__pending-desc">
            Your company registration is under review. You'll be able to post drives and
            manage candidates once an admin approves your account.
          </p>
          <AppButton variant="outline" iconLeft="bi bi-building" @click="router.push('/company/profile')">
            View Company Profile
          </AppButton>
        </div>
      </div>
    </template>

    <!-- Approved Company Dashboard -->
    <template v-else-if="companyStore.dashboard">

      <!-- Company Hero Banner -->
      <div class="company-dashboard__hero card">
        <div class="company-dashboard__hero-banner"></div>
        <div class="company-dashboard__hero-body">
          <div class="company-dashboard__hero-avatar">
            <img
              v-if="companyStore.companyLogo"
              :src="apiBase + '/static/uploads/logos/' + companyStore.companyLogo"
              :alt="companyStore.companyName"
              class="company-dashboard__hero-logo"
            />
            <AppAvatar v-else :name="companyStore.companyName || authStore.user?.name" size="lg" />
          </div>
          <div class="company-dashboard__hero-content">
            <div class="company-dashboard__hero-left">
              <div class="company-dashboard__hero-name-row">
                <span class="company-dashboard__hero-name">{{ companyStore.companyName || authStore.user?.name }}</span>
                <span class="company-dashboard__hero-verified">
                  <i class="bi bi-patch-check-fill"></i>
                  Approved Account
                </span>
              </div>
              <p class="company-dashboard__hero-desc">
                {{ companyStore.companyDescription || 'No company description provided.' }}
              </p>
            </div>
            <div class="company-dashboard__hero-actions">
              <AppButton variant="outline" @click="router.push('/company/profile/edit')">Edit Profile</AppButton>
              <AppButton variant="primary" iconLeft="bi bi-box-arrow-up-right" @click="router.push('/company/profile')">
                View Public Page
              </AppButton>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Row -->
      <section class="company-dashboard__stats-grid">
        <StatCard
          label="Active Drives"
          :value="companyStore.activeDrives.length"
          subLabel="Currently open for applications"
        />
        <StatCard
          label="Total Applications"
          :value="companyStore.totalApplications"
          subLabel="Across all drives"
        />
        <StatCard
          label="Total Shortlisted"
          :value="companyStore.totalShortlisted"
          subLabel="Candidates shortlisted"
        />
      </section>

      <!-- My Drives Section -->
      <section class="company-dashboard__drives-section">
        <div class="company-dashboard__drives-header">
          <div>
            <h2 class="company-dashboard__drives-title">My Placement Drives</h2>
            <p class="company-dashboard__drives-subtitle">
              Manage your active and past recruitment drives.
            </p>
          </div>
          <AppButton
            variant="primary"
            iconLeft="bi bi-plus-lg"
            @click="router.push('/company/drives/create')"
          >
            Create New Drive
          </AppButton>
        </div>

        <AppSpinner v-if="companyStore.loading" />

        <AppEmptyState
          v-else-if="!companyStore.drives.length"
          icon="bi bi-briefcase"
          title="No drives yet"
          subtitle="Create your first placement drive to start receiving applications."
          actionLabel="Create Drive"
          @action="router.push('/company/drives/create')"
        />

        <template v-else>
          <div class="company-dashboard__drives-grid">
            <CompanyDriveCard
              v-for="drive in companyStore.drives"
              :key="drive.drive_id"
              :drive="drive"
              @view="navigateToDrive(drive)"
              @edit="navigateToEdit(drive)"
              @delete="handleDelete(drive)"
            />
          </div>

        </template>
      </section>

    </template>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCompanyStore } from '@/stores/company'
import { useAuthStore } from '@/stores/auth'
import { ApprovalStatus } from '@/utils/constants'

import AppSpinner from '@/components/common/AppSpinner.vue'
import AppEmptyState from '@/components/common/AppEmptyState.vue'
import AppButton from '@/components/common/AppButton.vue'
import AppAvatar from '@/components/common/AppAvatar.vue'
import StatCard from '@/components/admin/StatCard.vue'
import CompanyDriveCard from '@/components/company/CompanyDriveCard.vue'

const router = useRouter()
const companyStore = useCompanyStore()
const authStore = useAuthStore()

const apiBase = import.meta.env.VITE_API_BASE_URL || ''

const navigateToDrive = (drive) => {
  router.push(`/company/drives/${drive.drive_id}/applications`)
}

const navigateToEdit = (drive) => {
  router.push(`/company/drives/${drive.drive_id}/edit`)
}

const handleDelete = (drive) => {
  // TODO: implement delete confirmation modal when drive delete endpoint is added
  console.log('Delete drive:', drive.drive_id)
}

onMounted(() => {
  companyStore.fetchDashboard()
})
</script>

<style scoped>
.company-dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

/* ── Pending State ── */
.company-dashboard__pending {
  display: flex;
  justify-content: center;
  padding-top: var(--space-12);
}

.company-dashboard__pending-card {
  max-width: 480px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
}

.company-dashboard__pending-icon {
  font-size: 3rem;
  color: var(--color-warning);
}

.company-dashboard__pending-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.company-dashboard__pending-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
  line-height: var(--line-height-base);
}

/* ── Hero Banner ── */
.company-dashboard__hero {
  overflow: hidden;
  padding: 0;
}

.company-dashboard__hero-banner {
  height: 100px;
  background: linear-gradient(135deg, #1e3a5f 0%, #2d5986 50%, #1a4a7a 100%);
}

.company-dashboard__hero-body {
  padding: 0 var(--space-6) var(--space-6);
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
}

.company-dashboard__hero-avatar {
  flex-shrink: 0;
  width: 72px;
  height: 72px;
  border-radius: var(--border-radius-lg);
  background-color: var(--color-white);
  border: 3px solid var(--color-white);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: -36px;
}

.company-dashboard__hero-logo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.company-dashboard__hero-content {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--space-4);
  padding-top: var(--space-4);
}

.company-dashboard__hero-left {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  min-width: 0;
}

.company-dashboard__hero-name-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.company-dashboard__hero-name {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.company-dashboard__hero-verified {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  background-color: var(--color-success-light);
  color: var(--color-success);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  padding-block: var(--space-1);
  padding-inline: var(--space-2);
  border-radius: var(--border-radius-pill);
}

.company-dashboard__hero-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
  max-width: 560px;
}

.company-dashboard__hero-actions {
  display: flex;
  gap: var(--space-3);
  align-items: center;
  flex-shrink: 0;
}

/* ── Stats Grid ── */
.company-dashboard__stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
}

/* ── Drives Section ── */
.company-dashboard__drives-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.company-dashboard__drives-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: var(--space-4);
}

.company-dashboard__drives-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-1) 0;
}

.company-dashboard__drives-subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin: 0;
}

.company-dashboard__drives-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
}

@media (max-width: 900px) {
  .company-dashboard__drives-grid {
    grid-template-columns: 1fr;
  }

  .company-dashboard__stats-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 600px) {
  .company-dashboard__stats-grid {
    grid-template-columns: 1fr;
  }

  .company-dashboard__hero-body {
    flex-direction: column;
    align-items: flex-start;
  }

  .company-dashboard__hero-actions {
    width: 100%;
    flex-direction: column;
  }
}
</style>
