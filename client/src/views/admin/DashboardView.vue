<template>
    <div class="dashboard">
        <AppSpinner v-if="adminStore.loading && !adminStore.stats" :fullPage="true" />

        <AppEmptyState v-else-if="adminStore.error" icon="bi bi-exclamation-circle" title="Failed to load dashboard"
            :subtitle="adminStore.error" actionLabel="Retry" @action="adminStore.fetchDashboard()" />

        <template v-else>
            <header class="dashboard__header">
                <div class="dashboard__header-info">
                    <h1 class="dashboard__title">Dashboard Overview</h1>
                    <p class="dashboard__subtitle">Welcome back, here's what's happening with placements today.</p>
                </div>
                <div class="dashboard__header-actions">
                    <AppButton variant="primary" iconLeft="bi bi-download" :loading="exportLoading"
                        @click="handleExport">Mail Report</AppButton>
                </div>
            </header>

            <Transition name="banner">
                <div v-if="exportMsg" class="dashboard__export-banner"
                    :class="exportMsgError ? 'dashboard__export-banner--error' : 'dashboard__export-banner--success'">
                    <i :class="exportMsgError ? 'bi bi-exclamation-circle' : 'bi bi-check-circle'"></i>
                    {{ exportMsg }}
                </div>
            </Transition>

            <section class="dashboard__stats-grid">
                <StatCard label="Total Students" :value="adminStore.stats?.total_students ?? 0" />
                <StatCard label="Total Companies" :value="adminStore.stats?.companies?.total ?? 0" />
                <StatCard label="Active Drives" :value="adminStore.stats?.drives?.approved ?? 0" />
                <StatCard label="Pending Approvals" :value="adminStore.stats?.companies?.pending ?? 0"/>
            </section>

            <section class="dashboard__actions-grid">
                <QuickActionCard title="Company Approvals" :pendingCount="adminStore.pendingCompaniesCount"
                    description="Review and approve new company registration requests." buttonLabel="Review Requests"
                    to="/admin/companies?status=pending" />
                <QuickActionCard title="Drive Approvals" :pendingCount="adminStore.pendingDrivesCount"
                    description="Approve upcoming placement drives and schedules." buttonLabel="Review Drives"
                    to="/admin/drives?status=pending" />
            </section>

            <section class="dashboard__bottom-grid">
                <div class="card">
                    <div class="card-header">
                        <h2 class="dashboard__card-title">Recent Placements</h2>
                        <AppButton variant="ghost" @click="router.push('/admin/applications')">View All</AppButton>
                    </div>

                    <AppSpinner v-if="adminStore.loading" />
                    <AppEmptyState v-else-if="!adminStore.recentPlacements || adminStore.recentPlacements.length === 0"
                        title="No recent placements" subtitle="Recent placement records will appear here." />
                    <div v-else class="dashboard__table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th>Student Name</th>
                                    <th>Company</th>
                                    <th>Role</th>
                                    <th>Package</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(placement, index) in adminStore.recentPlacements.slice(0, 5)" :key="index">
                                    <td>
                                        <div class="dashboard__name-cell">
                                            <AppAvatar :name="placement.student_name" size="sm" />
                                            <div>
                                                <router-link :to="`/admin/students/${placement.student_id}`"
                                                    class="table-link dashboard__name-link">{{ placement.student_name
                                                    }}</router-link>
                                                <div class="dashboard__name-sub">{{ placement.student_branch }}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td>
                                        <router-link :to="`/admin/companies/${placement.company_id}`"
                                            class="table-link">{{ placement.company_name }}</router-link>
                                    </td>
                                    <td>{{ placement.role }}</td>
                                    <td class="dashboard__package">{{ placement.package }}</td>
                                    <td>{{ formatDate(placement.date, { style: 'short' }) }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>
        </template>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { formatDate } from '@/utils/formatters'
import { generateReport } from '@/api/admin'

import AppButton from '@/components/common/AppButton.vue'
import AppSpinner from '@/components/common/AppSpinner.vue'
import AppEmptyState from '@/components/common/AppEmptyState.vue'
import AppAvatar from '@/components/common/AppAvatar.vue'
import StatCard from '@/components/admin/StatCard.vue'
import QuickActionCard from '@/components/admin/QuickActionCard.vue'

const router = useRouter()
const adminStore = useAdminStore()

onMounted(() => {
    adminStore.fetchDashboard()
})

const exportLoading = ref(false)
const exportMsg = ref('')
const exportMsgError = ref(false)
let exportMsgTimer = null

const handleExport = async () => {
    if (exportLoading.value) return
    exportLoading.value = true
    exportMsg.value = ''
    try {
        await generateReport()
        exportMsgError.value = false
        exportMsg.value = 'Report is being generated and will be emailed to you shortly.'
    } catch {
        exportMsgError.value = true
        exportMsg.value = 'Failed to trigger report generation.'
    } finally {
        exportLoading.value = false
        clearTimeout(exportMsgTimer)
        exportMsgTimer = setTimeout(() => { exportMsg.value = '' }, 5000)
    }
}
</script>

<style scoped>
.dashboard {
    display: flex;
    flex-direction: column;
    gap: var(--space-6);
}

.dashboard__header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: var(--space-4);
}

.dashboard__title {
    font-size: var(--font-size-2xl);
    font-weight: var(--font-weight-bold);
    color: var(--color-text-primary);
    margin-bottom: var(--space-1);
}

.dashboard__subtitle {
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
}

.dashboard__header-actions {
    display: flex;
    gap: var(--space-3);
    align-items: center;
}

.dashboard__export-banner {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3) var(--space-4);
    border-radius: var(--border-radius-md);
    font-size: var(--font-size-sm);
}

.dashboard__export-banner--success {
    background-color: var(--color-success-light, #dcfce7);
    color: var(--color-success, #16a34a);
}

.dashboard__export-banner--error {
    background-color: var(--color-danger-light, #fee2e2);
    color: var(--color-danger, #dc2626);
}

.banner-enter-active,
.banner-leave-active {
    transition: opacity 0.3s, transform 0.3s;
}

.banner-enter-from,
.banner-leave-to {
    opacity: 0;
    transform: translateY(-6px);
}

.dashboard__stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: var(--space-4);
}

.dashboard__actions-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-4);
}

.dashboard__bottom-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: var(--space-4);
    align-items: start;
}

.dashboard__card-title {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-bold);
    color: var(--color-text-primary);
    margin: 0;
}

.dashboard__table-wrap {
    overflow-x: auto;
}

.dashboard__package {
    color: var(--color-primary);
    font-weight: var(--font-weight-bold);
}

.dashboard__name-cell {
    display: flex;
    align-items: center;
    gap: var(--space-2);
}

.dashboard__name-link {
    font-weight: var(--font-weight-medium);
}

.dashboard__name-sub {
    font-size: var(--font-size-xs);
    color: var(--color-text-secondary);
}

@media (max-width: 991px) {
    .dashboard__stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .dashboard__bottom-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 575px) {
    .dashboard__stats-grid {
        grid-template-columns: 1fr;
    }

    .dashboard__actions-grid {
        grid-template-columns: 1fr;
    }
}
</style>
