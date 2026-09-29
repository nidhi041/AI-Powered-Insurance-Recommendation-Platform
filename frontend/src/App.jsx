import { useState, useEffect } from 'react'
import { Shield, Activity, LogOut } from 'lucide-react'
import Home from './pages/Home'
import Landing from './pages/Landing'
import AdminLogin from './pages/AdminLogin'
import AdminDashboard from './pages/AdminDashboard'
import { fetchAdminDocuments } from './api/api'

const ADMIN_AUTH_KEY = 'insureiq_admin_auth'

export default function App() {
  // Restore admin session from localStorage on first load
  const [adminAuth, setAdminAuth] = useState(() => {
    try {
      const saved = localStorage.getItem(ADMIN_AUTH_KEY)
      return saved ? JSON.parse(saved) : null
    } catch {
      return null
    }
  })

  // If there's a saved admin session, start directly on the dashboard
  const [view, setView] = useState(() => {
    try {
      const saved = localStorage.getItem(ADMIN_AUTH_KEY)
      return saved ? 'admin-dashboard' : 'landing'
    } catch {
      return 'landing'
    }
  })

  const handleAdminLogin = async (username, password) => {
    try {
      await fetchAdminDocuments(username, password)
      const auth = { username, password }
      setAdminAuth(auth)
      localStorage.setItem(ADMIN_AUTH_KEY, JSON.stringify(auth))
      setView('admin-dashboard')
    } catch (error) {
      throw error
    }
  }

  const handleSignOut = () => {
    setAdminAuth(null)
    localStorage.removeItem(ADMIN_AUTH_KEY)
    setView('landing')
  }

  const navigateTo = (newView) => {
    window.scrollTo(0, 0)
    setView(newView)
  }

  const renderView = () => {
    switch (view) {
      case 'landing': return <Landing onSelectUser={() => navigateTo('user')} onSelectAdmin={() => navigateTo('admin-login')} />
      case 'user': return <Home />
      case 'admin-login': return <AdminLogin onLogin={handleAdminLogin} />
      case 'admin-dashboard': return adminAuth ? <AdminDashboard auth={adminAuth} /> : null
      default: return null
    }
  }

  return (
    <div className="min-h-screen">
      <nav className="navbar">
        <div className="container nav-content">
          <div className="logo flex items-center gap-2 cursor-pointer" onClick={() => setView('landing')}>
            <Shield size={24} />
            <span>insureiq</span>
          </div>

          <div className="flex items-center gap-6">
            {view !== 'landing' && (
              <button 
                onClick={() => setView('landing')}
                className="text-sm text-slate-600 hover:underline"
              >
                Back home
              </button>
            )}
            
            <div className="flex items-center gap-2 text-xs text-slate-500 font-medium">
              <Activity size={14} />
              <span>{view.includes('admin') ? 'ADMIN MODE' : 'USER MODE'}</span>
            </div>

            {adminAuth && (
              <button 
                onClick={handleSignOut}
                className="text-red-600 text-sm hover:underline"
              >
                Sign Out
              </button>
            )}
          </div>
        </div>
      </nav>

      <main className="container">
        {renderView()}
      </main>

      <footer className="container py-10 mt-20 border-t border-slate-200 text-center text-sm text-slate-500">
        &copy; 2024 insureiq. Simple Insurance Recommendations.
      </footer>
    </div>
  )
}
