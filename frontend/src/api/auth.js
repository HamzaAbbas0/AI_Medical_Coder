import http from './http'

// Adjust payload keys to match your backend serializer
export const login = (username, password) =>
  http.post('/auth/login/', { username, password })


// Register a new user
export const registerUser = async (payload) => {
  const { data } = await http.post('/auth/register/', payload)
  return data
}

// Public: password reset (no auth)
export const resetPassword = async ({ email, new_password }) => {
  const { data } = await http.post('/auth/password/reset/', { email, new_password })
  return data
}