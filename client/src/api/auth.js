import api from './axios'

export const login = (data) => api.post('/auth/login', data)

export const logout = () => api.post('/auth/logout')

export const registerStudent = (data) => api.post('/api/student/register', data)

export const registerCompany = (data) => api.post('/api/company/register', data)
