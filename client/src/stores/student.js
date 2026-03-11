import { defineStore } from 'pinia'
import * as studentApi from '@/api/student'

export const useStudentStore = defineStore('student', {
  state: () => ({
    // Dashboard
    dashboard: null,
    dashboardLoading: false,
    dashboardError: null,

    // Full profile (for completion calculation)
    profile: null,

    // Drives browse
    drives: [],
    drivesLoading: false,
    drivesError: null,

    // Which drive is currently being applied to
    applyingDriveId: null,
  }),

  actions: {
    async fetchDashboard() {
      this.dashboardLoading = true
      this.dashboardError = null
      try {
        const res = await studentApi.getDashboard()
        this.dashboard = res.data
      } catch (e) {
        this.dashboardError = e.message || 'Failed to load dashboard'
      } finally {
        this.dashboardLoading = false
      }
    },

    async fetchProfile() {
      try {
        const res = await studentApi.getProfile()
        this.profile = res.data
      } catch {
        // Non-blocking — profile completion will just be hidden
      }
    },

    async fetchDrives(filters = {}) {
      this.drivesLoading = true
      this.drivesError = null
      try {
        const params = { ...filters }
        // Remove empty strings so the backend doesn't filter on them
        Object.keys(params).forEach((k) => {
          if (params[k] === '' || params[k] === null || params[k] === undefined) {
            delete params[k]
          }
        })
        const res = await studentApi.getDrives(params)
        this.drives = res.data || []
      } catch (e) {
        this.drivesError = e.message || 'Failed to load drives'
      } finally {
        this.drivesLoading = false
      }
    },

    async applyToDrive(driveId) {
      this.applyingDriveId = driveId
      try {
        await studentApi.applyToDrive(driveId)
        // Optimistically update the list
        const drive = this.drives.find((d) => d.drive_id === driveId)
        if (drive) drive.has_applied = true
        // Update dashboard counters
        if (this.dashboard) {
          this.dashboard.total_applications = (this.dashboard.total_applications ?? 0) + 1
          if (this.dashboard.applications_breakdown) {
            this.dashboard.applications_breakdown.applied =
              (this.dashboard.applications_breakdown.applied ?? 0) + 1
          }
          if (this.dashboard.eligible_drives_not_applied > 0) {
            this.dashboard.eligible_drives_not_applied -= 1
          }
        }
        return { success: true }
      } catch (e) {
        return { success: false, message: e.message || 'Failed to apply' }
      } finally {
        this.applyingDriveId = null
      }
    },
  },
})
