export default function Landing({ onSelectUser, onSelectAdmin }) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden px-4">
      {/* Background Effects */}
      <div className="absolute inset-0 z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-indigo-600/10 blur-[120px] animate-pulse-soft" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-violet-600/10 blur-[120px] animate-pulse-soft delay-500" />
      </div>

      <div className="relative z-10 max-w-4xl w-full text-center space-y-12">
        <div className="space-y-6 animate-fade-in-up">
          <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full border border-white/10 bg-white/5 backdrop-blur-md shadow-xl">
            <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
              <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <span className="text-sm font-bold tracking-widest text-indigo-300 uppercase">AarogyaAid Platform</span>
          </div>

          <h1 className="hero-title text-white">
            Smart Insurance <br />
            <span className="gradient-text">For Everyone.</span>
          </h1>
          
          <p className="text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed">
            Choose your portal to get started. Use the AI Advisor for personalized health coverage or manage the knowledge base as an administrator.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 animate-fade-in-up delay-200">
          {/* User Portal Card */}
          <button 
            onClick={onSelectUser}
            className="group relative glass-card p-10 border-indigo-500/20 hover:border-indigo-500/50 hover:bg-indigo-500/5 transition-all duration-500 text-left overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 blur-3xl -translate-y-1/2 translate-x-1/2 group-hover:bg-indigo-500/20 transition-colors" />
            
            <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 mb-8 group-hover:scale-110 group-hover:bg-indigo-500 group-hover:text-white transition-all duration-500 shadow-lg shadow-indigo-500/0 group-hover:shadow-indigo-500/20">
              <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            
            <h3 className="text-2xl font-bold text-white mb-4">User Portal</h3>
            <p className="text-slate-400 mb-8 leading-relaxed">Get personalized insurance recommendations powered by RAG and session-aware AI.</p>
            
            <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm">
              Launch AI Advisor
              <svg className="w-4 h-4 transition-transform group-hover:translate-x-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </div>
          </button>

          {/* Admin Panel Card */}
          <button 
            onClick={onSelectAdmin}
            className="group relative glass-card p-10 border-violet-500/20 hover:border-violet-500/50 hover:bg-violet-500/5 transition-all duration-500 text-left overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-violet-500/10 blur-3xl -translate-y-1/2 translate-x-1/2 group-hover:bg-violet-500/20 transition-colors" />

            <div className="w-16 h-16 rounded-2xl bg-violet-500/10 flex items-center justify-center text-violet-400 mb-8 group-hover:scale-110 group-hover:bg-violet-500 group-hover:text-white transition-all duration-500 shadow-lg shadow-violet-500/0 group-hover:shadow-violet-500/20">
              <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            
            <h3 className="text-2xl font-bold text-white mb-4">Admin Panel</h3>
            <p className="text-slate-400 mb-8 leading-relaxed">Manage policy documents, update knowledge base, and monitor system data.</p>
            
            <div className="flex items-center gap-2 text-violet-400 font-bold text-sm">
              Access Dashboard
              <svg className="w-4 h-4 transition-transform group-hover:translate-x-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </div>
          </button>
        </div>
      </div>
    </div>
  )
}
