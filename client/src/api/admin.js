import api from './axios'

// ── DASHBOARD ──

export const getDashboard = () => api.get('/api/admin/dashboard')

// ── COMPANIES ──

export const getCompanies = (params) => api.get('/api/admin/companies', { params })

export const getCompany = (id) => api.get(`/api/admin/companies/${id}`)

export const approveCompany = (id) => api.patch(`/api/admin/companies/${id}/approve`)

export const rejectCompany = (id, data) => api.patch(`/api/admin/companies/${id}/reject`, data)

export const blacklistCompany = (id) => api.patch(`/api/admin/companies/${id}/blacklist`)

export const activateCompany = (id) => api.patch(`/api/admin/companies/${id}/activate`)

// ── STUDENTS ──

export const getStudents = (params) => api.get('/api/admin/students', { params })

export const getStudent = (id) => api.get(`/api/admin/students/${id}`)

export const blacklistStudent = (id) => api.patch(`/api/admin/students/${id}/blacklist`)

export const activateStudent = (id) => api.patch(`/api/admin/students/${id}/activate`)

// ── DRIVES ──

export const getDrives = (params) => api.get('/api/admin/drives', { params })

export const getDrive = (id) => api.get(`/api/admin/drives/${id}`)

export const approveDrive = (id) => api.patch(`/api/admin/drives/${id}/approve`)

export const rejectDrive = (id, data) => api.patch(`/api/admin/drives/${id}/reject`, data)

// ── APPLICATIONS ──

export const getApplications = (params) => api.get('/api/admin/applications', { params })
