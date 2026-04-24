import { useState, useRef } from 'react'
import Form from '../components/Form'
import Table from '../components/Table'
import CoverageCard from '../components/CoverageCard'
import ChatExplainer from '../components/ChatExplainer'
import { fetchRecommendations } from '../api/api'

export default function Home() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [userProfile, setUserProfile] = useState(null)
  const resultsRef = useRef(null)

  const handleSubmit = async (data) => {
    setLoading(true)
    setError(null)
    setResult(null)
    setUserProfile(data)

    try {
      const res = await fetchRecommendations(data)
      setResult(res)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="py-10">
      <div className="mb-12">
        <h1 className="text-3xl font-bold mb-2">Policy Finder</h1>
        <p className="text-slate-600">Enter your details below to see the best insurance options for you.</p>
      </div>

      <div className="max-w-3xl mx-auto mb-20">
        <Form onSubmit={handleSubmit} isLoading={loading} />
      </div>

      {loading && (
        <div className="text-center py-20">
          <p className="text-lg font-medium">Searching for best policies...</p>
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded mb-10">
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && !loading && (
        <div ref={resultsRef} className="space-y-16">
          <div className="border-t border-slate-200 pt-16">
            <h2 className="text-2xl font-bold mb-6">Recommendations</h2>
            
            {result.why_this_policy && (
              <div className="p-6 bg-blue-50 border border-blue-100 rounded mb-12">
                <h3 className="font-bold text-blue-800 mb-2">Advisor Note:</h3>
                <p className="text-blue-900 italic">"{result.why_this_policy}"</p>
              </div>
            )}

            <div className="space-y-12">
              <div>
                <h3 className="text-xl font-bold mb-4">Comparison Table</h3>
                <Table data={result.comparison_table} />
              </div>

              <div>
                <h3 className="text-xl font-bold mb-4">Coverage Details</h3>
                <CoverageCard data={result.coverage_details} />
              </div>
            </div>
          </div>

          <div className="flex gap-4">
            <button
              onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
              className="btn btn-secondary"
            >
              Back to Top
            </button>
            <button
              onClick={() => window.print()}
              className="btn"
            >
              Print Report
            </button>
          </div>
        </div>
      )}

      {userProfile && (
        <ChatExplainer userProfile={userProfile} />
      )}
    </div>
  )
}
