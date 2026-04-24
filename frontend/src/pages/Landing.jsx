import { ArrowRight, User, Database } from 'lucide-react'

export default function Landing({ onSelectUser, onSelectAdmin }) {
  return (
    <div className="py-20 text-center">
      <h1 className="text-4xl font-bold text-slate-900 mb-4">
        Health Insurance Recommendations
      </h1>
      <p className="text-lg text-slate-600 mb-12 max-w-2xl mx-auto">
        A simple platform to help you find the right insurance policy based on your profile and health history.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
        <div className="card text-left">
          <div className="mb-4 text-blue-600">
            <User size={32} />
          </div>
          <h2 className="text-xl font-bold mb-2">Member Portal</h2>
          <p className="text-slate-600 mb-6">
            Get personalized insurance recommendations based on your age, lifestyle, and health context.
          </p>
          <button onClick={onSelectUser} className="btn w-full flex items-center justify-center gap-2">
            Go to Portal
            <ArrowRight size={18} />
          </button>
        </div>

        <div className="card text-left">
          <div className="mb-4 text-emerald-600">
            <Database size={32} />
          </div>
          <h2 className="text-xl font-bold mb-2">Admin Portal</h2>
          <p className="text-slate-600 mb-6">
            Upload and manage policy documents in the system knowledge base.
          </p>
          <button onClick={onSelectAdmin} className="btn btn-secondary w-full flex items-center justify-center gap-2">
            Go to Admin
            <Database size={18} />
          </button>
        </div>
      </div>
    </div>
  )
}
