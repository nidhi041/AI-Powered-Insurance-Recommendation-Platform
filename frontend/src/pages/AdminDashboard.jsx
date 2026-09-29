import { useState, useEffect, useRef } from 'react'
import {
  fetchAdminDocuments,
  deleteAdminDocument,
  uploadPolicy,
  updateAdminDocument,
} from '../api/api'
import {
  FileText,
  Upload,
  RefreshCw,
  Trash2,
  Edit2,
  Check,
  X,
  AlertCircle,
  Clock,
  CheckCircle2,
  Loader2,
  Database,
  Layers,
} from 'lucide-react'

function formatBytes(bytes, decimals = 1) {
  if (!bytes || bytes === 0) return '0 B'
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

function formatDate(isoString) {
  if (!isoString) return '—'
  try {
    const d = new Date(isoString)
    return d.toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return isoString
  }
}

export default function AdminDashboard({ auth }) {
  const [documents, setDocuments] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [isUploading, setIsUploading] = useState(false)
  const [file, setFile] = useState(null)
  const [feedbackMessage, setFeedbackMessage] = useState(null)

  const [editingId, setEditingId] = useState(null)
  const [editValue, setEditValue] = useState('')

  const fileInputRef = useRef(null)
  const pollTimerRef = useRef(null)

  const loadDocuments = async (silent = false) => {
    if (!silent) setIsLoading(true)
    try {
      const data = await fetchAdminDocuments(auth.username, auth.password)
      setDocuments(data.documents || [])
    } catch (err) {
      if (!silent) {
        setFeedbackMessage({
          type: 'error',
          text: err.message || 'Failed to load documents from database.',
        })
      }
    } finally {
      if (!silent) setIsLoading(false)
    }
  }

  // Initial load
  useEffect(() => {
    loadDocuments()
    return () => {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current)
    }
  }, [])

  // Auto-polling when any document is in 'pending' or 'processing'
  useEffect(() => {
    const hasActiveProcessing = documents.some(
      (doc) => doc.processing_status === 'pending' || doc.processing_status === 'processing'
    )

    if (hasActiveProcessing) {
      if (!pollTimerRef.current) {
        pollTimerRef.current = setInterval(() => {
          loadDocuments(true)
        }, 2500)
      }
    } else {
      if (pollTimerRef.current) {
        clearInterval(pollTimerRef.current)
        pollTimerRef.current = null
      }
    }

    return () => {
      if (pollTimerRef.current) {
        clearInterval(pollTimerRef.current)
        pollTimerRef.current = null
      }
    }
  }, [documents])

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to permanently delete "${name || 'this document'}"?`)) return
    try {
      await deleteAdminDocument(id, auth.username, auth.password)
      setDocuments((prev) => prev.filter((d) => d.id !== id))
      setFeedbackMessage({
        type: 'success',
        text: `Document "${name}" deleted successfully.`,
      })
    } catch (err) {
      setFeedbackMessage({
        type: 'error',
        text: err.message || 'Delete failed.',
      })
    }
  }

  const handleEdit = async (id) => {
    if (!editValue.trim()) return
    try {
      await updateAdminDocument(id, editValue.trim(), auth.username, auth.password)
      setEditingId(null)
      loadDocuments(true)
      setFeedbackMessage({
        type: 'success',
        text: 'Document name updated.',
      })
    } catch (err) {
      setFeedbackMessage({
        type: 'error',
        text: err.message || 'Update failed.',
      })
    }
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!file) return

    setIsUploading(true)
    setFeedbackMessage(null)

    try {
      const res = await uploadPolicy(file, auth.username, auth.password)
      if (fileInputRef.current) fileInputRef.current.value = ''
      setFile(null)

      if (res.is_duplicate) {
        setFeedbackMessage({
          type: 'info',
          text: `Duplicate file detected: "${res.filename}" is already in the database (${res.status}).`,
        })
      } else {
        setFeedbackMessage({
          type: 'success',
          text: `"${res.filename}" uploaded successfully! Background indexing in progress...`,
        })
      }

      // Refresh list immediately so pending/processing item appears
      await loadDocuments(true)
    } catch (err) {
      setFeedbackMessage({
        type: 'error',
        text: err.message || 'Upload failed. Please check the PDF format and try again.',
      })
    } finally {
      setIsUploading(false)
    }
  }

  const totalChunks = documents.reduce((acc, doc) => acc + (doc.chunk_count || 0), 0)
  const readyDocs = documents.filter((doc) => doc.processing_status === 'completed').length

  return (
    <div className="py-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Database className="text-blue-600" size={26} />
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              Admin Knowledge Base
            </h1>
          </div>
          <p className="text-sm text-slate-600">
            Upload policy PDFs. Documents are stored permanently and indexed asynchronously into ChromaDB for AI recommendations.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => loadDocuments(false)}
            disabled={isLoading}
            className="btn btn-secondary flex items-center gap-2 text-sm shadow-sm"
            title="Refresh document status"
          >
            <RefreshCw size={14} className={isLoading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div className="card p-4 flex items-center gap-4 shadow-sm">
          <div className="p-3 bg-blue-50 text-blue-600 rounded-lg">
            <FileText size={22} />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">{documents.length}</div>
            <div className="text-xs text-slate-500 font-medium">Total Documents</div>
          </div>
        </div>

        <div className="card p-4 flex items-center gap-4 shadow-sm">
          <div className="p-3 bg-emerald-50 text-emerald-600 rounded-lg">
            <CheckCircle2 size={22} />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">{readyDocs}</div>
            <div className="text-xs text-slate-500 font-medium">Ready for RAG</div>
          </div>
        </div>

        <div className="card p-4 flex items-center gap-4 shadow-sm">
          <div className="p-3 bg-violet-50 text-violet-600 rounded-lg">
            <Layers size={22} />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">{totalChunks}</div>
            <div className="text-xs text-slate-500 font-medium">Indexed Vector Chunks</div>
          </div>
        </div>
      </div>

      {/* Feedback Alert Banner */}
      {feedbackMessage && (
        <div
          className={`p-4 rounded-lg mb-6 flex items-start justify-between gap-3 text-sm ${
            feedbackMessage.type === 'error'
              ? 'bg-red-50 text-red-800 border border-red-200'
              : feedbackMessage.type === 'info'
              ? 'bg-amber-50 text-amber-800 border border-amber-200'
              : 'bg-emerald-50 text-emerald-800 border border-emerald-200'
          }`}
        >
          <div className="flex items-center gap-2">
            {feedbackMessage.type === 'error' ? (
              <AlertCircle size={18} className="shrink-0" />
            ) : feedbackMessage.type === 'info' ? (
              <AlertCircle size={18} className="shrink-0 text-amber-600" />
            ) : (
              <CheckCircle2 size={18} className="shrink-0 text-emerald-600" />
            )}
            <span>{feedbackMessage.text}</span>
          </div>
          <button
            onClick={() => setFeedbackMessage(null)}
            className="text-slate-400 hover:text-slate-600 ml-auto"
          >
            <X size={16} />
          </button>
        </div>
      )}

      {/* Upload Box */}
      <div className="card p-6 mb-8 shadow-sm">
        <h3 className="font-bold text-slate-900 mb-1 flex items-center gap-2">
          <Upload size={18} className="text-blue-600" />
          Upload Insurance Policy PDF
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          Uploads return in under 2 seconds. PDF text extraction, chunking, and ONNX vector embeddings process smoothly in the background.
        </p>

        <form onSubmit={handleUpload} className="flex flex-col sm:flex-row gap-3">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            className="input text-sm file:mr-4 file:py-1 file:px-3 file:rounded file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            onChange={(e) => setFile(e.target.files[0] || null)}
          />
          <button
            type="submit"
            disabled={!file || isUploading}
            className="btn whitespace-nowrap flex items-center justify-center gap-2 text-sm disabled:opacity-50"
          >
            {isUploading ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload size={16} />
                Upload Policy
              </>
            )}
          </button>
        </form>
      </div>

      {/* Documents Table */}
      <div className="card overflow-hidden shadow-sm">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <h2 className="font-bold text-slate-900">Stored Policies</h2>
          <span className="text-xs text-slate-500">
            {documents.length} document{documents.length !== 1 ? 's' : ''}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm border-collapse">
            <thead className="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-600 uppercase tracking-wider">
              <tr>
                <th className="p-3.5">Document</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5">Size</th>
                <th className="p-3.5">Uploaded</th>
                <th className="p-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading && documents.length === 0 ? (
                <tr>
                  <td colSpan="5" className="p-12 text-center text-slate-500">
                    <Loader2 size={24} className="animate-spin mx-auto mb-2 text-blue-600" />
                    Loading knowledge base...
                  </td>
                </tr>
              ) : documents.length === 0 ? (
                <tr>
                  <td colSpan="5" className="p-12 text-center text-slate-400">
                    <FileText size={32} className="mx-auto mb-2 opacity-40" />
                    No policy documents found. Upload your first PDF above.
                  </td>
                </tr>
              ) : (
                documents.map((doc) => {
                  const status = doc.processing_status || 'pending'
                  const isEditing = editingId === doc.id

                  return (
                    <tr key={doc.id} className="hover:bg-slate-50/70 transition-colors">
                      {/* Document Name */}
                      <td className="p-3.5 max-w-xs">
                        {isEditing ? (
                          <div className="flex items-center gap-2">
                            <input
                              className="input text-sm py-1 px-2"
                              value={editValue}
                              onChange={(e) => setEditValue(e.target.value)}
                              autoFocus
                              onKeyDown={(e) => {
                                if (e.key === 'Enter') handleEdit(doc.id)
                                if (e.key === 'Escape') setEditingId(null)
                              }}
                            />
                            <button
                              onClick={() => handleEdit(doc.id)}
                              className="text-emerald-600 hover:text-emerald-700 p-1"
                              title="Save"
                            >
                              <Check size={16} />
                            </button>
                            <button
                              onClick={() => setEditingId(null)}
                              className="text-slate-400 hover:text-slate-600 p-1"
                              title="Cancel"
                            >
                              <X size={16} />
                            </button>
                          </div>
                        ) : (
                          <div className="flex items-start gap-2.5">
                            <FileText size={18} className="text-blue-500 shrink-0 mt-0.5" />
                            <div>
                              <div className="font-medium text-slate-900 break-words">
                                {doc.filename || doc.original_filename}
                              </div>
                              {doc.filename !== doc.original_filename && (
                                <div className="text-xs text-slate-400">
                                  Original: {doc.original_filename}
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </td>

                      {/* Status */}
                      <td className="p-3.5 whitespace-nowrap">
                        {status === 'completed' && (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                            <CheckCircle2 size={13} className="text-emerald-500" />
                            Ready ({doc.chunk_count || 0} chunks)
                          </span>
                        )}

                        {status === 'processing' && (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200 animate-pulse">
                            <Loader2 size={13} className="animate-spin text-blue-600" />
                            Indexing...
                          </span>
                        )}

                        {status === 'pending' && (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
                            <Clock size={13} className="text-amber-500" />
                            Queued
                          </span>
                        )}

                        {status === 'failed' && (
                          <span
                            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-red-50 text-red-700 border border-red-200 cursor-help"
                            title={doc.processing_error || 'Processing failed'}
                          >
                            <AlertCircle size={13} className="text-red-500" />
                            Failed
                          </span>
                        )}
                      </td>

                      {/* File Size */}
                      <td className="p-3.5 whitespace-nowrap text-xs text-slate-500">
                        {formatBytes(doc.file_size_bytes)}
                      </td>

                      {/* Upload Date */}
                      <td className="p-3.5 whitespace-nowrap text-xs text-slate-500">
                        {formatDate(doc.upload_timestamp)}
                      </td>

                      {/* Actions */}
                      <td className="p-3.5 text-right whitespace-nowrap">
                        <div className="flex items-center justify-end gap-2">
                          {!isEditing && (
                            <>
                              <button
                                onClick={() => {
                                  setEditingId(doc.id)
                                  setEditValue(doc.filename)
                                }}
                                className="p-1.5 text-slate-500 hover:text-blue-600 hover:bg-slate-100 rounded transition"
                                title="Rename document"
                              >
                                <Edit2 size={15} />
                              </button>
                              <button
                                onClick={() => handleDelete(doc.id, doc.filename)}
                                className="p-1.5 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded transition"
                                title="Delete document"
                              >
                                <Trash2 size={15} />
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
