import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const normalizedError = {
      status: -1,
      message: 'An unexpected error occurred',
      data: null
    }

    if (error.response) {
      normalizedError.status = error.response.status
      normalizedError.message =
        error.response.data?.error ??
        error.response.data?.msg ??
        'An unexpected error occurred'
      normalizedError.data = error.response.data

      if (
        normalizedError.status === 401 &&
        error.config &&
        !error.config.url.includes('/auth/login')
      ) {
        localStorage.removeItem('access_token')
        window.location.href = '/login'
      }
    } else if (error.request) {
      normalizedError.status = 0
      normalizedError.message = 'Cannot reach server. Check your connection.'
    } else {
      normalizedError.message = error.message
    }

    return Promise.reject(normalizedError)
  }
)

export const uploadFile = async (url, file, fieldName) => {
  const formData = new FormData()
  formData.append(fieldName, file)

  return api.post(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const downloadFile = async (url, filename) => {
  try {
    const response = await api.get(url, {
      responseType: 'blob'
    })

    const urlCreator = window.URL || window.webkitURL
    const objectUrl = urlCreator.createObjectURL(response)

    const link = document.createElement('a')
    link.href = objectUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    urlCreator.revokeObjectURL(objectUrl)
    return response
  } catch (error) {
    console.error('Download failed:', error)
    throw error
  }
}

export default api
