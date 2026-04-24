const ITEMS = [
  {
    key: 'inclusions',
    label: 'Inclusions',
    accent: 'emerald',
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
  {
    key: 'exclusions',
    label: 'Exclusions',
    accent: 'red',
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
      </svg>
    ),
  },
  {
    key: 'sub_limits',
    label: 'Sub-limits',
    accent: 'amber',
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
      </svg>
    ),
  },
  {
    key: 'copay',
    label: 'Co-pay',
    accent: 'sky',
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75" />
      </svg>
    ),
  },
  {
    key: 'claim_type',
    label: 'Claim Type',
    accent: 'violet',
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25zM6.75 12h.008v.008H6.75V12zm0 3h.008v.008H6.75V15zm0 3h.008v.008H6.75V18z" />
      </svg>
    ),
  },
]

const accentMap = {
  emerald: { bg: 'bg-emerald-500/15', text: 'text-emerald-400', border: 'border-emerald-500/25' },
  red:     { bg: 'bg-red-500/15',     text: 'text-red-400',     border: 'border-red-500/25'     },
  amber:   { bg: 'bg-amber-500/15',   text: 'text-amber-400',   border: 'border-amber-500/25'   },
  sky:     { bg: 'bg-sky-500/15',     text: 'text-sky-400',     border: 'border-sky-500/25'     },
  violet:  { bg: 'bg-violet-500/15',  text: 'text-violet-400',  border: 'border-violet-500/25'  },
}

export default function CoverageCard({ data }) {
  return (
    <div className="space-y-8">
      {/* Grid of detail cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {ITEMS.map(({ key, label, icon, accent }) => {
          const colors = accentMap[accent]
          return (
            <div
              key={key}
              className={`group glass-card p-6 flex flex-col gap-4 hover:border-white/20 hover:bg-white/[0.05] transition-all duration-300`}
            >
              <div className={`w-12 h-12 rounded-2xl ${colors.bg} ${colors.text} flex items-center justify-center transition-transform group-hover:scale-110 duration-500`}>
                {icon}
              </div>
              <div className="space-y-1">
                <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">{label}</span>
                <p className="text-white text-base font-semibold leading-relaxed">
                  {data[key] || 'Not specified'}
                </p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

