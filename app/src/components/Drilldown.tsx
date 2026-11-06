import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { Meta } from '../types'
import { PILLARS } from '../types'
import type { Row } from '../scoring'

const STATUS: Record<string, string> = {
  operating_public: 'Operating (public)', operating_limited: 'Operating (limited)', testing: 'Testing', announced: 'Announced',
}
const TIER: Record<number, string> = {
  3: 'Tier 3: driverless commercial service allowed and operating', 2: 'Tier 2: driverless allowed with a permit or filing process',
  1: 'Tier 1: testing only; driverless commercial service unclear or restricted', 0: 'Tier 0: restrictive or no legal pathway',
}

function fmt(v: number, unit: string): string {
  if (unit.startsWith('share')) return `${(v * 100).toFixed(1)}%`
  if (unit === 'people' || unit === 'people / sq mi') return Math.round(v).toLocaleString('en-US')
  if (unit === 'per resident') return v.toFixed(2)
  if (unit === 'tier') return String(v)
  return v.toFixed(1)
}

export default function Drilldown({ rows, meta, selected, onSelect }: { rows: Row[]; meta: Meta; selected: string; onSelect: (m: string) => void }) {
  const row = rows.find(r => r.m.metro === selected) ?? rows[0]
  const m = row.m
  const chart = PILLARS.map(p => ({ pillar: meta.weights.pillars[p].label, score: row.pillars[p] }))
  const names = rows.map(r => r.m.metro).sort()
  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <select value={selected} onChange={e => onSelect(e.target.value)} className="rounded-md border border-line bg-white px-3 py-1.5 text-sm">
          {names.map(n => <option key={n}>{n}</option>)}
        </select>
        <div className="text-sm text-muted">
          {m.benchmark ? 'Benchmark (not ranked)' : `Rank ${row.rank} of 25`} · Total {row.total.toFixed(1)} · Opportunity {row.opportunity.toFixed(0)} · Ease of entry {row.ease.toFixed(0)}
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <section>
          <h3 className="mb-1 text-sm font-semibold">Pillar breakdown (0–100)</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chart} layout="vertical" margin={{ left: 20, right: 24 }}>
                <CartesianGrid stroke="#eef0f3" horizontal={false} />
                <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11, fill: '#6b7280' }} />
                <YAxis type="category" dataKey="pillar" width={140} tick={{ fontSize: 12, fill: '#111827' }} />
                <Tooltip formatter={(v) => (typeof v === 'number' ? v.toFixed(1) : String(v))} />
                <Bar dataKey="score" isAnimationActive={false} radius={[0, 4, 4, 0]} barSize={14}>
                  {chart.map(c => <Cell key={c.pillar} fill="#1d4ed8" />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <h3 className="mb-1 mt-4 text-sm font-semibold">Why</h3>
          <ul className="list-disc space-y-1 pl-5 text-sm">
            {m.why.map((w, i) => <li key={i} className={i === 2 ? 'text-ink' : ''}>{i === 2 && <span className="font-semibold">Biggest risk: </span>}{w}</li>)}
          </ul>

          <h3 className="mb-1 mt-4 text-sm font-semibold">Similarity to the Las Vegas beachhead</h3>
          <div className="flex items-center gap-3 text-sm">
            <div className="h-2 w-40 rounded-sm bg-line"><div className="h-2 rounded-sm bg-accent" style={{ width: `${m.benchmark ? 100 : m.vegas_similarity}%` }} /></div>
            <span className="tabular-nums">{m.benchmark ? 100 : m.vegas_similarity.toFixed(0)} / 100</span>
          </div>
          <p className="mt-1 text-xs text-muted">Distance on rain, snow, heat days, density and enplanements per resident. Context only; not part of the total.</p>
        </section>

        <section>
          <h3 className="mb-1 text-sm font-semibold">Raw metrics</h3>
          <table className="w-full text-sm">
            <tbody>
              {PILLARS.flatMap(p => Object.entries(meta.weights.pillars[p].submetrics).map(([k, s]) => {
                const key = k === 'log_metro_pop' ? 'metro_pop' : k === 'city_density' ? 'city_density' : k
                return (
                  <tr key={k} className="border-b border-line">
                    <td className="py-1 pr-2">{k === 'log_metro_pop' ? 'Metro population' : s.label}</td>
                    <td className="text-right tabular-nums">{fmt(m.raw[key], k === 'log_metro_pop' ? 'people' : s.unit)}</td>
                    <td className="pl-2 text-xs text-muted">{k === 'log_metro_pop' ? 'people' : s.unit}</td>
                    <td className="pl-3 text-right text-xs tabular-nums text-muted" title="Percentile score (0–100, direction-adjusted)">{m.sub_scores[k].toFixed(0)}</td>
                  </tr>
                )
              })) }
            </tbody>
          </table>
          <p className="mt-1 text-xs text-muted">Right-hand column: the 0–100 percentile sub-score used in the ranking.</p>

          <h3 className="mb-1 mt-4 text-sm font-semibold">Competitors</h3>
          {m.competitors.length === 0 ? <p className="text-sm text-muted">None found in the seed file.</p> : (
            <ul className="space-y-1 text-sm">
              {m.competitors.map(c => (
                <li key={c.competitor}>
                  <span className="font-medium">{c.competitor}</span> · {STATUS[c.status] ?? c.status}
                  {c.platform_partner && <span className="text-muted"> · via {c.platform_partner}</span>}
                  <a className="ml-2 text-xs text-accent underline" href={c.source_url} target="_blank" rel="noreferrer">source</a>
                  <span className="ml-1 text-xs text-muted">({c.confidence})</span>
                </li>
              ))}
            </ul>
          )}
          {m.nhtsa_incidents.length > 0 && (
            <p className="mt-1 text-xs text-muted">NHTSA ADS incident reports, 24 months (activity, not a rate): {m.nhtsa_incidents.map(n => `${n.operating_entity} ${n.ads_incidents}`).join(', ')}.</p>
          )}

          <h3 className="mb-1 mt-4 text-sm font-semibold">Regulation ({m.state})</h3>
          <p className="text-sm font-medium">{TIER[m.regulation.tier]}</p>
          <p className="mt-1 text-sm">{m.regulation.notes}</p>
          <p className="mt-1 text-xs text-muted">
            {m.regulation.key_law_or_rule} · Permit body: {m.regulation.permit_body || 'n/a'} ·{' '}
            <a className="text-accent underline" href={m.regulation.source_url} target="_blank" rel="noreferrer">{m.regulation.source_title}</a>{' '}
            · as of {m.regulation.as_of_date} · confidence {m.regulation.confidence}
          </p>
        </section>
      </div>
    </div>
  )
}
