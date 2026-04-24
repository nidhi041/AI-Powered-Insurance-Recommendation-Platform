import { motion } from 'framer-motion'
import { CheckCircle2, AlertCircle, HelpCircle } from 'lucide-react'

function scoreClass(score) {
  const num = parseFloat(score)
  if (!isNaN(num)) {
    if (num >= 7) return { color: 'text-emerald-600 bg-emerald-50', icon: <CheckCircle2 size={14} /> }
    if (num >= 4) return { color: 'text-amber-600 bg-amber-50', icon: <AlertCircle size={14} /> }
    return { color: 'text-rose-600 bg-rose-50', icon: <HelpCircle size={14} /> }
  }
  const lower = score.toLowerCase()
  if (lower.includes('high') || lower.includes('excellent'))
    return { color: 'text-emerald-600 bg-emerald-50', icon: <CheckCircle2 size={14} /> }
  if (lower.includes('medium') || lower.includes('good'))
    return { color: 'text-amber-600 bg-amber-50', icon: <AlertCircle size={14} /> }
  return { color: 'text-rose-600 bg-rose-50', icon: <HelpCircle size={14} /> }
}

export default function Table({ data }) {
  if (!data || !data.length) return null

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="aww-card p-0 overflow-hidden border-slate-100"
    >
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="bg-slate-50/50 border-b border-slate-100">
              {[
                'Policy Name', 'Provider', 'Premium', 'Cover',
                'Waiting', 'Key Advantage', 'Match'
              ].map((h) => (
                <th
                  key={h}
                  className="text-left px-8 py-6 text-[10px] font-black uppercase tracking-[0.3em] text-slate-400 whitespace-nowrap"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {data.map((policy, idx) => {
              const status = scoreClass(policy.suitability_score)
              return (
                <motion.tr 
                  key={idx} 
                  initial={{ opacity: 0, x: -10 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className="hover:bg-slate-50/50 transition-colors group"
                >
                  <td className="px-8 py-8">
                    <span className="font-black text-slate-900 block truncate max-w-[200px]" title={policy.policy_name}>
                      {policy.policy_name}
                    </span>
                  </td>
                  <td className="px-8 py-8 text-slate-500 font-bold whitespace-nowrap">
                    {policy.insurer}
                  </td>
                  <td className="px-8 py-8">
                    <span className="text-primary font-black text-lg">{policy.premium}</span>
                  </td>
                  <td className="px-8 py-8 text-slate-700 font-bold whitespace-nowrap">
                    {policy.cover_amount}
                  </td>
                  <td className="px-8 py-8 text-slate-400 font-medium whitespace-nowrap">
                    {policy.waiting_period}
                  </td>
                  <td className="px-8 py-8 max-w-[220px]">
                    <p className="text-slate-500 text-xs leading-relaxed italic truncate" title={policy.key_benefit}>
                      "{policy.key_benefit}"
                    </p>
                  </td>
                  <td className="px-8 py-8">
                    <div className={`inline-flex items-center gap-2 px-4 py-1.5 rounded-full font-black text-[10px] uppercase tracking-widest ${status.color}`}>
                      {status.icon}
                      {policy.suitability_score}
                    </div>
                  </td>
                </motion.tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </motion.div>
  )
}
