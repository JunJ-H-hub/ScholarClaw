import axios from 'axios'

const API_BASE_URL = '/knowledge'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const knowledgeApi = {
  getDatabases() {
    return api.get('/databases')
  },

  createDatabase(data) {
    return api.post('/databases', data)
  },

  deleteDatabase(dbId) {
    return api.delete(`/databases/${dbId}`)
  },

  selectDatabase(dbId) {
    return api.get('/databases/select', { params: { db_id: dbId } })
  },

  getDatabaseInfo(dbId) {
    return api.get(`/databases/${dbId}`)
  },

  updateDatabase(dbId, data) {
    return api.put(`/databases/${dbId}`, data)
  },

  addDocuments(dbId, items, params = {}) {
    return api.post(`/databases/${dbId}/documents`, { items, params })
  },

  getDocumentInfo(dbId, docId) {
    return api.get(`/databases/${dbId}/documents/${docId}`)
  },

  getDocumentBasicInfo(dbId, docId) {
    return api.get(`/databases/${dbId}/documents/${docId}/basic`)
  },

  getDocumentContent(dbId, docId) {
    return api.get(`/databases/${dbId}/documents/${docId}/content`)
  },

  deleteDocument(dbId, docId) {
    return api.delete(`/databases/${dbId}/documents/${docId}`)
  },

  queryDatabase(dbId, query, meta = {}) {
    return api.post(`/databases/${dbId}/query-test`, { query, meta })
  },

  uploadFile(file, dbId = null, allowJsonl = false) {
    const formData = new FormData()
    formData.append('file', file)
    
    const params = {}
    if (dbId) params.db_id = dbId
    if (allowJsonl) params.allow_jsonl = true

    return axios.post(`${API_BASE_URL}/files/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      params
    })
  },

  getSupportedTypes() {
    return api.get('/files/supported-types')
  }
}

export default knowledgeApi
