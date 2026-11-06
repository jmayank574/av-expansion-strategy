import { useEffect, useMemo, useState } from 'react'
import type { Scored, Weights } from './types'
import { scoreAll } from './scoring'
import Ranking from './components/Ranking'
import Quadrant from './components/Quadrant'
import Drilldown from './components/Drilldown'

type View = 'ranking' | 'quadrant' | 'drill'
const TABS: { id: View; label: string }[] = [
  { id: 'ranking', label: 'Ranking' },
  { id: 'quadrant', label: 'Opportunity vs. Ease of Entry' },
  { id: 'drill', label: 'Metro drill-down' },
]
const SCENARIO_LABEL: Record<string, string> = { balanced: 'Balanced', fast_growth: 'Fast growth', low_risk: 'Low risk', capital_light: 'Capital light' }

export default function App() {
  const [data, setData] = useState<Scored | null>(null)
  const [err, setErr] = useState<string | null>(null)
  const q = new URLSearchParams(window.location.search)
  const [view, setView] = useState<View>((['ranking', 'quadrant', 'drill'].includes(q.get('view') ?? '') ? q.get('view') : 'ranking') as View)
  const [scenario, setScenario] = useState<string>('balanced')
  const [weights, setWeights] = useState<Weights | null>(null)
  const [selected, setSelected] = useState<string>(q.get('metro') ?? '')

  useEffect(() => {
    fetch('metros_scored.json')
      .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json() })
      .then((d: Scored) => {
        setData(d)
        setWeights(d.meta.weights.scenarios[d.meta.weights.default_scenario])
        setScenario(d.meta.weights.default_scenario)
      })
      .catch(e => setErr(String(e)))
  }, [])

  const rows = useMemo(() => (data && weights ? scoreAll(data.metros, data.meta, weights) : []), [data, weights])
  const top5 = useMemo(
    () => rows.filter(r => !r.m.benchmark).sort((a, b) => (a.rank! - b.rank!) || a.m.metro.localeCompare(b.m.metro)).slice(0, 5),
    [rows],
  )

  if (err) return <div className="p-8 text-red-700">Could not load metros_scored.json: {err}</div>
  if (!data || !weights) return <div className="p-8 text-muted">Loading…</div>

  const sel = selected || top5[0]?.m.metro || data.metros[0].metro
  const apply = (name: string) => { setScenario(name); setWeights(data.meta.weights.scenarios[name]) }
  const setCustom = (w: Weights) => { setScenario('custom'); setWeights(w) }
  const open = (metro: string) => { setSelected(metro); setView('drill') }
  const v = data.meta.vintages

  return (
    <div className="mx-auto max-w-6xl px-6 py-6">
      <header className="mb-5">
        <div className="text-xs font-medium uppercase tracking-wide text-accent">AV market expansion · beachhead: Las Vegas</div>
        <h1 className="mt-1 text-2xl font-semibold">{data.meta.question}</h1>
        <p className="mt-2 text-base">
          <span className="text-muted">Current top 5 ({scenario === 'custom' ? 'custom weights' : SCENARIO_LABEL[scenario]}): </span>
          <strong>{top5.map(r => r.m.metro).join(', ')}</strong>.
        </p>
        <p className="mt-1 text-xs text-muted">Data as of {data.meta.data_as_of} · scores recompute live in your browser from the normalized sub-scores.</p>
      </header>

      <nav className="mb-5 flex gap-1 border-b border-line">
        {TABS.map(t => (
          <button
            key={t.id}
            onClick={() => setView(t.id)}
            className={`-mb-px border-b-2 px-4 py-2 text-sm font-medium ${view === t.id ? 'border-accent text-accent' : 'border-transparent text-muted hover:text-ink'}`}
          >
            {t.label}
          </button>
        ))}
      </nav>

      {view === 'ranking' && <Ranking rows={rows} meta={data.meta} weights={weights} scenario={scenario} onScenario={apply} onWeights={setCustom} onOpen={open} />}
      {view === 'quadrant' && <Quadrant rows={rows} onOpen={open} />}
      {view === 'drill' && <Drilldown rows={rows} meta={data.meta} selected={sel} onSelect={setSelected} />}

      <footer className="mt-10 border-t border-line pt-4 text-xs text-muted">
        <div>
          Data vintages: ACS {v.acs} · FAA {v.faa} · Weather {v.weather} · {v.nhtsa} · EIA {v.eia} · {v.regulation_and_competitors}.
        </div>
        <div className="mt-1">
          Public data only. NHTSA reports have no mileage, so they show where operators are active, not crash rates.{' '}
          <a className="text-accent underline" href="methodology.md" target="_blank" rel="noreferrer">Methodology</a>
        </div>
      </footer>
    </div>
  )
}
