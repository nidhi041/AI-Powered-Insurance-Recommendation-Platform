import { useState } from 'react'
import { motion } from 'framer-motion'
import { User, Calendar, Activity, Wallet, MapPin, HeartPulse, Sparkles, ShieldCheck } from 'lucide-react'

const LIFESTYLE_OPTIONS = ['Sedentary', 'Moderate', 'Active', 'Athlete']
const INCOME_OPTIONS = ['under 3L', '3-8L', '8-15L', '15L+']
const CITY_OPTIONS = ['Metro', 'Tier-2', 'Tier-3']

export default function Form({ onSubmit, isLoading }) {
  const [form, setForm] = useState({
    full_name: '',
    age: '',
    lifestyle: 'Sedentary',
    conditions: '',
    income: '3-8L',
    city: 'Metro',
  })

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({
      ...form,
      age: parseInt(form.age) || 0,
      conditions: form.conditions ? form.conditions.split(',').map(c => c.trim()) : ['None']
    })
  }

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.98 }}
      whileInView={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
      className="aww-card max-w-5xl mx-auto shadow-2xl overflow-hidden"
    >
      <div className="mb-16">
        <h2 className="text-4xl font-black text-slate-900 tracking-tight mb-3">Risk Assessment</h2>
        <p className="text-slate-500 font-medium">Input your profile to initialize the RAG retrieval engine.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-16">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-16 gap-y-12">
          {/* Full Name */}
          <div className="space-y-4">
            <label className="flex items-center gap-2 text-xs font-black text-slate-400 uppercase tracking-widest">
              <User size={14} className="text-primary" /> Full Name
            </label>
            <input
              name="full_name"
              type="text"
              required
              className="aww-input"
              placeholder="e.g. Rahul Sharma"
              value={form.full_name}
              onChange={handleChange}
            />
          </div>

          {/* Age */}
          <div className="space-y-4">
            <label className="flex items-center gap-2 text-xs font-black text-slate-400 uppercase tracking-widest">
              <Calendar size={14} className="text-primary" /> Age
            </label>
            <input
              name="age"
              type="number"
              required
              className="aww-input"
              placeholder="e.g. 28"
              value={form.age}
              onChange={handleChange}
            />
          </div>

          {/* Lifestyle */}
          <div className="space-y-4">
            <label className="flex items-center gap-2 text-xs font-black text-slate-400 uppercase tracking-widest">
              <Activity size={14} className="text-primary" /> Lifestyle
            </label>
            <select name="lifestyle" className="aww-input appearance-none bg-slate-50" value={form.lifestyle} onChange={handleChange}>
              {LIFESTYLE_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>

          {/* Income */}
          <div className="space-y-4">
            <label className="flex items-center gap-2 text-xs font-black text-slate-400 uppercase tracking-widest">
              <Wallet size={14} className="text-primary" /> Income
            </label>
            <select name="income" className="aww-input appearance-none bg-slate-50" value={form.income} onChange={handleChange}>
              {INCOME_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>

          {/* City */}
          <div className="space-y-4">
            <label className="flex items-center gap-2 text-xs font-black text-slate-400 uppercase tracking-widest">
              <MapPin size={14} className="text-primary" /> City Tier
            </label>
            <select name="city" className="aww-input appearance-none bg-slate-50" value={form.city} onChange={handleChange}>
              {CITY_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>

          {/* Conditions */}
          <div className="space-y-4">
            <label className="flex items-center gap-2 text-xs font-black text-slate-400 uppercase tracking-widest">
              <HeartPulse size={14} className="text-primary" /> Health Context
            </label>
            <input
              name="conditions"
              type="text"
              className="aww-input"
              placeholder="e.g. Diabetes, None"
              value={form.conditions}
              onChange={handleChange}
            />
          </div>
        </div>

        <div className="pt-10 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-8">
           <div className="flex items-center gap-4 text-slate-400 text-sm font-medium italic">
             <div className="w-8 h-8 rounded-full bg-emerald-50 flex items-center justify-center text-secondary">
               <ShieldCheck size={18} />
             </div>
             Encrypted session initialized
           </div>

          <motion.button 
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            type="submit" 
            disabled={isLoading} 
            className="aww-btn w-full sm:w-[320px] text-xl py-5"
          >
            {isLoading ? (
              <div className="flex items-center gap-3">
                <div className="w-6 h-6 border-4 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Scanning...</span>
              </div>
            ) : (
              <>
                Compute Recommendations
                <Sparkles size={20} />
              </>
            )}
          </motion.button>
        </div>
      </form>
    </motion.div>
  )
}
