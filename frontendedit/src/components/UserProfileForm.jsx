import { useState, useEffect } from 'react'

export const FLEXCARE_SESSION_KEY = 'flexcare_session_id'

function getOrCreateSessionId() {
  try {
    let id = localStorage.getItem(FLEXCARE_SESSION_KEY)
    if (!id) {
      id = typeof crypto !== 'undefined' && crypto.randomUUID
        ? crypto.randomUUID()
        : `s${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
      localStorage.setItem(FLEXCARE_SESSION_KEY, id)
    }
    return id
  } catch {
    return `s${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
  }
}

const Field = ({ label, children }) => (
  <label className="block">
    <span className="text-xs font-medium text-gray-600 mb-1 block">{label}</span>
    {children}
  </label>
)

const inputCls = "w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-800 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent transition"

export default function UserProfileForm({ apiUrl, onClose }) {
  const [sessionId, setSessionId] = useState('')
  const [medicalHistory, setMedicalHistory] = useState('')
  const [previousSurgeries, setPreviousSurgeries] = useState('')
  const [priorInjuries, setPriorInjuries] = useState('')
  const [chronicConditions, setChronicConditions] = useState('')
  const [otherRelevant, setOtherRelevant] = useState('')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [loaded, setLoaded] = useState(false)

  const baseUrl = apiUrl || (import.meta.env.VITE_API_URL || 'http://localhost:8000')

  useEffect(() => {
    setSessionId(getOrCreateSessionId())
  }, [])

  useEffect(() => {
    if (!sessionId || !baseUrl) return
    fetch(`${baseUrl}/profile?session_id=${encodeURIComponent(sessionId)}`)
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then((data) => {
        if (data.profile) {
          setMedicalHistory(data.profile.medical_history || '')
          setPreviousSurgeries((data.profile.previous_surgeries || []).join(', '))
          setPriorInjuries((data.profile.prior_injuries || []).join(', '))
          setChronicConditions((data.profile.chronic_conditions || []).join(', '))
          setOtherRelevant(data.profile.other_relevant || '')
        }
      })
      .catch(() => {})
      .finally(() => setLoaded(true))
  }, [sessionId, baseUrl])

  const handleSubmit = (e) => {
    e.preventDefault()
    setSaving(true)
    setSaved(false)
    const payload = {
      session_id: sessionId,
      medical_history: medicalHistory.trim() || null,
      previous_surgeries: previousSurgeries.split(',').map((s) => s.trim()).filter(Boolean),
      prior_injuries: priorInjuries.split(',').map((s) => s.trim()).filter(Boolean),
      chronic_conditions: chronicConditions.split(',').map((s) => s.trim()).filter(Boolean),
      other_relevant: otherRelevant.trim() || null,
    }
    fetch(`${baseUrl}/profile`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
      .then((res) => {
        if (!res.ok) throw new Error('Failed to save')
        setSaved(true)
      })
      .catch(() => setSaved(false))
      .finally(() => setSaving(false))
  }

  return (
    <div className="bg-white rounded-2xl border border-indigo-100 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-violet-600 px-5 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"/>
            </svg>
          </div>
          <div>
            <h3 className="text-white font-semibold text-sm">Health Profile</h3>
            <p className="text-indigo-200 text-xs">Personalises your AI recommendations</p>
          </div>
        </div>
        {onClose && (
          <button onClick={onClose} className="text-white/70 hover:text-white transition p-1 rounded-lg hover:bg-white/10">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        )}
      </div>

      <div className="px-5 py-4">
        {!loaded && sessionId ? (
          <div className="flex items-center gap-2 text-indigo-500 text-sm py-4">
            <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
            </svg>
            Loading profile…
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-3">
            <Field label="Relevant medical history">
              <textarea
                value={medicalHistory}
                onChange={(e) => setMedicalHistory(e.target.value)}
                placeholder="e.g. Previous knee surgery (ACL repair, 2022)"
                rows={2}
                className={inputCls}
              />
            </Field>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <Field label="Previous surgeries (comma-separated)">
                <input
                  type="text"
                  value={previousSurgeries}
                  onChange={(e) => setPreviousSurgeries(e.target.value)}
                  placeholder="e.g. Knee (ACL, 2022)"
                  className={inputCls}
                />
              </Field>
              <Field label="Prior injuries (comma-separated)">
                <input
                  type="text"
                  value={priorInjuries}
                  onChange={(e) => setPriorInjuries(e.target.value)}
                  placeholder="e.g. Lower back strain 2020"
                  className={inputCls}
                />
              </Field>
              <Field label="Chronic conditions (comma-separated)">
                <input
                  type="text"
                  value={chronicConditions}
                  onChange={(e) => setChronicConditions(e.target.value)}
                  placeholder="e.g. Asthma, Diabetes"
                  className={inputCls}
                />
              </Field>
              <Field label="Other (medications, lifestyle)">
                <input
                  type="text"
                  value={otherRelevant}
                  onChange={(e) => setOtherRelevant(e.target.value)}
                  placeholder="Optional"
                  className={inputCls}
                />
              </Field>
            </div>

            <div className="flex items-center gap-3 pt-1">
              <button
                type="submit"
                disabled={saving}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold transition disabled:opacity-50 shadow-sm"
              >
                {saving ? (
                  <>
                    <svg className="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
                    </svg>
                    Saving…
                  </>
                ) : (
                  <>
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5"/>
                    </svg>
                    Save profile
                  </>
                )}
              </button>
              {saved && (
                <span className="flex items-center gap-1 text-emerald-600 text-sm font-medium">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  Profile saved
                </span>
              )}
            </div>
          </form>
        )}

        <p className="text-gray-400 text-xs mt-3 border-t border-gray-100 pt-3">
          Stored locally in this browser. Session: <code className="bg-gray-100 px-1 rounded text-gray-500">{sessionId.slice(0, 12)}…</code>
        </p>
      </div>
    </div>
  )
}
