export default function Table({ data }) {
  if (!data || !data.length) return null

  const getScoreColor = (scoreStr) => {
    const score = parseInt(scoreStr.split('/')[0])
    if (isNaN(score)) return 'bg-slate-100 text-slate-600'
    
    if (score < 5) return 'bg-red-100 text-red-700'
    if (score < 8) return 'bg-amber-100 text-amber-700'
    return 'bg-emerald-100 text-emerald-700'
  }

  return (
    <div className="overflow-x-auto border border-slate-200 rounded">
      <table className="w-full text-left text-sm border-collapse">
        <thead className="bg-slate-50 border-b border-slate-200">
          <tr>
            <th className="p-3 font-bold text-slate-700">Policy Name</th>
            <th className="p-3 font-bold text-slate-700">Provider</th>
            <th className="p-3 font-bold text-slate-700">Premium</th>
            <th className="p-3 font-bold text-slate-700">Cover</th>
            <th className="p-3 font-bold text-slate-700">Waiting Period</th>
            <th className="p-3 font-bold text-slate-700">Key Benefit</th>
            <th className="p-3 font-bold text-slate-700">Match</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200">
          {data.map((policy, idx) => (
            <tr key={idx} className="hover:bg-slate-50">
              <td className="p-3 font-medium">{policy.policy_name}</td>
              <td className="p-3">{policy.insurer}</td>
              <td className="p-3 text-blue-600 font-bold">{policy.premium}</td>
              <td className="p-3">{policy.cover_amount}</td>
              <td className="p-3">{policy.waiting_period}</td>
              <td className="p-3 text-xs">{policy.key_benefit}</td>
              <td className="p-3">
                <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${getScoreColor(policy.suitability_score)}`}>
                  {policy.suitability_score}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
