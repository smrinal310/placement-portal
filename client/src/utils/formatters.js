export const formatDate = (isoString, options = { style: 'short' }) => {
  if (!isoString) return ''

  const date = new Date(isoString)
  if (isNaN(date)) return ''

  if (options.style === 'relative') {
    const diffTime = date.getTime() - new Date().getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

    if (diffDays === 0) return 'today'
    if (diffDays === 1) return 'tomorrow'
    if (diffDays === -1) return 'yesterday'
    if (diffDays > 0) return `in ${diffDays} days`
    return `${Math.abs(diffDays)} days ago`
  }

  if (options.style === 'long') {
    return new Intl.DateTimeFormat('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }).format(date)
  }

  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(date)
}

export const formatNumber = (n) => {
  if (n === null || n === undefined || isNaN(n)) return '0'
  return new Intl.NumberFormat('en-US').format(n)
}

export const formatCGPA = (value) => {
  if (value === null || value === undefined || isNaN(value)) return 'N/A'
  return Number(value).toFixed(1)
}

export const formatSalary = (value) => {
  if (!value) return 'Not disclosed'
  return value.toString()
}

export const getStatusLabel = (status) => {
  if (!status) return 'Unknown'
  return status
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
}

export const getDaysRemaining = (isoDeadline) => {
  if (!isoDeadline) return null
  const deadline = new Date(isoDeadline)
  if (isNaN(deadline)) return null
  const diffTime = deadline.getTime() - new Date().getTime()
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

export const truncate = (str, maxLength = 60) => {
  if (!str) return ''
  if (str.length <= maxLength) return str
  return str.slice(0, maxLength) + '...'
}

export const getInitials = (name) => {
  if (!name || typeof name !== 'string') return '?'
  const trimmed = name.trim()
  if (!trimmed) return '?'

  const words = trimmed.split(/\s+/)
  if (words.length === 1) {
    return words[0].charAt(0).toUpperCase()
  }
  return (words[0].charAt(0) + words[1].charAt(0)).toUpperCase()
}
