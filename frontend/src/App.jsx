import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Shield, Activity, Lock, ArrowRight, Menu, LogOut } from 'lucide-react'
import Home from './pages/Home'
import Landing from './pages/Landing'
import AdminLogin from './pages/AdminLogin'
import AdminDashboard from './pages/AdminDashboard'
import { fetchAdminPolicies } from './api/api'

export default function App() {
  const [view, setView] = useState('landing')
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
    switch (view) {
      case 'landing': return <Landing onSelectUser={() => navigateTo('user')} onSelectAdmin={() => navigateTo('admin-login')} />
      case 'user': return <Home />
      case 'admin-login': return <AdminLogin onLogin={handleAdminLogin} />
      case 'admin-dashboard': return adminAuth ? <AdminDashboard auth={adminAuth} /> : null
      default: return null
    }
  }

  return (
    <div className="min-h-screen bg-white">
      {/* ─── Awwwards Minimalist Nav ──────────────────────────────────── */}
      <motion.nav 
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ type: 'spring', stiffness: 100, damping: 20 }}
        className="aww-nav"
      >
        <div className="aww-logo cursor-pointer group" onClick={() => setView('landing')}>
          <motion.div 
            whileHover={{ rotate: 180 }}
            className="w-12 h-12 rounded-2xl bg-primary flex items-center justify-center text-white"
          >
            <Shield size={28} strokeWidth={3} />
          </motion.div>
          <span className="tracking-tighter">
            Aarogya<span className="text-secondary">Aid</span>
          </span>
        </div>

        <div className="flex items-center gap-12">
          {view !== 'landing' && (
            <button 
              onClick={() => setView('landing')}
              className="text-sm font-bold text-slate-500 hover:text-primary transition-colors flex items-center gap-2"
            >
              <motion.span whileHover={{ x: -4 }}>Back home</motion.span>
            </button>
          )}
          
          <div className="hidden md:flex items-center gap-3 px-6 py-2 rounded-full bg-slate-50 border border-slate-100">
            <Activity size={14} className="text-secondary animate-pulse" />
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-widest">
              {view.includes('admin') ? 'Admin Core' : 'Advisor Node'}
            </span>
          </div>

          {adminAuth && (
            <button 
              onClick={() => { setAdminAuth(null); setView('landing'); }}
              className="p-3 rounded-full hover:bg-red-50 transition-colors text-red-500"
              title="Sign Out"
            >
              <LogOut size={20} />
            </button>
          )}
        </div>
      </motion.nav>

      <div className="pt-[90px]">
        <AnimatePresence mode="wait">
          <motion.div
            key={view}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          >
            {renderView()}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  )
}
