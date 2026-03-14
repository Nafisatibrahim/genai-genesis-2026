import Body from 'react-muscle-highlighter'
import {
  REGION_TO_LIBRARY_BACK,
  REGION_TO_LIBRARY_FRONT,
  libraryPressToRegionId,
} from '../constants/regions'

/**
 * Body map using react-muscle-highlighter (anatomically styled).
 * Supports male/female and front/back view. Maps library slugs to backend region IDs.
 */
export default function BodyMap({
  onRegionClick,
  selectedRegionId,
  side = 'back',
  gender = 'male',
}) {
  const map = side === 'back' ? REGION_TO_LIBRARY_BACK : REGION_TO_LIBRARY_FRONT
  const mapping = selectedRegionId ? map[selectedRegionId] : null
  const data =
    mapping &&
    [{
      ...mapping,
      color: '#3b82f6',
      intensity: 1,
    }]

  const handleBodyPartPress = (part, pressSide) => {
    const regionId = libraryPressToRegionId(part?.slug, pressSide)
    if (regionId) onRegionClick?.(regionId)
  }

  return (
    <div
      className="w-full max-w-sm mx-auto select-none"
      role="img"
      aria-label={`Body map ${side} view - tap a region`}
    >
      <Body
        data={data || []}
        side={side}
        gender={gender}
        scale={1.4}
        colors={['#3b82f6']}
        onBodyPartPress={handleBodyPartPress}
        defaultFill="#94a3b8"
        defaultStroke="#64748b"
        defaultStrokeWidth={0.5}
        border="#cbd5e1"
      />
    </div>
  )
}
