import api, { downloadFile, uploadFile } from './axios'

// ── PROFILE ──

export const getProfile = () => api.get('/api/company/profile')

export const updateProfile = (data) => api.put('/api/company/profile', data)

export const uploadLogo = (file) => uploadFile('/api/company/profile/logo', file, 'logo')

// ── DASHBOARD ──

export const getDashboard = () => api.get('/api/company/dashboard')

// ── DRIVES ──

export const createDrive = (data) => api.post('/api/company/drives', data)

export const getDrives = (params) => api.get('/api/company/drives', { params })

export const getDrive = (id) => api.get(`/api/company/drives/${id}`)

export const updateDrive = (id, data) => api.put(`/api/company/drives/${id}`, data)

export const getDriveApplications = (id, params) => api.get(`/api/company/drives/${id}/applications`, { params })

// ── STUDENTS ──

export const getStudent = (id) => api.get(`/api/company/students/${id}`)

// ── APPLICATIONS ──

export const updateApplicationStatus = (id, data) => api.patch(`/api/company/applications/${id}/status`, data)

export const updateApplicationInterview = (id, data) => api.patch(`/api/company/applications/${id}/interview`, data)

export const downloadResume = (id, filename) => downloadFile(`/api/company/applications/${id}/resume`, filename)

