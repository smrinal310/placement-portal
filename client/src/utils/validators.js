export const validateEmail = (value) => {
  if (!value || typeof value !== 'string') {
    return { valid: false, message: 'Valid email is required' }
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(value)) {
    return { valid: false, message: 'Valid email is required' }
  }
  return { valid: true, message: '' }
}

export const validatePassword = (value) => {
  if (!value || typeof value !== 'string') {
    return { valid: false, message: 'Password is required' }
  }
  if (value.length < 8) {
    return { valid: false, message: 'Password must be at least 8 characters' }
  }
  if (!/\d/.test(value)) {
    return { valid: false, message: 'Password must contain at least one number' }
  }
  return { valid: true, message: '' }
}

export const validateConfirmPassword = (password, confirm) => {
  if (password !== confirm) {
    return { valid: false, message: 'Passwords must match' }
  }
  return { valid: true, message: '' }
}

export const validateCGPA = (value) => {
  if (value === null || value === undefined || value === '') {
    return { valid: false, message: 'CGPA must be between 0 and 10' }
  }
  const num = Number(value)
  if (isNaN(num) || num < 0.0 || num > 10.0) {
    return { valid: false, message: 'CGPA must be between 0 and 10' }
  }
  return { valid: true, message: '' }
}

export const validateYear = (value) => {
  if (value === null || value === undefined || value === '') {
    return { valid: false, message: 'Year is required' }
  }
  const num = Number(value)
  if (!Number.isInteger(num) || num < 1 || num > 4) {
    return { valid: false, message: 'Year must be between 1 and 4' }
  }
  return { valid: true, message: '' }
}

export const validateRequired = (value, fieldName) => {
  if (value === null || value === undefined || (typeof value === 'string' && value.trim() === '')) {
    return { valid: false, message: `${fieldName} is required` }
  }
  return { valid: true, message: '' }
}

export const validateFutureDate = (isoString, fieldName) => {
  if (!isoString) {
    return { valid: false, message: `${fieldName} is required` }
  }
  const date = new Date(isoString)
  if (isNaN(date.getTime())) {
    return { valid: false, message: `${fieldName} must be a valid date` }
  }
  if (date <= new Date()) {
    return { valid: false, message: `${fieldName} must be a future date` }
  }
  return { valid: true, message: '' }
}

export const validateFileSize = (file, maxMB) => {
  if (!file) {
    return { valid: false, message: 'File is required' }
  }
  const maxSize = maxMB * 1024 * 1024
  if (file.size > maxSize) {
    return { valid: false, message: `File must be under ${maxMB}MB` }
  }
  return { valid: true, message: '' }
}

export const validateFileType = (file, allowedExtensions) => {
  if (!file || !file.name) {
    return { valid: false, message: 'File is required' }
  }
  const extMatch = file.name.match(/\.([^.]+)$/)
  if (!extMatch) {
    return { valid: false, message: 'File type not allowed' }
  }
  const extension = `.${extMatch[1]}`.toLowerCase()
  const isAllowed = allowedExtensions.some(ext => ext.toLowerCase() === extension)
  
  if (!isAllowed) {
    return { valid: false, message: 'File type not allowed' }
  }
  return { valid: true, message: '' }
}
