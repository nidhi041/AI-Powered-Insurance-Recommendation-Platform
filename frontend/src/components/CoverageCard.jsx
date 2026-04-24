const ITEMS = [
  { key: 'inclusions', label: 'Inclusions' },
  { key: 'exclusions', label: 'Exclusions' },
  { key: 'sub_limits', label: 'Sub-limits' },
  { key: 'copay', label: 'Co-payment' },
  { key: 'claim_type', label: 'Claim Process' },
]

export default function CoverageCard({ data }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {ITEMS.map(({ key, label }) => (
        <div key={key} className="card">
          <h4 className="text-sm font-bold text-slate-800 mb-2 border-b border-slate-100 pb-2">{label}</h4>
          <p className="text-sm text-slate-600">
            {data[key] || 'N/A'}
          </p>
        </div>
      ))}
    </div>
  )
}
