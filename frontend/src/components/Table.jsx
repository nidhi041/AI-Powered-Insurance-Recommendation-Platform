function scoreClass(score) {
  const num = parseFloat(score)
  if (!isNaN(num)) {
    if (num >= 7) return 'score-high'
    if (num >= 4) return 'score-medium'
    return 'score-low'
  }
  const lower = score.toLowerCase()
  if (lower.includes('high') || lower.includes('excellent') || lower.includes('very good'))
    return 'score-high'
  if (lower.includes('medium') || lower.includes('moderate') || lower.includes('good'))
    return 'score-medium'
  return 'score-low'
}

export default function Table({ data }) {
  if (!data || !data.length) return null

  return (
    <div className="glass-card overflow-hidden border-white/5 shadow-2xl">
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b border-white/5 bg-white/[0.02]">
              {[
                'Policy Name', 'Insurer', 'Premium', 'Coverage',
                'Waiting Period', 'Key Benefit', 'Suitability',
              ].map((h) => (
                <th
                  key={h}
                  className="text-left px-6 py-5 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500 whitespace-nowrap"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {data.map((policy, idx) => (
              <tr
                key={idx}
                className="hover:bg-indigo-500/[0.03] transition-colors duration-200 group"
              >
                {/* Policy Name */}
                <td className="px-6 py-5">
                  <div className="flex flex-col gap-0.5">
                    <span className="font-bold text-white text-base group-hover:text-indigo-300 transition-colors">
                      {policy.policy_name}
                    </span>
                    <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Recommended Plan</span>
                  </div>
                </td>

                {/* Insurer */}
                <td className="px-6 py-5 text-slate-300 font-medium">
                  {policy.insurer}
                </td>

                {/* Premium */}
                <td className="px-6 py-5">
                  <div className="flex flex-col">
                    <span className="text-emerald-400 font-bold text-base">{policy.premium}</span>
                    <span className="text-[10px] text-slate-500 uppercase">per year</span>
                  </div>
                </td>

                {/* Coverage */}
                <td className="px-6 py-5 text-slate-200 font-semibold">
                  {policy.cover_amount}
                </td>

                {/* Waiting Period */}
                <td className="px-6 py-5 text-slate-400">
                  {policy.waiting_period}
                </td>

                {/* Key Benefit */}
                <td className="px-6 py-5 max-w-[240px]">
                  <p className="text-slate-400 text-xs leading-relaxed line-clamp-2 italic" title={policy.key_benefit}>
                    "{policy.key_benefit}"
                  </p>
                </td>

                {/* Suitability Score */}
                <td className="px-6 py-5">
                  <span className={`score-badge ${scoreClass(policy.suitability_score)}`}>
                    {policy.suitability_score}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

