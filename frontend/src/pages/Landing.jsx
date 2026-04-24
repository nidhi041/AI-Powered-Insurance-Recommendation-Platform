import { motion } from 'framer-motion'
import { ArrowRight, User, ShieldCheck, Database, Zap } from 'lucide-react'

export default function Landing({ onSelectUser, onSelectAdmin }) {
  return (
    <div className="min-h-[calc(100vh-90px)] flex flex-col items-center justify-center bg-white overflow-hidden">
      {/* Background Decorative Element */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 0.4, scale: 1 }}
        transition={{ duration: 2, ease: "easeOut" }}
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-50 rounded-full blur-[120px] -z-10"
      />

      <div className="max-w-6xl w-full px-6 py-20 text-center">
        {/* Badge */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-2 px-6 py-2 rounded-full bg-slate-50 border border-slate-100 text-primary text-xs font-bold uppercase tracking-[0.2em] mb-10"
        >
          <Zap size={14} fill="currentColor" />
          RAG-Powered Intelligence
        </motion.div>

        {/* Hero Title */}
        <motion.h1 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1 }}
          className="text-7xl sm:text-8xl font-black text-slate-900 mb-10 tracking-tight leading-[0.9]"
        >
          Your health. <br />
          <span className="aww-gradient-text">Intelligently</span> insured.
        </motion.h1>
        
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.4 }}
          className="text-xl text-slate-500 max-w-3xl mx-auto mb-16 leading-relaxed font-medium"
        >
          AarogyaAid analyzes thousands of policy clauses to find the coverage 
          that fits your life, not just your budget.
        </motion.p>

        {/* Portals Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-10 max-w-5xl mx-auto">
          {/* Member Advisor */}
          <motion.div 
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="aww-card text-left group"
          >
            <div className="w-16 h-16 rounded-3xl bg-blue-50 flex items-center justify-center text-primary mb-10 group-hover:bg-primary group-hover:text-white transition-all duration-500">
              <User size={32} strokeWidth={2.5} />
            </div>
            <h2 className="text-3xl font-black text-slate-900 mb-4 tracking-tight">Member Advisor</h2>
            <p className="text-slate-500 mb-12 text-lg leading-relaxed">
              Scan your profile against our knowledge base to get a personalized suitability report.
            </p>
            <button onClick={onSelectUser} className="aww-btn w-full">
              Launch Advisor
              <ArrowRight size={20} />
            </button>
          </motion.div>

          {/* Admin Node */}
          <motion.div 
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.7 }}
            className="aww-card text-left group"
          >
            <div className="w-16 h-16 rounded-3xl bg-emerald-50 flex items-center justify-center text-secondary mb-10 group-hover:bg-secondary group-hover:text-white transition-all duration-500">
              <Database size={32} strokeWidth={2.5} />
            </div>
            <h2 className="text-3xl font-black text-slate-900 mb-4 tracking-tight">System Node</h2>
            <p className="text-slate-500 mb-12 text-lg leading-relaxed">
              Manage policy documents and maintain the retrieval-augmented knowledge base.
            </p>
            <button onClick={onSelectAdmin} className="aww-btn aww-btn-secondary w-full">
              Manage Infrastructure
              <ShieldCheck size={20} />
            </button>
          </motion.div>
        </div>
      </div>

      {/* Trust Indicator */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 1.2 }}
        className="pb-10 text-slate-300 text-[10px] font-bold uppercase tracking-[0.4em]"
      >
        Verified Knowledge Base • DeepRAG Engine • 2024
      </motion.div>
    </div>
  )
}
