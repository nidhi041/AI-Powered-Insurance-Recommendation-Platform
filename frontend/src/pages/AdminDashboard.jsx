import { useState, useEffect } from 'react'
import { fetchAdminPolicies, deleteAdminPolicy, uploadPolicy } from '../api/api'

export default function AdminDashboard({ auth }) {
  const [policies, setPolicies] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
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
      setError('Failed to load policies')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadPolicies()
  }, [])

  const handleEdit = async (id) => {
    if (!editValue.trim()) return
    try {
      await fetch(`http://127.0.0.1:8000/admin/policy/${id}`, {
        method: 'PATCH',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': 'Basic ' + btoa(auth.username + ":" + auth.password)
        },
        body: JSON.stringify({ source: editValue.trim() })
      })
      setEditingId(null)
      loadPolicies()
    } catch (err) {
      alert('Failed to update policy')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this policy document?')) return
    
    try {
      await deleteAdminPolicy(id, auth.username, auth.password)
      setPolicies(prev => prev.filter(p => p.id !== id))
    } catch (err) {
      alert('Failed to delete policy')
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
      alert('Upload failed: ' + (err.message || 'Unknown error'))
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="min-h-screen pt-24 pb-12 px-4 sm:px-6">
      <div className="max-w-6xl mx-auto space-y-10">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div>
            <h1 className="text-3xl font-extrabold text-white mb-2">Knowledge Base</h1>
            <p className="text-slate-400">Manage the insurance policy documents used for AI recommendations.</p>
          </div>
          
          <div className="flex items-center gap-4">
            <button 
              onClick={loadPolicies}
              className="p-2.5 rounded-xl border border-white/10 bg-white/5 text-slate-400 hover:text-white transition-colors"
              title="Refresh"
            >
              <svg className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
            <button 
              onClick={() => window.location.reload()}
              className="text-xs font-bold text-slate-500 hover:text-red-400 uppercase tracking-widest transition-colors"
            >
              Sign Out
            </button>
          </div>
        </div>

        {/* Upload Card */}
        <div className="glass-card p-6 sm:p-8 border-indigo-500/20 bg-indigo-500/5">
          <h3 className="text-lg font-bold text-white mb-6">Upload New Policy</h3>
          <form onSubmit={handleUpload} className="flex flex-col sm:flex-row items-end gap-4">
            <div className="flex-1 w-full space-y-2">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-widest ml-1">Select Document (PDF/TXT/JSON)</label>
              <div className="relative group">
                <input 
                  type="file" 
                  accept=".pdf,.txt,.json"
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                  onChange={(e) => setFile(e.target.files[0])}
                />
                <div className="form-input flex items-center justify-between pointer-events-none group-hover:border-indigo-500/50 transition-colors">
                  <span className={file ? 'text-white' : 'text-slate-500'}>
                    {file ? file.name : 'Choose a file...'}
                  </span>
                  <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
              </div>
            </div>
            <button 
              type="submit" 
              disabled={!file || isUploading}
              className="btn-primary py-3.5 px-8 disabled:opacity-50 disabled:grayscale"
            >
              {isUploading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                'Ingest Document'
              )}
            </button>
          </form>
        </div>

        {/* Policies Table */}
        <div className="glass-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/5 bg-white/2">
                  <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Document Name</th>
                  <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-widest">Chunks</th>
                  <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-widest text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {isLoading ? (
                  <tr>
                    <td colSpan="3" className="px-6 py-12 text-center">
                      <div className="flex flex-col items-center gap-3">
                        <div className="w-8 h-8 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
                        <p className="text-sm text-slate-400">Loading knowledge base...</p>
                      </div>
                    </td>
                  </tr>
                ) : policies.length === 0 ? (
                  <tr>
                    <td colSpan="3" className="px-6 py-12 text-center">
                      <p className="text-slate-400">No documents found. Upload a policy to get started.</p>
                    </td>
                  </tr>
                ) : (
                  policies.map((policy) => (
                    <tr key={policy.id} className="hover:bg-white/2 transition-colors group">
                      <td className="px-6 py-5">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-lg bg-slate-800 flex items-center justify-center text-indigo-400">
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                          </div>
                          <div>
                            {editingId === policy.id ? (
                              <div className="flex items-center gap-2">
                                <input 
                                  className="bg-white/5 border border-indigo-500/50 rounded px-2 py-1 text-sm text-white focus:outline-none"
                                  value={editValue}
                                  onChange={(e) => setEditValue(e.target.value)}
                                  autoFocus
                                />
                                <button onClick={() => handleEdit(policy.id)} className="text-emerald-400 hover:text-emerald-300">
                                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" /></svg>
                                </button>
                                <button onClick={() => setEditingId(null)} className="text-slate-500 hover:text-slate-300">
                                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" /></svg>
                                </button>
                              </div>
                            ) : (
                              <>
                                <p className="text-sm font-medium text-white">{policy.source}</p>
                                <p className="text-[10px] text-slate-500 font-mono mt-0.5">{policy.id}</p>
                              </>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-5">
                        <span className="px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[10px] font-bold">
                          {policy.chunk_count} CHUNKS
                        </span>
                      </td>
                      <td className="px-6 py-5 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button 
                            onClick={() => { setEditingId(policy.id); setEditValue(policy.source); }}
                            className="p-2 rounded-lg text-slate-500 hover:bg-white/5 hover:text-white transition-all opacity-0 group-hover:opacity-100"
                            title="Edit Name"
                          >
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                          </button>
                          <button 
                            onClick={() => handleDelete(policy.id)}
                            className="p-2 rounded-lg text-slate-500 hover:bg-red-500/10 hover:text-red-400 transition-all opacity-0 group-hover:opacity-100"
                            title="Delete Policy"
                          >
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
