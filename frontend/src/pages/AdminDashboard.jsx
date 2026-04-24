import { useState, useEffect } from 'react'
import { fetchAdminPolicies, deleteAdminPolicy, uploadPolicy, updateAdminPolicy } from '../api/api'

export default function AdminDashboard({ auth }) {
  const [policies, setPolicies] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [isUploading, setIsUploading] = useState(false)
  const [file, setFile] = useState(null)

  const [editingId, setEditingId] = useState(null)
  const [editValue, setEditValue] = useState('')

  const loadPolicies = async () => {
    setIsLoading(true)
    try {
      const data = await fetchAdminPolicies(auth.username, auth.password)
      setPolicies(data.policies)
    } catch (err) {
      alert('Failed to load policies')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadPolicies()
  }, [])

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this policy?')) return
    try {
      await deleteAdminPolicy(id, auth.username, auth.password)
      setPolicies(prev => prev.filter(p => p.id !== id))
    } catch (err) {
      alert('Delete failed')
    }
  }

  const handleEdit = async (id) => {
    if (!editValue.trim()) return
    try {
      await updateAdminPolicy(id, editValue.trim(), auth.username, auth.password)
      setEditingId(null)
      loadPolicies()
    } catch (err) {
      alert('Update failed')
    }
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!file) return
    setIsUploading(true)
    try {
      await uploadPolicy(file, auth.username, auth.password)
      setFile(null)
      loadPolicies()
    } catch (err) {
      alert('Upload failed')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="py-10">
      <div className="flex justify-between items-center mb-10">
        <div>
          <h1 className="text-2xl font-bold">Knowledge Base</h1>
          <p className="text-slate-600">Manage insurance documents.</p>
        </div>
        <button onClick={loadPolicies} className="btn btn-secondary">Refresh</button>
      </div>

      <div className="card mb-10">
        <h3 className="font-bold mb-4">Upload Policy</h3>
        <form onSubmit={handleUpload} className="flex gap-4">
          <input 
            type="file" 
            className="input" 
            onChange={(e) => setFile(e.target.files[0])} 
          />
          <button type="submit" disabled={!file || isUploading} className="btn whitespace-nowrap">
            {isUploading ? 'Uploading...' : 'Upload'}
          </button>
        </form>
      </div>

      <div className="card">
        <table className="w-full text-left text-sm border-collapse">
          <thead className="border-b border-slate-200">
            <tr>
              <th className="p-3 font-bold">Document Name</th>
              <th className="p-3 font-bold text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {isLoading ? (
              <tr><td colSpan="2" className="p-10 text-center">Loading...</td></tr>
            ) : policies.length === 0 ? (
              <tr><td colSpan="2" className="p-10 text-center">No documents.</td></tr>
            ) : (
              policies.map((p) => (
                <tr key={p.id}>
                  <td className="p-3">
                    {editingId === p.id ? (
                      <input 
                        className="input text-sm py-1" 
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        autoFocus
                      />
                    ) : (
                      p.source
                    )}
                  </td>
                  <td className="p-3 text-right">
                    <div className="flex justify-end gap-4">
                      {editingId === p.id ? (
                        <>
                          <button onClick={() => handleEdit(p.id)} className="text-emerald-600 hover:underline">Save</button>
                          <button onClick={() => setEditingId(null)} className="text-slate-500 hover:underline">Cancel</button>
                        </>
                      ) : (
                        <>
                          <button 
                            onClick={() => { setEditingId(p.id); setEditValue(p.source); }} 
                            className="text-blue-600 hover:underline"
                          >
                            Edit
                          </button>
                          <button 
                            onClick={() => handleDelete(p.id)} 
                            className="text-red-600 hover:underline"
                          >
                            Delete
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
