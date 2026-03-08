import api, { downloadFile, uploadFile } from './axios'

// ── PROFILE ──

export const getProfile = () => api.get('/api/student/profile')

export const updateProfile = (data) => api.put('/api/student/profile', data)

export const uploadResume = (file) => uploadFile('/api/student/profile/resume', file, 'resume')

export const downloadResume = (filename) => downloadFile('/api/student/profile/resume', filename)

// ── DASHBOARD ──

export const getDashboard = () => api.get('/api/student/dashboard')

// ── DRIVES ──

export const getDrives = (params) => api.get('/api/student/drives', { params })

export const getDrive = (id) => api.get(`/api/student/drives/${id}`)

export const applyToDrive = (id) => api.post(`/api/student/drives/${id}/apply`)

// ── APPLICATIONS ──

export const getApplications = (params) => api.get('/api/student/applications', { params })

export const getApplication = (id) => api.get(`/api/student/applications/${id}`)

// ── EXPORT ──

export const triggerExport = () => api.post('/api/student/applications/export')

export const getExportStatus = (jobId) => api.get(`/api/student/applications/export/${jobId}`)

export const downloadExport = (jobId, filename) => downloadFile(`/api/student/applications/export/${jobId}/download`, filename)

// ── NOTIFICATIONS ──

export const getNotifications = (params) => api.get('/api/student/notifications', { params })

export const markNotificationRead = (id) => api.patch(`/api/student/notifications/${id}/read`)

export const markAllNotificationsRead = () => api.patch('/api/student/notifications/read-all')
