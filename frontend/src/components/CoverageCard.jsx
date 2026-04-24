import { motion } from 'framer-motion'
import { Check, X, AlertTriangle, CreditCard, ClipboardCheck } from 'lucide-react'

const ITEMS = [
  {
    key: 'inclusions',
    label: 'Standard Inclusions',
    color: 'emerald',
    icon: <Check size={20} strokeWidth={3} />,
  },
  {
    key: 'exclusions',
    label: 'Critical Exclusions',
    color: 'rose',
    icon: <X size={20} strokeWidth={3} />,
  },
  {
    key: 'sub_limits',
    label: 'Hospital Sub-limits',
    color: 'amber',
    icon: <AlertTriangle size={20} strokeWidth={3} />,
  },
  {
    key: 'copay',
    label: 'Co-payment Clauses',
    color: 'sky',
    icon: <CreditCard size={20} strokeWidth={3} />,
  },
  {
    key: 'claim_type',
    label: 'Claim Process',
    color: 'indigo',
    icon: <ClipboardCheck size={20} strokeWidth={3} />,
  },
]

const colorMap = {
  emerald: 'text-emerald-600 bg-emerald-50',
  rose:    'text-rose-600 bg-rose-50',
  amber:   'text-amber-600 bg-amber-50',
  sky:     'text-sky-600 bg-sky-50',
  indigo:  'text-indigo-600 bg-indigo-50',
}

export default function CoverageCard({ data }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
      {ITEMS.map(({ key, label, icon, color }, idx) => (
        <motion.div 
          key={key} 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.1 }}
          viewport={{ once: true }}
          className="aww-card p-10 flex flex-col items-start gap-8 border-slate-100 hover:border-slate-200"
        >
          <div className={`w-14 h-14 rounded-2xl flex items-center justify-center shrink-0 ${colorMap[color]}`}>
            {icon}
          </div>
          <div className="space-y-4">
            <span className="text-[11px] font-black text-slate-400 uppercase tracking-[0.3em]">{label}</span>
            <p className="text-slate-900 text-lg font-bold leading-relaxed">
              {data[key] || 'Data not extracted'}
            </p>
          </div>
        </motion.div>
      ))}
    </div>
  )
}
