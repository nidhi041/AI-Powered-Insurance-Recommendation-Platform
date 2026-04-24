import { useState } from 'react'

/* ------------------------------------------------------------------ */
/* Static option sets                                                    */
/* ------------------------------------------------------------------ */
const INCOME_OPTIONS = [
  'under 3L',
  '3-8L',
  '8L+',
]

const CITY_OPTIONS = [
  'Metro',
  'Tier-2',
  'Tier-3',
]

const LIFESTYLE_OPTIONS = [
  'Sedentary',
  'Active',
]

/* ------------------------------------------------------------------ */
/* Component                                                             */
/* ------------------------------------------------------------------ */
export default function Form({ onSubmit, isLoading }) {
  const [form, setForm] = useState({
    full_name: '',
    age: '',
    lifestyle: '',
    conditions: '',
    income: '',
    city: '',
  })
  const [errors, setErrors] = useState({})

  /* ---- validation ---- */
  const validate = () => {
    const errs = {}
    
    if (!form.full_name.trim()) errs.full_name = 'Full name is required'
    
    if (!form.age) {
      errs.age = 'Age is required'
    } else if (isNaN(Number(form.age)) || Number(form.age) < 1 || Number(form.age) > 100) {
      errs.age = 'Enter a valid age (1–100)'
    }
    
    if (!form.lifestyle) errs.lifestyle = 'Please select a lifestyle'
    if (!form.conditions.trim()) errs.conditions = 'Please enter health conditions (e.g. None)'
    if (!form.income) errs.income = 'Please select your income range'
    if (!form.city) errs.city = 'Please select your city'
    
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  /* ---- submit ---- */
  const handleSubmit = (e) => {
    e.preventDefault()
    if (!validate()) return

    const payload = {
      full_name: form.full_name.trim(),
      age: Number(form.age),
      lifestyle: form.lifestyle,
      conditions: [form.conditions.trim()],
      income: form.income,
      city: form.city,
    }

    onSubmit(payload)
  }

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }))
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: undefined }))
  }

  return (
    <div className="relative group">
      {/* Background glow for form */}
      <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 rounded-[28px] blur-xl opacity-50 group-hover:opacity-75 transition duration-500" />
      
      <form
        onSubmit={handleSubmit}
        noValidate
        className="relative glass-card p-8 sm:p-10 animate-fade-in-up"
      >
        {/* Header */}
        <div className="mb-10 text-center sm:text-left">
          <h2 className="text-3xl font-extrabold text-white mb-2">Build Your Profile</h2>
          <p className="text-slate-400">
            Tell us about yourself for a truly personalized insurance strategy.
          </p>
        </div>

        <div className="space-y-8">
          {/* Section: Personal Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
            <Field label="Full Name" error={errors.full_name}>
              <input
                id="full_name"
                type="text"
                className="form-input"
                placeholder="Rahul Sharma"
                value={form.full_name}
                onChange={handleChange('full_name')}
              />
            </Field>

            <Field label="Current Age" error={errors.age}>
              <input
                id="age"
                type="number"
                className="form-input"
                placeholder="28"
                min={1}
                max={100}
                value={form.age}
                onChange={handleChange('age')}
              />
            </Field>

            <Field label="Lifestyle Habit" error={errors.lifestyle}>
              <select
                id="lifestyle"
                className="form-input appearance-none"
                value={form.lifestyle}
                onChange={handleChange('lifestyle')}
              >
                <option value="">Select lifestyle</option>
                {LIFESTYLE_OPTIONS.map(opt => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            </Field>

            <Field label="Pre-existing Conditions" error={errors.conditions}>
              <input
                id="conditions"
                type="text"
                className="form-input"
                placeholder="None or specific condition"
                value={form.conditions}
                onChange={handleChange('conditions')}
              />
            </Field>

            <Field label="Annual Income Bracket" error={errors.income}>
              <select
                id="income"
                className="form-input appearance-none"
                value={form.income}
                onChange={handleChange('income')}
              >
                <option value="">Select income range</option>
                {INCOME_OPTIONS.map((o) => (
                  <option key={o} value={o}>{o}</option>
                ))}
              </select>
            </Field>

            <Field label="City Category" error={errors.city}>
              <select
                id="city"
                className="form-input appearance-none"
                value={form.city}
                onChange={handleChange('city')}
              >
                <option value="">Select city category</option>
                {CITY_OPTIONS.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </Field>
          </div>

          {/* Submit */}
          <div className="pt-4">
            <button
              id="submit-btn"
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full sm:w-auto min-w-[240px]"
            >
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  Generate AI Recommendations
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}

/* ------------------------------------------------------------------ */
/* Field wrapper                                                         */
/* ------------------------------------------------------------------ */
function Field({ label, error, className = '', children }) {
  return (
    <div className={className}>
      <label className="block text-sm font-medium text-slate-300 mb-2">
        {label}
      </label>
      {children}
      {error && (
        <p className="text-xs text-red-400 mt-1.5 flex items-center gap-1 animate-fade-in">
          <svg className="w-3.5 h-3.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          {error}
        </p>
      )}
    </div>
  )
}
