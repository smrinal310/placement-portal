<template>
  <div class="companies">
    <Transition name="toast">
      <div
        v-if="feedbackMessage"
        class="companies__toast"
        :class="feedbackType === 'error' ? 'companies__toast--error' : 'companies__toast--success'"
      >
        <i :class="feedbackType === 'error' ? 'bi bi-x-circle-fill' : 'bi bi-check-circle-fill'"></i>
        {{ feedbackMessage }}
      </div>
    </Transition>

    <header class="companies__header">
      <div>
        <h1 class="companies__title">Companies</h1>
        <p class="companies__subtitle">Manage registered companies and approval requests.</p>
      </div>
      <div class="companies__header-actions">
        <AppButton variant="outline" iconLeft="bi bi-download" @click="handleExport">Export</AppButton>
      </div>
    </header>

    <AppFilterBar v-model="searchQuery" placeholder="Search companies by name, industry...">
      <select class="filter-select" v-model="selectedStatus">
        <option value="">All Statuses</option>
        <option :value="ApprovalStatus.APPROVED">Approved</option>
        <option :value="ApprovalStatus.PENDING">Pending</option>
        <option :value="ApprovalStatus.REJECTED">Rejected</option>
      </select>
    </AppFilterBar>

    <div class="card companies__table-card">
      <AppSpinner v-if="adminStore.loading" />

      <AppEmptyState
        v-else-if="adminStore.error"
        icon="bi bi-exclamation-circle"
        title="Failed to load companies"
        :subtitle="adminStore.error"
        actionLabel="Retry"
        @action="loadCompanies"
      />

      <AppEmptyState
        v-else-if="!adminStore.companies.length"
        icon="bi bi-buildings"
        title="No companies found"
        subtitle="No companies match your current filters."
      />

      <template v-else>
        <div class="companies__table-wrap">
          <table>
            <thead>
              <tr>
                <th>Company Name</th>
                <th>Industry</th>
                <th>HR Contact</th>
                <th>Registered On</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="company in adminStore.companies" :key="company.id">
                <td>
                  <div class="companies__name-cell">
                    <AppAvatar :name="company.company_name" size="sm" />
                    <div>
                      <div class="companies__company-name">{{ company.company_name }}</div>
                      <div class="companies__company-email">{{ company.email }}</div>
                    </div>
                  </div>
                </td>
                <td>{{ company.industry || '—' }}</td>
                <td>
                  <div class="companies__hr-name">{{ company.hr_name }}</div>
                  <div class="companies__hr-contact">{{ company.hr_contact }}</div>
                </td>
                <td>{{ formatDate(company.created_at, { style: 'short' }) }}</td>
                <td>
                  <div class="companies__status-cell">
                    <AppBadge
                      v-if="company.account_status === AccountStatus.BLACKLISTED"
                      status="blacklisted"
                    />
                    <AppBadge v-else :status="company.approval_status" />
                  </div>
                </td>
                <td>
                  <div class="companies__actions">
                    <template v-if="company.approval_status === ApprovalStatus.PENDING">
                      <button
                        class="companies__action-btn companies__action-btn--success"
                        title="Approve"
                        @click="openModal('approve', company)"
                      >
                        <i class="bi bi-check-circle-fill"></i>
                      </button>
                      <button
                        class="companies__action-btn companies__action-btn--danger"
                        title="Reject"
                        @click="openModal('reject', company)"
                      >
                        <i class="bi bi-x-circle-fill"></i>
                      </button>
                      <button
                        class="companies__action-btn"
                        title="View"
                        @click="router.push('/admin/companies/' + company.id)"
                      >
                        <i class="bi bi-eye"></i>
                      </button>
                    </template>

                    <template v-else-if="company.approval_status === ApprovalStatus.APPROVED">
                      <button
                        class="companies__action-btn"
                        title="View"
                        @click="router.push('/admin/companies/' + company.id)"
                      >
                        <i class="bi bi-eye"></i>
                      </button>
                      <button
                        v-if="company.account_status !== AccountStatus.BLACKLISTED"
                        class="companies__action-btn companies__action-btn--danger"
                        title="Blacklist"
                        @click="openModal('blacklist', company)"
                      >
                        <i class="bi bi-slash-circle"></i>
                      </button>
                      <button
                        v-if="company.account_status === AccountStatus.BLACKLISTED"
                        class="companies__action-btn companies__action-btn--success"
                        title="Activate"
                        @click="openModal('activate', company)"
                      >
                        <i class="bi bi-check-circle"></i>
                      </button>
                    </template>

                    <template v-else-if="company.approval_status === ApprovalStatus.REJECTED">
                      <button
                        class="companies__action-btn"
                        title="View"
                        @click="router.push('/admin/companies/' + company.id)"
                      >
                        <i class="bi bi-eye"></i>
                      </button>
                    </template>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="companies__pagination">
          <AppPagination
            variant="text"
            :total="adminStore.companiesTotal"
            :perPage="10"
            :currentPage="adminStore.companyFilters.page"
            @page-change="(page) => adminStore.fetchCompanies({ page })"
          />
        </div>
      </template>
    </div>

    <AppModal
      :show="modalState.show && modalState.type === 'approve'"
      title="Approve Company Registration"
      headerIcon="bi bi-shield-check"
      confirmLabel="Confirm Approval"
      confirmVariant="primary"
      warningMessage="This company will be notified and can start posting placement drives immediately."
      :loading="adminStore.actionLoading"
      @confirm="handleApproveConfirm"
      @cancel="closeModal"
    >
      <div class="companies__modal-summary">
        <div class="companies__modal-grid">
          <div>
            <div class="companies__modal-label">Company Name</div>
            <div class="companies__modal-value">{{ modalState.company?.company_name }}</div>
          </div>
          <div>
            <div class="companies__modal-label">Industry</div>
            <div class="companies__modal-value">{{ modalState.company?.industry || '—' }}</div>
          </div>
        </div>
        <div class="companies__modal-hr">
          <AppAvatar :name="modalState.company?.hr_name || ''" size="sm" />
          <div>
            <div class="companies__modal-value">{{ modalState.company?.hr_name }}</div>
            <div class="companies__modal-label">{{ modalState.company?.email }}</div>
          </div>
        </div>
      </div>
    </AppModal>

    <AppModal
      :show="modalState.show && modalState.type === 'reject'"
      title="Reject Company Registration"
      headerIcon="bi bi-shield-x"
      confirmLabel="Confirm Rejection"
      confirmVariant="danger"
      warningMessage="The company will be notified of the rejection."
      :loading="adminStore.actionLoading"
      @confirm="handleRejectConfirm"
      @cancel="closeModal"
    >
      <div>
        <label class="companies__modal-label" for="reject-reason">Reason for rejection</label>
        <textarea
          id="reject-reason"
          class="companies__reject-textarea"
          v-model="modalState.reason"
          rows="3"
          placeholder="Provide a reason..."
        ></textarea>
        <p v-if="rejectError" class="companies__reject-error">{{ rejectError }}</p>
      </div>
    </AppModal>

    <AppModal
      :show="modalState.show && modalState.type === 'blacklist'"
      title="Blacklist Company"
      headerIcon="bi bi-slash-circle"
      confirmLabel="Confirm Blacklist"
      confirmVariant="danger"
      warningMessage="This company will be prevented from creating new drives. Existing drives remain unchanged."
      :loading="adminStore.actionLoading"
      @confirm="handleBlacklistConfirm"
      @cancel="closeModal"
    >
      <div class="companies__modal-summary">
        <div class="companies__modal-value">{{ modalState.company?.company_name }}</div>
        <div class="companies__modal-label">
          Current status:
          <AppBadge v-if="modalState.company" :status="modalState.company.approval_status" />
        </div>
      </div>
    </AppModal>

    <AppModal
      :show="modalState.show && modalState.type === 'activate'"
      title="Activate Company"
      headerIcon="bi bi-building-check"
      confirmLabel="Confirm Activation"
      confirmVariant="primary"
      warningMessage="This company will regain full access and can create new placement drives."
      :loading="adminStore.actionLoading"
      @confirm="handleActivateConfirm"
      @cancel="closeModal"
    >
      <div class="companies__modal-summary">
        <div class="companies__modal-grid">
          <div>
            <div class="companies__modal-label">Company Name</div>
            <div class="companies__modal-value">{{ modalState.company?.company_name }}</div>
          </div>
          <div>
            <div class="companies__modal-label">Industry</div>
            <div class="companies__modal-value">{{ modalState.company?.industry || '—' }}</div>
          </div>
        </div>
        <div class="companies__modal-hr">
          <AppAvatar :name="modalState.company?.hr_name || ''" size="sm" />
          <div>
            <div class="companies__modal-value">{{ modalState.company?.hr_name }}</div>
            <div class="companies__modal-label">{{ modalState.company?.email }}</div>
          </div>
        </div>
      </div>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { formatDate } from '@/utils/formatters'
