import type { Dispatch, SetStateAction } from 'react'

const regions = ['ap-southeast-1']

interface RegionSelectorProps {
  region: string
  onChange: Dispatch<SetStateAction<string>>
}

export default function RegionSelector({ region, onChange }: RegionSelectorProps) {
  return (
    <label className="region-selector">
      AWS region
      <select value={region} onChange={e => onChange(e.target.value)}>
        {regions.map(r => (
          <option key={r} value={r}>
            {r}
          </option>
        ))}
      </select>
    </label>
  )
}
