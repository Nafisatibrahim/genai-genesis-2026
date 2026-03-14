import { useState, useEffect } from 'react'
import { FLEXCARE_SESSION_KEY } from './UserProfileForm'

const PROVIDER_TYPE_LABELS = {
  physio: 'Physiotherapy',
  chiro: 'Chiropractic',
  massage: 'Massage therapy',
  urgent: 'Urgent / emergency care',
  none: 'None',
}

const inputCls = "rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent transition"

export default function ReferralBlock({ referral, apiUrl }) {
  const [providers, setProviders] = useState([])
  const [coverage, setCoverage] = useState(null)
  const [loadingProviders, setLoadingProviders] = useState(false)
  const [loadingCoverage, setLoadingCoverage] = useState(false)
  const [insurers, setInsurers] = useState([])
  const [plans, setPlans] = useState([])
  const [selectedInsurer, setSelectedInsurer] = useState('sunlife')
  const [selectedPlan, setSelectedPlan] = useState('')
  const [explainLoading, setExplainLoading] = useState(false)
  const [explainResult, setExplainResult] = useState(null)
  const [explainQuestion, setExplainQuestion] = useState(null)
  const [costEstimate, setCostEstimate] = useState(null)

  const showProvidersAndCoverage = referral?.provider_type && referral.provider_type !== 'none'

  useEffect(() => {
    if (!showProvidersAndCoverage || !apiUrl) return
    setLoadingProviders(true)
    setLoadingCoverage(true)
    const type = referral.provider_type

    fetch(`${apiUrl}/referral/providers?provider_type=${encodeURIComponent(type)}`)
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then((data) => setProviders(data.providers || []))
      .catch(() => setProviders([]))
      .finally(() => setLoadingProviders(false))

    fetch(`${apiUrl}/referral/coverage?provider_type=${encodeURIComponent(type)}`)
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then(setCoverage)
      .catch(() => setCoverage(null))
      .finally(() => setLoadingCoverage(false))
  }, [showProvidersAndCoverage, referral?.provider_type, apiUrl])

  useEffect(() => {
    if (!apiUrl) return
    fetch(`${apiUrl}/referral/insurers`)
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then((data) => setInsurers(data.insurers || []))
      .catch(() => setInsurers([]))
  }, [apiUrl])

  useEffect(() => {
    if (!apiUrl || !selectedInsurer) {
      setPlans([])
      setSelectedPlan('')
      return
    }
    fetch(`${apiUrl}/referral/plans?insurer_slug=${encodeURIComponent(selectedInsurer)}`)
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then((data) => {
        const planList = data.plans || []
        setPlans(planList)
        setSelectedPlan((prev) => (planList.some((p) => p.slug === prev) ? prev : ''))
      })
      .catch(() => setPlans([]))
  }, [apiUrl, selectedInsurer])

  useEffect(() => {
    if (!showProvidersAndCoverage || !apiUrl) return
    try {
      const sessionId = localStorage.getItem(FLEXCARE_SESSION_KEY)
      if (!sessionId) return
      fetch(`${apiUrl}/profile?session_id=${encodeURIComponent(sessionId)}`)
        .then((res) => (res.ok ? res.json() : Promise.reject()))
        .then((data) => {
          const p = data.profile
          if (p?.insurer_slug) setSelectedInsurer(p.insurer_slug)
          if (p?.plan_slug) setSelectedPlan(p.plan_slug)
        })
        .catch(() => {})
    } catch { }
  }, [showProvidersAndCoverage, apiUrl])

  useEffect(() => {
    if (!apiUrl || !selectedPlan || !referral?.provider_type || referral.provider_type === 'urgent') {
      setCostEstimate(null)
      return
    }
    fetch(`${apiUrl}/referral/cost-estimate?plan_slug=${encodeURIComponent(selectedPlan)}&provider_type=${encodeURIComponent(referral.provider_type)}`)
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then((data) => setCostEstimate(Object.keys(data).length ? data : null))
      .catch(() => setCostEstimate(null))
  }, [apiUrl, selectedPlan, referral?.provider_type])

  const handleExplain = (question) => {
    if (!apiUrl || !selectedPlan || !referral?.provider_type) return
    setExplainQuestion(question)
    setExplainLoading(true)
    setExplainResult(null)
    fetch(`${apiUrl}/referral/explain`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider_type: referral.provider_type, plan_slug: selectedPlan, question }),
    })
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then((data) => setExplainResult(data.explanation || ''))
      .catch(() => setExplainResult('Could not load explanation. Please try again.'))
      .finally(() => setExplainLoading(false))
  }

  return (
    <div className="rounded-2xl overflow-hidden border border-orange-100 shadow-sm">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-500 to-amber-500 px-5 py-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"/>
            </svg>
          </div>
          <div>
            <p className="text-white font-semibold text-sm">Specialist Referral</p>
            <p className="text-orange-100 text-xs">{PROVIDER_TYPE_LABELS[referral.provider_type] ?? referral.provider_type}</p>
          </div>
        </div>
      </div>

      <div className="bg-amber-50 px-5 py-4 space-y-4">
        <div>
          <p className="text-gray-800 text-sm leading-relaxed">{referral.reason}</p>
          {referral.timing && (
            <p className="text-amber-700 text-xs mt-1 font-medium">⏱ When: {referral.timing}</p>
          )}
        </div>

        {referral.discipline_explanation && (
          <div className="bg-white rounded-xl px-4 py-3 border border-amber-100">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Why this type of care?</p>
            <p className="text-gray-700 text-sm">{referral.discipline_explanation}</p>
          </div>
        )}

        {showProvidersAndCoverage && (
          <>
            {/* Providers */}
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Find a provider</p>
              {loadingProviders ? (
                <p className="text-gray-500 text-sm">Loading providers…</p>
              ) : providers.length === 0 ? (
                <p className="text-gray-500 text-sm">No providers listed yet. Check your local directory.</p>
              ) : (
                <ul className="space-y-2">
                  {providers.map((provider) => (
                    <li key={provider.id} className={`rounded-xl px-4 py-3 border text-sm ${provider.recommended ? 'border-orange-300 bg-orange-50' : 'border-gray-200 bg-white'}`}>
                      {provider.recommended && (
                        <span className="inline-block px-2 py-0.5 rounded-full bg-orange-500 text-white text-xs font-medium mr-2 mb-1">⭐ Recommended</span>
                      )}
                      <p className="font-semibold text-gray-800">{provider.name} — {provider.clinic}</p>
                      <p className="text-gray-500 text-xs">{provider.address}, {provider.postal_code}</p>
                      {provider.phone && <p className="text-gray-500 text-xs">📞 {provider.phone}</p>}
                      {provider.languages?.length > 0 && (
                        <p className="text-gray-400 text-xs">Languages: {provider.languages.join(', ')}</p>
                      )}
                      {provider.accepts_direct_bill && (
                        <p className="text-emerald-600 text-xs font-medium mt-0.5">✓ Accepts direct billing</p>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Coverage */}
            <div className="bg-white rounded-xl border border-amber-100 overflow-hidden">
              <div className="px-4 py-3 border-b border-amber-100">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Coverage</p>
                <p className="text-gray-400 text-xs mt-0.5">Final coverage is determined by your insurer.</p>
              </div>

              <div className="px-4 py-3 space-y-3">
                {loadingCoverage ? (
                  <p className="text-gray-500 text-sm">Loading…</p>
                ) : coverage ? (
                  <>
                    <p className="text-gray-700 text-sm">{coverage.copy}</p>
                    <ul className="space-y-1">
                      {coverage.checklist?.map((item, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                          <span className="text-indigo-500 mt-0.5">✓</span>{item}
                        </li>
                      ))}
                    </ul>
                  </>
                ) : null}

                {/* Insurer + Plan selectors */}
                <div className="pt-3 border-t border-gray-100">
                  <div className="flex flex-wrap gap-3 mb-3">
                    <div className="flex flex-col gap-1">
                      <label className="text-xs font-medium text-gray-500">Insurer</label>
                      <select
                        value={selectedInsurer}
                        onChange={(e) => setSelectedInsurer(e.target.value)}
                        className={inputCls}
                      >
                        <option value="">Select insurer</option>
                        {insurers.map((i) => (
                          <option key={i.slug} value={i.slug}>{i.name}</option>
                        ))}
                      </select>
                    </div>
                    <div className="flex flex-col gap-1">
                      <label className="text-xs font-medium text-gray-500">Plan</label>
                      <select
                        value={selectedPlan}
                        onChange={(e) => setSelectedPlan(e.target.value)}
                        disabled={!selectedInsurer || plans.length === 0}
                        className={`${inputCls} disabled:opacity-50`}
                      >
                        <option value="">Select plan</option>
                        {plans.map((p) => (
                          <option key={p.slug} value={p.slug}>{p.name}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {/* Cost estimate */}
                  {costEstimate && (
                    <div className="bg-indigo-50 rounded-xl px-4 py-3 mb-3 border border-indigo-100">
                      <p className="text-xs font-semibold text-indigo-600 uppercase tracking-wide mb-2">Estimated cost per visit</p>
                      <div className="grid grid-cols-3 gap-2 text-center">
                        <div>
                          <p className="text-lg font-bold text-gray-800">${costEstimate.cost_per_visit}</p>
                          <p className="text-xs text-gray-500">Session cost</p>
                        </div>
                        <div>
                          <p className="text-lg font-bold text-emerald-600">${costEstimate.covered_amount}</p>
                          <p className="text-xs text-gray-500">Covered</p>
                        </div>
                        <div>
                          <p className="text-lg font-bold text-orange-500">${costEstimate.you_pay}</p>
                          <p className="text-xs text-gray-500">You pay</p>
                        </div>
                      </div>
                      <p className="text-xs text-gray-400 mt-2 text-center">
                        {costEstimate.coverage_percent}% coverage · ${costEstimate.annual_limit_dollars} annual limit
                      </p>
                    </div>
                  )}

                  {/* Explain buttons */}
                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => handleExplain('why')}
                      disabled={!selectedPlan || explainLoading}
                      className="px-3 py-1.5 rounded-lg bg-emerald-600 text-white text-xs font-semibold hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                    >
                      Why this fits
                    </button>
                    <button
                      type="button"
                      onClick={() => handleExplain('why_not')}
                      disabled={!selectedPlan || explainLoading}
                      className="px-3 py-1.5 rounded-lg bg-amber-600 text-white text-xs font-semibold hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                    >
                      Why it might not
                    </button>
                  </div>

                  {(explainLoading || explainResult) && (
                    <div className="mt-3 p-3 rounded-xl bg-gray-50 border border-gray-200 text-sm text-gray-800">
                      {explainLoading ? (
                        <p className="text-gray-500">Loading explanation…</p>
                      ) : (
                        <>
                          <p className="font-semibold text-gray-700 mb-1 text-xs uppercase tracking-wide">
                            {explainQuestion === 'why' ? 'Why this fits your plan' : 'Why it might not fit'}
                          </p>
                          <p className="text-sm">{explainResult}</p>
                        </>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