import { ApprovalStatus, AccountStatus } from '@/utils/constants'

import AppButton from '@/components/common/AppButton.vue'
import AppFilterBar from '@/components/common/AppFilterBar.vue'
import AppBadge from '@/components/common/AppBadge.vue'
import AppAvatar from '@/components/common/AppAvatar.vue'
import AppSpinner from '@/components/common/AppSpinner.vue'
import AppEmptyState from '@/components/common/AppEmptyState.vue'
import AppPagination from '@/components/common/AppPagination.vue'
import AppModal from '@/components/common/AppModal.vue'

const router = useRouter()
const adminStore = useAdminStore()

const searchQuery = ref('')
const selectedStatus = ref('')
const feedbackMessage = ref('')
const feedbackType = ref('success')
const rejectError = ref('')

const modalState = reactive({
  show: false,
  type: null,
  company: null,
  reason: ''
})

let searchTimer = null
let feedbackTimer = null

const showFeedback = (message, type = 'success') => {
  feedbackMessage.value = message
  feedbackType.value = type
  clearTimeout(feedbackTimer)
  feedbackTimer = setTimeout(() => { feedbackMessage.value = '' }, 3000)
}

const loadCompanies = () => {
  adminStore.fetchCompanies({
    search: searchQuery.value,
    status: selectedStatus.value,
    page: 1
  })
}

