<template>
  <div class="students">
    <Transition name="toast">
      <div
        v-if="feedbackMessage"
        class="students__toast"
        :class="feedbackType === 'error' ? 'students__toast--error' : 'students__toast--success'"
      >
        <i :class="feedbackType === 'error' ? 'bi bi-x-circle-fill' : 'bi bi-check-circle-fill'"></i>
        {{ feedbackMessage }}
      </div>
    </Transition>

    <header class="students__header">
      <div>
        <h1 class="students__title">Student Management</h1>
        <p class="students__subtitle">Manage student profiles, academic records, and eligibility status.</p>
      </div>

    </header>

    <AppFilterBar v-model="searchQuery" placeholder="Search by name, ID or email...">
      <select class="filter-select" v-model="selectedBranch">
        <option value="">All Branches</option>
        <option v-for="branch in BRANCH_LIST" :key="branch" :value="branch">{{ branch }}</option>
      </select>
      <select class="filter-select" v-model="selectedYear">
        <option value="">All Years</option>
        <option value="1">1</option>
        <option value="2">2</option>
        <option value="3">3</option>
        <option value="4">4</option>
      </select>
    </AppFilterBar>

    <div class="card students__table-card">
      <AppSpinner v-if="adminStore.loading" />

      <AppEmptyState
        v-else-if="adminStore.error"
        icon="bi bi-exclamation-circle"
        title="Failed to load students"
        :subtitle="adminStore.error"
        actionLabel="Retry"
        @action="loadStudents"
      />

      <AppEmptyState
        v-else-if="!adminStore.students.length"
        icon="bi bi-people"
        title="No students found"
        subtitle="No students match your current filters."
      />

      <template v-else>
        <div class="students__table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Branch</th>
                <th>CGPA</th>
                <th>Grad Year</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="student in adminStore.students" :key="student.id">
                <td>
                  <div class="students__name-cell">
                    <AppAvatar :name="student.name" size="sm" />
                    <div class="students__student-name">{{ student.name }}</div>
                  </div>
                </td>
                <td>{{ student.email }}</td>
                <td>{{ student.branch }}</td>
                <td>{{ formatCGPA(student.cgpa) }}</td>
                <td>{{ student.year }}</td>
                <td>
                  <div class="students__status-cell">
                    <AppBadge :status="student.account_status" />
                    <span v-if="student.is_placed" class="students__placed-tag">Placed</span>
                  </div>
                </td>
                <td>
                  <div class="students__actions">
                    <button
                      class="students__action-btn"
                      title="View"
                      @click="router.push('/admin/students/' + student.id)"
                    >
                      <i class="bi bi-eye"></i>
                    </button>
                    <button
                      v-if="student.account_status === AccountStatus.ACTIVE"
                      class="students__action-btn students__action-btn--danger"
                      title="Blacklist"
                      @click="openModal('blacklist', student)"
                    >
                      <i class="bi bi-slash-circle"></i>
                    </button>
                    <button
                      v-if="student.account_status === AccountStatus.BLACKLISTED"
                      class="students__action-btn students__action-btn--success"
                      title="Activate"
                      @click="openModal('activate', student)"
                    >
                      <i class="bi bi-check-circle"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="students__pagination">
          <AppPagination
            variant="text"
            :total="adminStore.studentsTotal"
            :perPage="10"
            :currentPage="adminStore.studentFilters.page"
            @page-change="(page) => adminStore.fetchStudents({ page })"
          />
        </div>
      </template>
    </div>

    <AppModal
      :show="modalState.show && modalState.type === 'blacklist'"
      title="Blacklist Student"
      headerIcon="bi bi-person-slash"
      confirmLabel="Confirm Blacklist"
      confirmVariant="danger"
      warningMessage="This student will be unable to apply for any placement drives."
      :loading="adminStore.actionLoading"
      @confirm="handleBlacklistConfirm"
      @cancel="closeModal"
    >
      <div class="students__modal-summary">
        <div class="students__modal-row">
          <AppAvatar :name="modalState.student?.name || ''" size="sm" />
          <div>
            <div class="students__modal-name">{{ modalState.student?.name }}</div>
            <div class="students__modal-meta">{{ modalState.student?.branch }}</div>
          </div>
          <div class="students__modal-cgpa">
            CGPA <span>{{ formatCGPA(modalState.student?.cgpa) }}</span>
          </div>
        </div>
      </div>
    </AppModal>

    <AppModal
      :show="modalState.show && modalState.type === 'activate'"
      title="Activate Student"
      headerIcon="bi bi-person-check"
      confirmLabel="Confirm Activation"
      confirmVariant="primary"
      warningMessage="This student will regain access to apply for placement drives."
      :loading="adminStore.actionLoading"
      @confirm="handleActivateConfirm"
      @cancel="closeModal"
    >
      <div class="students__modal-summary">
        <div class="students__modal-row">
          <AppAvatar :name="modalState.student?.name || ''" size="sm" />
          <div>
            <div class="students__modal-name">{{ modalState.student?.name }}</div>
            <div class="students__modal-meta">{{ modalState.student?.branch }}</div>
          </div>
          <div class="students__modal-cgpa">
            CGPA <span>{{ formatCGPA(modalState.student?.cgpa) }}</span>
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
import { formatCGPA } from '@/utils/formatters'
import { AccountStatus, BRANCH_LIST } from '@/utils/constants'

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
const selectedBranch = ref('')
const selectedYear = ref('')
const feedbackMessage = ref('')
const feedbackType = ref('success')

