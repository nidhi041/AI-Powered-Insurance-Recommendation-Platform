import { useState } from 'react'
import Home from './pages/Home'
import Landing from './pages/Landing'
import AdminLogin from './pages/AdminLogin'
import AdminDashboard from './pages/AdminDashboard'
import { fetchAdminPolicies } from './api/api'

export default function App() {
  const [view, setView] = useState('landing') // landing, user, admin-login, admin-dashboard
  const [adminAuth, setAdminAuth] = useState(null)

  const handleAdminLogin = async (username, password) => {
    await fetchAdminPolicies(username, password)
    setAdminAuth({ username, password })
    setView('admin-dashboard')
  }

  const navigateTo = (newView) => {
    window.scrollTo(0, 0)
    setView(newView)
  }

  const renderView = () => {
    if (view === 'landing') return <Landing onSelectUser={() => navigateTo('user')} onSelectAdmin={() => navigateTo('admin-login')} />
    if (view === 'user') return <Home />
    if (view === 'admin-login') return <AdminLogin onLogin={handleAdminLogin} />
    if (view === 'admin-dashboard' && adminAuth) return <AdminDashboard auth={adminAuth} />
    return null
  }

  return (
    <div className="min-h-screen text-slate-200">
      {/* ─── Global Navigation ────────────────────────────────────────── */}
      <nav className="fixed top-0 left-0 w-full z-[100] backdrop-blur-md border-b border-white/5 bg-[#030712]/60">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div 
            className="flex items-center gap-3 cursor-pointer group"
            onClick={() => setView('landing')}
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-110 transition-transform">
              <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <span className="text-xl font-black tracking-tighter text-white">
              Aarogya<span className="text-indigo-400">Aid</span>
            </span>
          </div>

          <div className="flex items-center gap-4">
            {view !== 'landing' && (
              <button 
                onClick={() => setView('landing')}
                className="text-xs font-bold text-slate-400 hover:text-white transition-colors uppercase tracking-widest"
              >
                Switch Portal
              </button>
            )}
            <div className="h-4 w-px bg-white/10" />
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest bg-white/5 px-3 py-1 rounded-full border border-white/5">
              {view === 'admin-dashboard' || view === 'admin-login' ? 'Admin Node' : 'User Node'}
            </span>
          </div>
        </div>
      </nav>

      <div className="pt-20">
        {renderView()}
      </div>
    </div>
  )
}