const openModal = (type, company) => {
  modalState.type = type
  modalState.company = company
  modalState.reason = ''
  rejectError.value = ''
  modalState.show = true
}

const closeModal = () => {
  modalState.show = false
  setTimeout(() => {
    modalState.type = null
    modalState.company = null
    modalState.reason = ''
    rejectError.value = ''
  }, 300)
}

const handleApproveConfirm = async () => {
  try {
    await adminStore.approveCompany(modalState.company.id)
    closeModal()
    showFeedback('Company approved successfully.')
  } catch {
    showFeedback(adminStore.error || 'Failed to approve company.', 'error')
  }
}

const handleRejectConfirm = async () => {
  if (!modalState.reason.trim()) {
    rejectError.value = 'Please provide a reason for rejection.'
    return
  }
  try {
    await adminStore.rejectCompany(modalState.company.id, modalState.reason)
    closeModal()
    showFeedback('Company rejected.')
  } catch {
    showFeedback(adminStore.error || 'Failed to reject company.', 'error')
  }
}

const handleBlacklistConfirm = async () => {
  try {
    await adminStore.blacklistCompany(modalState.company.id)
    closeModal()
    showFeedback('Company blacklisted.')
  } catch {
    showFeedback(adminStore.error || 'Failed to blacklist company.', 'error')
  }
}

const handleActivateConfirm = async () => {
  try {
    await adminStore.activateCompany(modalState.company.id)
    closeModal()
    showFeedback('Company activated successfully.')
  } catch {
    showFeedback(adminStore.error || 'Failed to activate company.', 'error')
  }
}

const handleExport = () => { console.log('TODO: Export companies') }

watch(selectedStatus, () => {
  adminStore.fetchCompanies({ status: selectedStatus.value, search: searchQuery.value, page: 1 })
})

watch(searchQuery, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    adminStore.fetchCompanies({ search: searchQuery.value, status: selectedStatus.value, page: 1 })
  }, 300)
})

onMounted(() => {
  loadCompanies()
})
</script>

<style scoped>
.companies {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.companies__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: var(--space-4);
}

.companies__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-1);
}

.companies__subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.companies__header-actions {
  display: flex;
  gap: var(--space-3);
  align-items: center;
}

.companies__table-card {
  padding: 0;
  overflow: hidden;
}

.companies__table-wrap {
  overflow-x: auto;
}

.companies__pagination {
  padding: var(--space-4) var(--space-6);
  border-top: var(--border-width) solid var(--border-color);
}

.companies__name-cell {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.companies__company-name {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
}

.companies__company-email {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.companies__hr-name {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
}

.companies__hr-contact {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.companies__status-cell {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  align-items: flex-start;
}

.companies__actions {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.companies__action-btn {
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
}

.companies__action-btn:hover {
  background-color: var(--color-gray-100);
  color: var(--color-text-primary);
}

.companies__action-btn--success {
  color: var(--color-success);
}

.companies__action-btn--success:hover {
  background-color: var(--color-success-light);
  color: var(--color-success);
}

.companies__action-btn--danger {
  color: var(--color-danger);
}

.companies__action-btn--danger:hover {
  background-color: var(--color-danger-light);
  color: var(--color-danger);
}

.companies__modal-summary {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.companies__modal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.companies__modal-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  font-weight: var(--font-weight-medium);
  margin-bottom: var(--space-1);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.companies__modal-value {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.companies__modal-hr {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.companies__reject-textarea {
  width: 100%;
  margin-top: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border: var(--border-width) solid var(--border-color);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  background: var(--color-white);
  resize: vertical;
  outline: none;
  transition: border-color var(--transition-fast);
}

.companies__reject-textarea:focus {
  border-color: var(--color-primary);
}

.companies__reject-error {
  margin-top: var(--space-2);
  font-size: var(--font-size-xs);
  color: var(--color-danger);
}

.companies__toast {
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

.companies__toast--success {
  background-color: var(--color-success);
}

.companies__toast--error {
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

@media (max-width: 767px) {
  .companies__filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .companies__header-actions {
    flex-wrap: wrap;
  }
}
</style>
