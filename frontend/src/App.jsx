import { useState } from 'react'
import { Shield, Activity, LogOut } from 'lucide-react'
import Home from './pages/Home'
import Landing from './pages/Landing'
import AdminLogin from './pages/AdminLogin'
import AdminDashboard from './pages/AdminDashboard'
import { fetchAdminPolicies } from './api/api'

export default function App() {
  const [view, setView] = useState('landing')
  const [adminAuth, setAdminAuth] = useState(null)

  const handleAdminLogin = async (username, password) => {
    try {
      await fetchAdminPolicies(username, password)
      setAdminAuth({ username, password })
      setView('admin-dashboard')
    } catch (error) {
      throw error
    }
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
            <span>AarogyaAid</span>
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
                onClick={() => { setAdminAuth(null); setView('landing'); }}
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
        &copy; 2024 AarogyaAid. Simple Insurance Recommendations.
      </footer>
    </div>
  )
}
