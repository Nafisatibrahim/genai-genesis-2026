import { useState } from 'react'
import BodyMap from './components/BodyMap'
import { REGION_LABELS } from './constants/regions'

export default function App() {
  const [selectedRegionId, setSelectedRegionId] = useState(null)
  const [view, setView] = useState('back')
  const [gender, setGender] = useState('male')

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <header className="text-center mb-4">
        <h1 className="text-2xl font-semibold text-slate-800">FlexCare</h1>
        <p className="text-slate-600 text-sm mt-1">Tap where it hurts</p>
      </header>

      <div className="flex flex-wrap justify-center gap-4 mb-4">
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-600">View:</span>
          <button
            type="button"
            onClick={() => setView('front')}
            className={`px-3 py-1.5 rounded text-sm font-medium ${
              view === 'front'
                ? 'bg-blue-600 text-white'
                : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
            }`}
          >
            Front
          </button>
          <button
            type="button"
            onClick={() => setView('back')}
            className={`px-3 py-1.5 rounded text-sm font-medium ${
              view === 'back'
                ? 'bg-blue-600 text-white'
                : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
            }`}
          >
            Back
          </button>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-600">Body:</span>
          <button
            type="button"
            onClick={() => setGender('male')}
            className={`px-3 py-1.5 rounded text-sm font-medium ${
              gender === 'male'
                ? 'bg-blue-600 text-white'
                : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
            }`}
          >
            Male
          </button>
          <button
            type="button"
            onClick={() => setGender('female')}
            className={`px-3 py-1.5 rounded text-sm font-medium ${
              gender === 'female'
                ? 'bg-blue-600 text-white'
                : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
            }`}
          >
            Female
          </button>
        </div>
      </div>

      <BodyMap
        onRegionClick={setSelectedRegionId}
        selectedRegionId={selectedRegionId}
        side={view}
        gender={gender}
      />
      {selectedRegionId && (
        <p className="text-center mt-4 text-slate-600">
          Selected: <strong>{REGION_LABELS[selectedRegionId]}</strong>
        </p>
      )}
    </div>
  )
}
