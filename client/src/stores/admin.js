import { defineStore } from 'pinia'
import * as adminApi from '../api/admin'

export const useAdminStore = defineStore('admin', {
  state: () => ({
    // Dashboard
    stats: null,
    recentPlacements: [],
    recentActivity: [],

    // Companies
    companies: [],
    companiesTotal: 0,
    selectedCompany: null,

    // Students
    students: [],
    studentsTotal: 0,
    selectedStudent: null,

    // Drives
    drives: [],
    drivesTotal: 0,
    selectedDrive: null,

    // Applications
    applications: [],
    applicationsTotal: 0,

    // Filters
    companyFilters: { search: '', status: '', page: 1, perPage: 10 },
    studentFilters: { search: '', branch: '', isPlaced: '', page: 1, perPage: 10 },
    driveFilters: { search: '', status: '', page: 1, perPage: 10 },
    applicationFilters: { status: '', driveId: '', companyId: '', page: 1, perPage: 10 },

    // Dropdown options
    driveOptions: [],
    companyOptions: [],

    // UI state
    loading: false,
    actionLoading: false,
    error: null,
    exportLoading: false
  }),

  getters: {
    pendingCompaniesCount: (state) => state.stats?.companies?.pending ?? 0,
    pendingDrivesCount: (state) => state.stats?.drives?.pending ?? 0
  },

  actions: {
    async fetchDashboard() {
      this.loading = true
      this.error = null
      try {
        const response = await adminApi.getDashboard()
        this.stats = response.data
        this.recentPlacements = response.data?.recent_placements || []
        this.recentActivity = response.data?.recent_activity || []
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },

    async fetchCompanies(filters = {}) {
      this.loading = true
      this.error = null
      this.companyFilters = { ...this.companyFilters, ...filters }
      try {
        const response = await adminApi.getCompanies(this.companyFilters)
        this.companies = response.data || []
        this.companiesTotal = this.companies.length
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },

    async fetchCompany(id) {
      this.loading = true
      this.error = null
      try {
        const response = await adminApi.getCompany(id)
        this.selectedCompany = response.data
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },

    async approveCompany(id) {
      this.actionLoading = true
      this.error = null
      try {
        await adminApi.approveCompany(id)
        const index = this.companies.findIndex(c => c.id === id)
        if (index !== -1) {
          const updated = { ...this.companies[index], approval_status: 'approved' }
          this.companies.splice(index, 1, updated)
        }
        await this.fetchDashboard()
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.actionLoading = false
      }
    },

    async rejectCompany(id, reason) {
      this.actionLoading = true
      this.error = null
      try {
        await adminApi.rejectCompany(id, { reason })
        const index = this.companies.findIndex(c => c.id === id)
        if (index !== -1) {
          const updated = { ...this.companies[index], approval_status: 'rejected' }
          this.companies.splice(index, 1, updated)
        }
        await this.fetchDashboard()
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.actionLoading = false
      }
    },

    async blacklistCompany(id) {
      this.actionLoading = true
      this.error = null
      try {
        await adminApi.blacklistCompany(id)
        const index = this.companies.findIndex(c => c.id === id)
        if (index !== -1) {
          const updated = { ...this.companies[index], account_status: 'blacklisted' }
          this.companies.splice(index, 1, updated)
        }
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.actionLoading = false
      }
    },

    async activateCompany(id) {
      this.actionLoading = true
      this.error = null
      try {
        await adminApi.activateCompany(id)
        const index = this.companies.findIndex(c => c.id === id)
        if (index !== -1) {
          const updated = { ...this.companies[index], account_status: 'active' }
          this.companies.splice(index, 1, updated)
        }
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.actionLoading = false
      }
    },

    async fetchStudents(filters = {}) {
      this.loading = true
      this.error = null
      this.studentFilters = { ...this.studentFilters, ...filters }
      try {
        const response = await adminApi.getStudents(this.studentFilters)
        this.students = response.data || []
        this.studentsTotal = this.students.length
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },

    async fetchStudent(id) {
      this.loading = true
      this.error = null
      try {
        const response = await adminApi.getStudent(id)
        this.selectedStudent = response.data
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },

    async blacklistStudent(id) {
      this.actionLoading = true
      this.error = null
      try {
        await adminApi.blacklistStudent(id)
        const index = this.students.findIndex(s => s.id === id)
        if (index !== -1) {
          const updated = { ...this.students[index], account_status: 'blacklisted' }
          this.students.splice(index, 1, updated)
        }
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.actionLoading = false
      }
    },

    async activateStudent(id) {
      this.actionLoading = true
      this.error = null
      try {
        await adminApi.activateStudent(id)
        const index = this.students.findIndex(s => s.id === id)
        if (index !== -1) {
          const updated = { ...this.students[index], account_status: 'active' }
          this.students.splice(index, 1, updated)
        }
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.actionLoading = false
      }
    },

    async fetchDrives(filters = {}) {
      this.loading = true
      this.error = null
      this.driveFilters = { ...this.driveFilters, ...filters }
      try {
        const response = await adminApi.getDrives(this.driveFilters)
        this.drives = response.data || []
        this.drivesTotal = this.drives.length
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },

    async fetchDrive(id) {
      this.loading = true
      this.error = null
      try {
        const response = await adminApi.getDrive(id)
        this.selectedDrive = response.data
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },

    async approveDrive(id) {
      this.actionLoading = true
      this.error = null
      try {
        await adminApi.approveDrive(id)
        const index = this.drives.findIndex(d => d.id === id)
        if (index !== -1) {
          const updated = { ...this.drives[index], status: 'approved' }
          this.drives.splice(index, 1, updated)
        }
        await this.fetchDashboard()
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.actionLoading = false
      }
    },

    async rejectDrive(id, reason) {
      this.actionLoading = true
      this.error = null
      try {
        await adminApi.rejectDrive(id, { reason })
        const index = this.drives.findIndex(d => d.id === id)
        if (index !== -1) {
          const updated = { ...this.drives[index], status: 'rejected' }
          this.drives.splice(index, 1, updated)
        }
        await this.fetchDashboard()
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.actionLoading = false
      }
    },

    async fetchApplications(filters = {}) {
      this.loading = true
      this.error = null
      this.applicationFilters = { ...this.applicationFilters, ...filters }
      try {
        const response = await adminApi.getApplications(this.applicationFilters)
        this.applications = response.data || []
        this.applicationsTotal = this.applications.length
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loading = false
      }
    },

    async fetchDriveOptions() {
      try {
        const response = await adminApi.getDrives({ perPage: 999 })
        this.driveOptions = (response.data || []).map(d => ({
          id: d.id,
          label: d.job_title
        }))
      } catch (e) {
        // Silently fail for options mapping
      }
    },

    async fetchCompanyOptions() {
      try {
        const response = await adminApi.getCompanies({ perPage: 999 })
        this.companyOptions = (response.data || []).map(c => ({
          id: c.id,
          label: c.company_name
        }))
      } catch (e) {
        // Silently fail for options mapping
      }
    }
  }
})