const modalState = reactive({
  show: false,
  type: null,
  student: null
})

let searchTimer = null
let feedbackTimer = null

const showFeedback = (message, type = 'success') => {
  feedbackMessage.value = message
  feedbackType.value = type
  clearTimeout(feedbackTimer)
  feedbackTimer = setTimeout(() => { feedbackMessage.value = '' }, 3000)
}

const loadStudents = () => {
  adminStore.fetchStudents({
    search: searchQuery.value,
    branch: selectedBranch.value,
    year: selectedYear.value,
    page: 1
  })
}

const openModal = (type, student) => {
  modalState.type = type
  modalState.student = student
  modalState.show = true
}

const closeModal = () => {
  modalState.show = false
  setTimeout(() => {
    modalState.type = null
    modalState.student = null
  }, 300)
}

const handleBlacklistConfirm = async () => {
  try {
    await adminStore.blacklistStudent(modalState.student.id)
    closeModal()
    showFeedback('Student blacklisted successfully.')
  } catch {
    showFeedback(adminStore.error || 'Failed to blacklist student.', 'error')
  }
}

const handleActivateConfirm = async () => {
  try {
    await adminStore.activateStudent(modalState.student.id)
    closeModal()
    showFeedback('Student activated successfully.')
  } catch {
    showFeedback(adminStore.error || 'Failed to activate student.', 'error')
  }
}

watch(selectedBranch, () => {
  adminStore.fetchStudents({ branch: selectedBranch.value, search: searchQuery.value, year: selectedYear.value, page: 1 })
})

watch(selectedYear, () => {
  adminStore.fetchStudents({ year: selectedYear.value, search: searchQuery.value, branch: selectedBranch.value, page: 1 })
})

watch(searchQuery, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    adminStore.fetchStudents({ search: searchQuery.value, branch: selectedBranch.value, year: selectedYear.value, page: 1 })
  }, 300)
})

onMounted(() => {
  loadStudents()
})
</script>

<style scoped>
.students {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.students__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: var(--space-4);
}

.students__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-1);
}

.students__subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.students__header-actions {
  display: flex;
  gap: var(--space-3);
  align-items: center;
}

.students__table-card {
  padding: 0;
  overflow: hidden;
}

.students__table-wrap {
  overflow-x: auto;
}

.students__pagination {
  padding: var(--space-4) var(--space-6);
  border-top: var(--border-width) solid var(--border-color);
}

.students__name-cell {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.students__student-name {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
}

.students__status-cell {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  align-items: flex-start;
}

.students__placed-tag {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--color-success);
}

.students__actions {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.students__action-btn {
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

.students__action-btn:hover {
  background-color: var(--color-gray-100);
  color: var(--color-text-primary);
}

.students__action-btn--success {
  color: var(--color-success);
}

.students__action-btn--success:hover {
  background-color: var(--color-success-light);
  color: var(--color-success);
}

.students__action-btn--danger {
  color: var(--color-danger);
}

.students__action-btn--danger:hover {
  background-color: var(--color-danger-light);
  color: var(--color-danger);
}

.students__modal-summary {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.students__modal-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.students__modal-name {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
}

.students__modal-meta {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.students__modal-cgpa {
  margin-left: auto;
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.students__modal-cgpa span {
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
}

.students__toast {
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

.students__toast--success {
  background-color: var(--color-success);
}

.students__toast--error {
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
  .students__filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .students__header-actions {
    flex-wrap: wrap;
  }
}
</style>
