import { useState } from 'react'
import type { Meta, Metro } from '../types'
import { economics } from '../scoring'

const SLIDERS: { key: string; label: string; min: number; max: number; step: number; fmt: (v: number) => string }[] = [
  { key: 'avg_fare_usd', label: 'Average fare', min: 10, max: 40, step: 0.5, fmt: v => `$${v.toFixed(2)}` },
  { key: 'capture_share', label: 'Robotaxi capture share of ride-hail trips', min: 0.005, max: 0.15, step: 0.005, fmt: v => `${(v * 100).toFixed(1)}%` },
  { key: 'trips_per_vehicle_per_day', label: 'Paid trips per vehicle per day', min: 8, max: 35, step: 1, fmt: v => v.toFixed(0) },
]
const usd = (v: number) => `$${Math.round(v).toLocaleString('en-US')}`

export default function UnitEconomics({ m, meta }: { m: Metro; meta: Meta }) {
  const A = meta.assumptions
  const base = A ? Object.fromEntries(Object.entries(A).map(([k, v]) => [k, v.value])) : null
  const [over, setOver] = useState<Record<string, number>>({})
  if (!A || !base || !m.demand_estimate || !m.unit_economics) return null
  const a = { ...base, ...over }
  const e = economics(m.demand_estimate.trips_base, m.raw.elec_cents_kwh, a)
  const py = m.unit_economics
  const changed = Object.keys(over).length > 0
  return (
    <section className="mt-6 rounded-lg border border-line bg-panel p-4">
      <div className="mb-1 flex items-baseline justify-between">
        <h3 className="text-sm font-semibold">Unit economics (estimate, not a forecast)</h3>
        {changed && <button onClick={() => setOver({})} className="text-xs text-accent underline">reset to base assumptions</button>}
      </div>
      <p className="mb-3 text-xs text-muted">
        City ride-hail demand is estimated from two anchors (Chicago and NYC, {meta.demand_method?.anchor_year}): about {(m.demand_estimate.trips_base / 1e6).toFixed(1)}M trips a year
        ({(m.demand_estimate.trips_low / 1e6).toFixed(1)}M to {(m.demand_estimate.trips_high / 1e6).toFixed(1)}M). All other inputs are labeled analyst assumptions in config/assumptions.yaml.
      </p>
      <div className="grid gap-6 md:grid-cols-2">
        <div>
          {SLIDERS.map(s => (
            <label key={s.key} className="mb-3 block text-sm">
              <div className="flex justify-between"><span>{s.label}</span><span className="font-medium tabular-nums">{s.fmt(a[s.key])}</span></div>
              <input type="range" min={s.min} max={s.max} step={s.step} value={a[s.key]} onChange={ev => setOver({ ...over, [s.key]: Number(ev.target.value) })} className="w-full" />
            </label>
          ))}
        </div>
        <table className="w-full self-start text-sm">
          <tbody>
            {[
              ['Addressable robotaxi trips per day', Math.round(e.addressable_trips_per_day).toLocaleString('en-US'), Math.round(py.low.addressable_trips_per_day).toLocaleString('en-US') + ' – ' + Math.round(py.high.addressable_trips_per_day).toLocaleString('en-US')],
              ['Fleet needed (vehicles)', Math.round(e.fleet_vehicles).toLocaleString('en-US'), Math.round(py.low.fleet_vehicles).toLocaleString('en-US') + ' – ' + Math.round(py.high.fleet_vehicles).toLocaleString('en-US')],
              ['Revenue per vehicle per year', usd(e.revenue_per_vehicle), usd(py.low.revenue_per_vehicle) + ' – ' + usd(py.high.revenue_per_vehicle)],
              ['Operating cost per vehicle per year', usd(e.opex_per_vehicle), usd(py.high.opex_per_vehicle) + ' – ' + usd(py.low.opex_per_vehicle)],
              ['  of which charging', usd(e.charging_cost_per_vehicle), `${m.raw.elec_cents_kwh.toFixed(1)} cents/kWh in ${m.state}`],
              ['Contribution per vehicle per year', usd(e.contribution_per_vehicle), usd(py.low.contribution_per_vehicle) + ' – ' + usd(py.high.contribution_per_vehicle)],
              ['Payback on vehicle cost', e.payback_years == null ? 'never' : `${e.payback_years.toFixed(1)} years`,
                (py.high.payback_years?.toFixed(1) ?? 'n/a') + ' – ' + (py.low.payback_years?.toFixed(1) ?? 'never') + ' years'],
            ].map(([label, val, range]) => (
              <tr key={label} className="border-b border-line">
                <td className="py-1 pr-2">{label}</td>
                <td className="text-right font-medium tabular-nums">{val}</td>
                <td className="pl-3 text-right text-xs text-muted">{range}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-2 text-xs text-muted">Left column of numbers follows the sliders; the grey range is the Python low to high case (pessimistic to optimistic on every input at once, with the low to high demand estimate).</p>
    </section>
  )
}
