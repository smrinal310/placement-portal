import { defineStore } from 'pinia'
import * as companyApi from '@/api/company'
import { DriveStatus } from '@/utils/constants'

export const useCompanyStore = defineStore('company', {
  state: () => ({
    dashboard: null,
    loading: false,
    error: null,

    // My Drives page state
    drivesList: [],
    drivesLoading: false,
    drivesError: null,
    drivesFilters: {
      search: '',
      status: ''
    }
  }),

  getters: {
    // Dashboard-sourced
    drives: (state) => state.dashboard?.drives ?? [],

    activeDrives: (state) =>
      (state.dashboard?.drives ?? []).filter((d) => d.status === DriveStatus.APPROVED),

    totalApplications: (state) =>
      (state.dashboard?.drives ?? []).reduce((sum, d) => sum + (d.applicant_count ?? 0), 0),

    totalShortlisted: (state) =>
      (state.dashboard?.drives ?? []).reduce((sum, d) => sum + (d.shortlisted_count ?? 0), 0),

    approvalStatus: (state) => state.dashboard?.approval_status,
    companyName: (state) => state.dashboard?.company_name,
    companyDescription: (state) => state.dashboard?.company_description,
    companyLogo: (state) => state.dashboard?.company_logo,

    // Drives page — filtered client-side
    filteredDrives: (state) => {
      let list = state.drivesList
      const q = state.drivesFilters.search.trim().toLowerCase()
      const s = state.drivesFilters.status

      if (q) {
        list = list.filter(
          (d) =>
            d.job_title?.toLowerCase().includes(q) ||
            d.job_type?.toLowerCase().includes(q) ||
            d.salary_package?.toLowerCase().includes(q)
        )
      }
      if (s) {
        list = list.filter((d) => d.status === s)
      }
      return list
    }
  },

  actions: {
    async fetchDashboard() {
      this.loading = true
      this.error = null
      try {
        const response = await companyApi.getDashboard()
        this.dashboard = response.data
      } catch (e) {
        this.error = e.message || 'Failed to load dashboard.'
      } finally {
        this.loading = false
      }
    },

    async fetchDrives() {
      this.drivesLoading = true
      this.drivesError = null
      try {
        const response = await companyApi.getDrives()
        this.drivesList = response.data || []
      } catch (e) {
        this.drivesError = e.message || 'Failed to load drives.'
      } finally {
        this.drivesLoading = false
      }
    }
  }
})
