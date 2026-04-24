const BASE_URL = 'http://127.0.0.1:8000'

function getAuthHeader(username, password) {
  return { 'Authorization': 'Basic ' + btoa(username + ":" + password) }
}

export async function fetchRecommendations(payload) {
  const response = await fetch(`${BASE_URL}/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || 'Failed to fetch recommendations')
  }

  return response.json()
}

export async function fetchChatResponse(payload) {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || 'Chat failed')
  }

  return response.json()
}

export async function fetchAdminPolicies(username, password) {
  const response = await fetch(`${BASE_URL}/admin/policies`, {
    headers: getAuthHeader(username, password)
  })

  if (!response.ok) throw new Error('Unauthorized')
  return response.json()
}

export async function deleteAdminPolicy(doc_id, username, password) {
  const response = await fetch(`${BASE_URL}/admin/policy/${doc_id}`, {
    method: 'DELETE',
    headers: getAuthHeader(username, password)
  })

  if (!response.ok) throw new Error('Delete failed')
  return response.json()
}

export async function uploadPolicy(file, username, password) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${BASE_URL}/upload-policy`, {
    method: 'POST',
    body: formData,
    // Add auth header if you protect this endpoint
    headers: getAuthHeader(username, password)
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || 'Upload failed')
  }
  return response.json()
}

export async function updateAdminPolicy(doc_id, source, username, password) {
  const response = await fetch(`${BASE_URL}/admin/policy/${doc_id}`, {
    method: 'PATCH',
    headers: { 
      ...getAuthHeader(username, password),
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ source })
  })

  if (!response.ok) throw new Error('Update failed')
  return response.json()
}

