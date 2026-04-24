import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, ArrowLeft, Download, Search, Info, TrendingUp, ShieldCheck } from 'lucide-react'
import Form from '../components/Form'
import Table from '../components/Table'
import CoverageCard from '../components/CoverageCard'
import Loader from '../components/Loader'
import ChatExplainer from '../components/ChatExplainer'
import { fetchRecommendations } from '../api/api'

export default function Home() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [userProfile, setUserProfile] = useState(null)
  const [submissionId, setSubmissionId] = useState(0)
  const resultsRef = useRef(null)

  const handleSubmit = async (data) => {
    setLoading(true)
    setError(null)
    setResult(null)
    setUserProfile(data)
    setSubmissionId(prev => prev + 1)

    try {
      const res = await fetchRecommendations(data)
      setResult(res)
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }, 100)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-8 py-20 bg-white">
      <main className="space-y-32">
        
        {/* Intro Section */}
        <section className="text-center space-y-8 max-w-4xl mx-auto">
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="inline-flex items-center gap-3 px-4 py-1.5 rounded-full bg-blue-50 text-primary text-[11px] font-black uppercase tracking-[0.2em]"
          >
            <ShieldCheck size={14} />
            Unbiased AI Protocol v4.0
          </motion.div>
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-6xl font-black text-slate-900 tracking-tight leading-tight"
          >
            Personalized <span className="aww-gradient-text">Policy Intelligence.</span>
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-xl text-slate-400 font-medium leading-relaxed"
          >
            Initialize your profile to run a real-time retrieval-augmented analysis across 250+ insurance documents.
          </motion.p>
        </section>

        {/* Input Section */}
        <section id="profile-form">
          <Form onSubmit={handleSubmit} isLoading={loading} />
        </section>

        {/* Loader Overlay */}
        <AnimatePresence>
          {loading && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center py-32 space-y-10"
            >
              <Loader />
              <div className="text-center space-y-2">
                <p className="text-sm font-black text-primary uppercase tracking-[0.3em] animate-pulse">Analyzing Knowledge Graph</p>
                <p className="text-xs text-slate-400 font-bold">Document IDs: SEC-402, CL-981, HLT-002...</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error Handle */}
        {error && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="aww-card border-red-100 bg-red-50/30 flex items-start gap-8 max-w-3xl mx-auto"
          >
            <div className="w-14 h-14 rounded-full bg-red-100 flex items-center justify-center text-red-500 shrink-0">
              <Info size={24} />
            </div>
            <div>
              <h3 className="text-2xl font-black text-red-600 mb-2">Protocol Interrupted</h3>
              <p className="text-slate-500 font-medium leading-relaxed">{error}</p>
              <button onClick={() => window.location.reload()} className="mt-6 aww-btn aww-btn-secondary px-6 py-2 text-xs uppercase tracking-widest">Restart Analysis</button>
            </div>
          </motion.div>
        )}

        {/* Results Strategy */}
        <AnimatePresence>
          {result && !loading && (
            <motion.div 
              ref={resultsRef} 
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="space-y-40 py-20 scroll-mt-24"
            >
              {/* Report Header */}
              <div className="flex flex-col items-center text-center space-y-6">
                <div className="w-1.5 h-20 bg-gradient-to-b from-primary to-transparent rounded-full" />
                <h2 className="text-5xl font-black text-slate-900 tracking-tighter">Analysis Strategy</h2>
                <p className="text-slate-400 font-bold uppercase tracking-[0.2em] text-xs">Generated for {userProfile.full_name} • Ref: AI-{submissionId}</p>
              </div>

              {/* Narrative Card */}
              {result.why_this_policy && (
                <div className="aww-card bg-slate-50 border-none relative group overflow-hidden">
                   <div className="absolute top-0 right-0 p-8 text-primary/10 group-hover:text-primary/20 transition-colors">
                     <Sparkles size={120} />
                   </div>
                   
                   <div className="flex flex-col md:flex-row gap-16 relative z-10">
                      <div className="w-24 h-24 rounded-[32px] bg-primary flex items-center justify-center text-white shrink-0 shadow-2xl shadow-primary/30">
                        <TrendingUp size={40} strokeWidth={2.5} />
                      </div>
                      
                      <div className="space-y-8">
                         <div className="inline-flex items-center gap-3 px-3 py-1 rounded-lg bg-primary/10 text-primary text-[10px] font-black uppercase tracking-widest">
                           AI Advisor Recommendation
                         </div>
                         <h3 className="text-4xl font-black text-slate-900 leading-tight">Advisor Insight</h3>
                         <p className="text-slate-600 text-2xl leading-relaxed font-medium italic border-l-8 border-primary/10 pl-10">
                           "{result.why_this_policy}"
                         </p>
                      </div>
                   </div>
                </div>
              )}

              {/* Comparison Section */}
              <div className="space-y-12">
                 <div className="flex items-end justify-between px-6">
                    <div className="space-y-2">
                       <h4 className="text-xs font-black text-primary uppercase tracking-[0.3em]">Dataset Analysis</h4>
                       <h2 className="text-4xl font-black text-slate-900">Policy Benchmarks</h2>
                    </div>
                    <div className="hidden sm:flex items-center gap-4 text-slate-300 font-bold uppercase text-[10px] tracking-widest">
                      <Search size={14} />
                      Context Match Optimized
                    </div>
                 </div>
                 <Table data={result.comparison_table} />
              </div>

              {/* Clause Detail Grid */}
              <div className="space-y-12">
                 <div className="flex items-end justify-between px-6">
                    <div className="space-y-2">
                       <h4 className="text-xs font-black text-secondary uppercase tracking-[0.3em]">Knowledge Extraction</h4>
                       <h2 className="text-4xl font-black text-slate-900">Granular Clauses</h2>
                    </div>
                 </div>
                 <CoverageCard data={result.coverage_details} />
              </div>

              {/* Global Actions */}
              <div className="flex flex-col items-center gap-10 py-20 border-t border-slate-100">
                <div className="text-center space-y-2">
                  <h3 className="text-2xl font-black text-slate-900">Finalize Decision</h3>
                  <p className="text-slate-400 font-medium">Download your report or modify the risk parameters.</p>
                </div>
                
                <div className="flex flex-wrap justify-center gap-6">
                  <button
                    onClick={() => {
                      setResult(null)
                      setError(null)
                      window.scrollTo({ top: 0, behavior: 'smooth' })
                    }}
                    className="aww-btn aww-btn-secondary px-10 py-5"
                  >
                    <ArrowLeft size={20} />
                    Modify Search
                  </button>

                  <button
                    onClick={() => window.print()}
                    className="aww-btn px-10 py-5"
                  >
                    Generate PDF
                    <Download size={20} />
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

      </main>

      {/* Persistent Chat Intelligence */}
      {userProfile && (
        <ChatExplainer 
          key={`${userProfile.full_name}-${submissionId}`} 
          userProfile={userProfile} 
        />
      )}
    </div>
  )
}
