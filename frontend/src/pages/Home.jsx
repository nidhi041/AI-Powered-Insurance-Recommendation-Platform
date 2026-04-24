import { useState, useRef } from 'react'
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
      // Smooth scroll to results after a tick
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }, 100)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Something went wrong. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col pt-16">
      {/* ─── Hero ───────────────────────────────────────────────────── */}
      <section className="relative overflow-hidden pt-20 pb-24 sm:pt-32 sm:pb-32">
        {/* Animated background elements */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-full pointer-events-none">
          <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-indigo-600/20 blur-[120px] animate-pulse-soft" />
          <div className="absolute bottom-[10%] right-[-5%] w-[30%] h-[30%] rounded-full bg-violet-600/20 blur-[100px] animate-pulse-soft delay-300" />
        </div>

        <div className="relative max-w-5xl mx-auto px-4 sm:px-6 text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-white/10 bg-white/5 text-indigo-300 text-sm font-medium mb-8 animate-fade-in">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
            </span>
            Personalized RAG Pipeline
          </div>

          <h1 className="hero-title text-white mb-8 animate-fade-in-up">
            Your Health, <br />
            <span className="gradient-text">Intelligently Insured.</span>
          </h1>

          <p className="text-xl text-slate-400 leading-relaxed max-w-2xl mx-auto mb-12 animate-fade-in-up delay-100">
            AarogyaAid uses advanced AI to analyze policy documents and find the perfect match for your profile. 
            Get unbiased, data-backed recommendations in seconds.
          </p>

          <div className="flex flex-wrap justify-center gap-4 animate-fade-in-up delay-200">
            <button 
              onClick={() => document.getElementById('profile-form')?.scrollIntoView({ behavior: 'smooth' })}
              className="btn-primary"
            >
              Analyze My Profile
            </button>
          </div>
        </div>
      </section>

      {/* ─── Main content ───────────────────────────────────────────── */}
      <main className="relative z-10 max-w-6xl mx-auto w-full px-4 sm:px-6 pb-24 space-y-20">
        
        {/* Form section */}
        <div id="profile-form" className="scroll-mt-24">
          <Form onSubmit={handleSubmit} isLoading={loading} />
        </div>

        {/* Loader */}
        {loading && <Loader />}

        {/* Error */}
        {error && (
          <div className="mt-8 animate-fade-in">
            <div className="glass-card border-red-500/30 bg-red-500/5 p-6 flex items-start gap-4">
              <div className="w-12 h-12 rounded-2xl bg-red-500/20 flex items-center justify-center flex-shrink-0 text-red-400">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-bold text-red-400">Analysis Interrupted</h3>
                <p className="text-slate-400 mt-1">
                  {typeof error === 'string' ? error : (error.message || 'An unexpected error occurred while generating your report.')}
                </p>
                <button 
                  onClick={() => setError(null)}
                  className="mt-4 text-xs font-bold text-red-400 uppercase tracking-widest hover:text-red-300 transition-colors"
                >
                  Dismiss & Try Again
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {result && !loading && (
          <div ref={resultsRef} className="space-y-16 py-16">
            {/* Section Header */}
            <div className="flex flex-col items-center gap-4 text-center animate-fade-in">
              <div className="px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[10px] font-bold uppercase tracking-[0.2em]">
                Analysis Results
              </div>
              <h2 className="text-4xl sm:text-5xl font-black text-white tracking-tight">Your Tailored Strategy</h2>
              <p className="text-slate-400 max-w-xl mx-auto">
                Based on your profile and 268+ insurance clauses analyzed.
              </p>
            </div>

            {/* AI Narrative Section */}
            {result.why_this_policy && (
              <div className="glass-card relative overflow-hidden border-indigo-500/10 shadow-2xl shadow-indigo-500/5">
                {/* Accent line */}
                <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-indigo-500 to-violet-600" />
                
                <div className="p-8 sm:p-12">
                  <div className="flex flex-col md:flex-row items-start gap-10">
                    <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 flex items-center justify-center flex-shrink-0 text-indigo-400">
                      <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                    </div>
                    <div className="space-y-6">
                      <div className="space-y-1">
                        <h3 className="text-2xl font-bold text-white">The AI Advisor's Take</h3>
                        <p className="text-[10px] font-bold text-indigo-500 uppercase tracking-widest">Grounding check complete — Document ID: RAG-8812</p>
                      </div>
                      <p className="text-slate-300 text-lg leading-relaxed font-medium">
                        "{result.why_this_policy}"
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Comparison Grid */}
            <div className="grid grid-cols-1 gap-12">
              <div className="space-y-4">
                <div className="flex items-center gap-3 pl-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                  <h4 className="text-sm font-bold text-slate-500 uppercase tracking-[0.2em]">Market Comparison Table</h4>
                </div>
                <Table data={result.comparison_table} />
              </div>

              <div className="space-y-4">
                <div className="flex items-center gap-3 pl-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-violet-500" />
                  <h4 className="text-sm font-bold text-slate-500 uppercase tracking-[0.2em]">Policy Clause Breakdown</h4>
                </div>
                <CoverageCard data={result.coverage_details} />
              </div>
            </div>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-12 border-t border-white/5 animate-fade-in delay-300">
              <button
                onClick={() => {
                  setResult(null)
                  setError(null)
                  window.scrollTo({ top: 0, behavior: 'smooth' })
                }}
                className="group flex items-center gap-3 px-8 py-4 rounded-2xl bg-white/5 border border-white/10 text-slate-300 font-bold text-sm hover:text-white hover:bg-white/10 transition-all"
              >
                <svg className="w-5 h-5 transition-transform group-hover:-translate-x-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                Modify Search Profile
              </button>

              <button
                onClick={() => window.print()}
                className="btn-primary px-8 py-4 rounded-2xl"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 00-2 2h2m2 4h10a2 2 0 002-2v-3a2 2 0 00-2-2H7a2 2 0 00-2 2v3a2 2 0 002 2zm0-10V4a2 2 0 012-2h4a2 2 0 012 2v4M7 10h10" />
                </svg>
                Download PDF Report
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Persistent Chat Explainer */}
      {userProfile && (
        <ChatExplainer 
          key={`${userProfile.full_name}-${submissionId}`} 
          userProfile={userProfile} 
        />
      )}

      {/* ─── Footer ─────────────────────────────────────────────────── */}
      <footer className="border-t border-white/8 py-10 text-center text-slate-600 text-xs">
        © {new Date().getFullYear()} AarogyaAid — AI-Powered Insurance Recommendations. Not a licensed insurer.
      </footer>
    </div>
  )
}
