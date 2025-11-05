import http from './http'

// Upload file
export const uploadDocument = async (file) => {
  const form = new FormData()
  form.append('file', file)
  const { data } = await http.post('/medical-documents/upload/', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}
