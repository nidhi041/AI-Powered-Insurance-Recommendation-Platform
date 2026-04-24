import { useState } from 'react'

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
    <div className="card">
      <h2 className="text-2xl font-bold mb-6">User Profile</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-grid mb-6">
          <div className="space-y-1">
            <label className="text-sm font-semibold">Full Name</label>
            <input
              name="full_name"
              type="text"
              required
              className="input"
              value={form.full_name}
              onChange={handleChange}
            />
          </div>

          <div className="space-y-1">
            <label className="text-sm font-semibold">Age</label>
            <input
              name="age"
              type="number"
              required
              className="input"
              value={form.age}
              onChange={handleChange}
            />
          </div>

          <div className="space-y-1">
            <label className="text-sm font-semibold">Lifestyle</label>
            <select name="lifestyle" className="input" value={form.lifestyle} onChange={handleChange}>
              {LIFESTYLE_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-sm font-semibold">Income Bracket</label>
            <select name="income" className="input" value={form.income} onChange={handleChange}>
              {INCOME_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-sm font-semibold">City Tier</label>
            <select name="city" className="input" value={form.city} onChange={handleChange}>
              {CITY_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </div>

          <div className="space-y-1">
            <label className="text-sm font-semibold">Medical Conditions (comma separated)</label>
            <input
              name="conditions"
              type="text"
              className="input"
              placeholder="e.g. Diabetes, None"
              value={form.conditions}
              onChange={handleChange}
            />
          </div>
        </div>

        <button 
          type="submit" 
          disabled={isLoading} 
          className="btn w-full py-3"
        >
          {isLoading ? 'Processing...' : 'Get Recommendations'}
        </button>
      </form>
    </div>
  )
}
