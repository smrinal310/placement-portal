<template>
    <div class="dashboard">
        <AppSpinner v-if="adminStore.loading && !adminStore.stats" :fullPage="true" />

        <AppEmptyState
            v-else-if="adminStore.error"
            icon="bi bi-exclamation-circle"
            title="Failed to load dashboard"
            :subtitle="adminStore.error"
            actionLabel="Retry"
            @action="adminStore.fetchDashboard()"
        />

        <template v-else>
            <header class="dashboard__header">
                <div class="dashboard__header-info">
                    <h1 class="dashboard__title">Dashboard Overview</h1>
                    <p class="dashboard__subtitle">Welcome back, here's what's happening with placements today.</p>
                </div>
                <div class="dashboard__header-actions">
                    <AppButton variant="outline" iconLeft="bi bi-download" @click="handleExport">Export Report</AppButton>
                    <AppButton variant="primary" iconLeft="bi bi-plus-lg" @click="router.push('/admin/drives')">New Drive</AppButton>
                </div>
            </header>

            <section class="dashboard__stats-grid">
                <StatCard label="Total Students" :value="adminStore.stats?.total_students ?? 0" trend="+12%"
                    trendVariant="success" subLabel="vs last month" />
                <StatCard label="Total Companies" :value="adminStore.stats?.companies?.total ?? 0" trend="+5"
                    trendVariant="success" subLabel="new this week" />
                <StatCard label="Active Drives" :value="adminStore.stats?.drives?.approved ?? 0"
                    subLabel="Updated 2 hours ago" />
                <StatCard label="Pending Approvals" :value="adminStore.stats?.companies?.pending ?? 0"
                    actionBadge="Action needed" subLabel="Requires attention" />
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
                                    <td>{{ placement.student_name }}</td>
                                    <td>{{ placement.company_name }}</td>
                                    <td>{{ placement.job_title }}</td>
                                    <td class="dashboard__package">{{ placement.salary_package }}</td>
                                    <td>{{ formatDate(placement.created_at, { style: 'short' }) }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="card dashboard__activity">
                    <h2 class="dashboard__card-title dashboard__activity-title">Recent Activity</h2>
                    <div v-if="adminStore.recentActivity.length" class="dashboard__activity-feed">
                        <div v-for="(activity, index) in adminStore.recentActivity" :key="index" class="dashboard__activity-item">
                            <div class="dashboard__activity-row">
                                <span class="dashboard__activity-actor">{{ activity.actor }}</span>
                                <span class="dashboard__activity-time">{{ formatDate(activity.timestamp, { style: 'relative' }) }}</span>
                            </div>
                            <p class="dashboard__activity-desc">{{ activity.description }}</p>
                        </div>
                    </div>
                    <AppEmptyState
                        v-else-if="!adminStore.loading"
                        title="No recent activity"
                        subtitle="Activity stream will appear here."
                    />
                    <div class="dashboard__activity-footer">
                        <AppButton variant="ghost" @click="router.push('/admin/applications')">View All Activity</AppButton>
                    </div>
                </div>
            </section>
        </template>
    </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { formatDate } from '@/utils/formatters'

import AppButton from '@/components/common/AppButton.vue'
import AppSpinner from '@/components/common/AppSpinner.vue'
import AppEmptyState from '@/components/common/AppEmptyState.vue'
import StatCard from '@/components/admin/StatCard.vue'
import QuickActionCard from '@/components/admin/QuickActionCard.vue'

const router = useRouter()
const adminStore = useAdminStore()

onMounted(() => {
    adminStore.fetchDashboard()
})

const handleExport = () => {
    console.log('TODO: Export Report')
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
    grid-template-columns: 2fr 1fr;
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

.dashboard__activity {
    display: flex;
    flex-direction: column;
}

.dashboard__activity-title {
    margin-bottom: var(--space-4);
}

.dashboard__activity-feed {
    flex: 1;
}

.dashboard__activity-item {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
    padding-block: var(--space-3);
    border-bottom: var(--border-width) solid var(--border-color);
}

.dashboard__activity-item:last-child {
    border-bottom: none;
}

.dashboard__activity-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.dashboard__activity-actor {
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
    font-size: var(--font-size-sm);
}

.dashboard__activity-time {
    color: var(--color-text-muted);
    font-size: var(--font-size-xs);
}

.dashboard__activity-desc {
    color: var(--color-text-secondary);
    font-size: var(--font-size-sm);
    margin: 0;
}

.dashboard__activity-footer {
    margin-top: var(--space-4);
    display: flex;
    justify-content: center;
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
