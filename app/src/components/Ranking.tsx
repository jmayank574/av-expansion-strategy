import type { Meta, Weights } from '../types'
import { PILLARS } from '../types'
import type { Row } from '../scoring'
import { setWeight } from '../scoring'

const SCEN: [string, string][] = [['balanced', 'Balanced'], ['fast_growth', 'Fast growth'], ['low_risk', 'Low risk'], ['capital_light', 'Capital light']]

function Bar({ v, label }: { v: number; label: string }) {
  return (
    <div className="h-2 w-14 rounded-sm bg-line" title={`${label}: ${v.toFixed(0)}`}>
      <div className="h-2 rounded-sm bg-accent" style={{ width: `${Math.max(2, v)}%` }} />
    </div>
  )
}

interface Props {
  rows: Row[]; meta: Meta; weights: Weights; scenario: string
  onScenario: (s: string) => void; onWeights: (w: Weights) => void; onOpen: (m: string) => void
}

export default function Ranking({ rows, meta, weights, scenario, onScenario, onWeights, onOpen }: Props) {
  const cand = rows.filter(r => !r.m.benchmark).sort((a, b) => (a.rank! - b.rank!) || a.m.metro.localeCompare(b.m.metro))
  const sum = PILLARS.reduce((a, k) => a + weights[k], 0)
  const vegas = rows.find(r => r.m.benchmark)
  const confCol = cand.some(r => r.m.confidence != null)
  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_260px]">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-line text-left text-xs uppercase tracking-wide text-muted">
              <th className="py-2 pr-2">#</th>
              <th className="pr-3">Metro</th>
              <th className="pr-3 text-right">Total</th>
              {PILLARS.map(p => <th key={p} className="pr-2" title={meta.weights.pillars[p].label}>{meta.weights.pillars[p].label.split(' ')[0]}</th>)}
              <th className="pr-2 text-center">Reg. tier</th>
              <th className="pr-2 text-center">Competitors</th>
              {confCol && <th className="text-right" title="Share of Monte Carlo weight draws in which the metro lands in the top 5">Confidence</th>}
            </tr>
          </thead>
          <tbody>
            {cand.map(r => (
              <tr key={r.m.metro} onClick={() => onOpen(r.m.metro)} className={`cursor-pointer border-b border-line hover:bg-panel ${r.rank! <= 5 ? 'font-medium' : ''}`}>
                <td className="py-1.5 pr-2 text-muted">{r.rank}</td>
                <td className="pr-3">{r.m.metro}</td>
                <td className="pr-3 text-right tabular-nums">{r.total.toFixed(1)}</td>
                {PILLARS.map(p => <td key={p} className="pr-2"><Bar v={r.pillars[p]} label={meta.weights.pillars[p].label} /></td>)}
                <td className="pr-2 text-center">{r.m.regulation.tier}</td>
                <td className="pr-2 text-center">{r.m.raw.n_competitors}</td>
                {confCol && <td className="text-right tabular-nums">{r.m.confidence != null ? `${(r.m.confidence * 100).toFixed(0)}%` : '–'}</td>}
              </tr>
            ))}
            {vegas && (
              <tr className="border-t-2 border-line italic text-muted">
                <td className="py-1.5 pr-2">ref</td>
                <td className="pr-3">Las Vegas (benchmark)</td>
                <td className="pr-3 text-right tabular-nums">{vegas.total.toFixed(1)}</td>
                {PILLARS.map(p => <td key={p} className="pr-2"><Bar v={vegas.pillars[p]} label={meta.weights.pillars[p].label} /></td>)}
                <td className="pr-2 text-center">{vegas.m.regulation.tier}</td>
                <td className="pr-2 text-center">{vegas.m.raw.n_competitors}</td>
                {confCol && <td />}
              </tr>
            )}
          </tbody>
        </table>
        <p className="mt-2 text-xs text-muted">
          Click a row for the drill-down. Bars are 0–100 percentile scores within the 25 candidates. Las Vegas is scored on the same scale but not ranked.
        </p>
      </div>

      <aside className="h-fit rounded-lg border border-line bg-panel p-4 text-sm">
        <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">Scenario</div>
        <div className="mb-4 flex flex-wrap gap-2">
          {SCEN.map(([id, label]) => (
            <button
              key={id}
              onClick={() => onScenario(id)}
              className={`rounded-md border px-2.5 py-1 text-xs font-medium ${scenario === id ? 'border-accent bg-accent text-white' : 'border-line bg-white hover:border-accent'}`}
            >
              {label}
            </button>
          ))}
        </div>
        <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">Pillar weights</div>
        {PILLARS.map(p => (
          <label key={p} className="mb-3 block">
            <div className="flex justify-between">
              <span>{meta.weights.pillars[p].label}</span>
              <span className="font-medium tabular-nums">{weights[p]}</span>
            </div>
            <input type="range" min={0} max={100} value={weights[p]} onChange={e => onWeights(setWeight(weights, p, Number(e.target.value)))} className="w-full" />
          </label>
        ))}
        <div className="flex justify-between border-t border-line pt-2 text-xs">
          <span className="text-muted">Total (always 100)</span>
          <span className="font-semibold tabular-nums">{sum}</span>
        </div>
      </aside>
    </div>
  )
}
