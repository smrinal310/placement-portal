export const UserRole = Object.freeze({
  ADMIN: 'admin',
  COMPANY: 'company',
  STUDENT: 'student'
})

export const ApprovalStatus = Object.freeze({
  PENDING: 'pending',
  APPROVED: 'approved',
  REJECTED: 'rejected'
})

export const DriveStatus = Object.freeze({
  PENDING: 'pending',
  APPROVED: 'approved',
  CLOSED: 'closed'
})

export const ApplicationStatus = Object.freeze({
  APPLIED: 'applied',
  SHORTLISTED: 'shortlisted',
  SELECTED: 'selected',
  REJECTED: 'rejected'
})

export const AccountStatus = Object.freeze({
  ACTIVE: 'active',
  INACTIVE: 'inactive',
  BLACKLISTED: 'blacklisted'
})

export const BRANCH_LIST = [
  'Computer Science',
  'Information Technology',
  'Electronics',
  'Mechanical',
  'Civil',
  'Chemical',
  'Electrical'
]

export const JOB_TYPES = ['Full-time', 'Internship', 'Contract']

export const EXPORT_POLL_INTERVAL_MS = 3000
export const EXPORT_POLL_MAX_ATTEMPTS = 20
