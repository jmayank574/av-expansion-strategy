import { CartesianGrid, Cell, LabelList, ReferenceLine, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis, ZAxis } from 'recharts'
import type { Row } from '../scoring'
import { median } from '../scoring'

interface Pt { name: string; x: number; y: number; z: number; q: string }

export default function Quadrant({ rows, onOpen }: { rows: Row[]; onOpen: (m: string) => void }) {
  const cand = rows.filter(r => !r.m.benchmark)
  const mx = median(cand.map(r => r.ease))
  const my = median(cand.map(r => r.opportunity))
  const quad = (x: number, y: number) => (y >= my ? (x >= mx ? 'Launch next' : 'Build case') : (x >= mx ? 'Opportunistic' : 'Deprioritize'))
  const pts: Pt[] = cand.map(r => ({ name: r.m.metro, x: r.ease, y: r.opportunity, z: 0.5 + r.m.raw.crowding, q: quad(r.ease, r.opportunity) }))
  const v = rows.find(r => r.m.benchmark)
  const vegas: Pt[] = v ? [{ name: 'Las Vegas (benchmark)', x: v.ease, y: v.opportunity, z: 0.5 + v.m.raw.crowding, q: quad(v.ease, v.opportunity) }] : []
  const launch = pts.filter(p => p.q === 'Launch next').sort((a, b) => b.x + b.y - a.x - a.y)
  const dom = (k: 'x' | 'y'): [number, number] => {
    const all = [...pts, ...vegas].map(p => p[k])
    return [Math.floor(Math.min(...all) / 10) * 10, Math.ceil(Math.max(...all) / 10) * 10]
  }
  const ticks = (d: [number, number]) => { const t: number[] = []; for (let v = d[0]; v <= d[1]; v += 10) t.push(v); return t }
  const qLabel = 'pointer-events-none absolute text-xs font-semibold uppercase tracking-wide'
  return (
    <div>
      <p className="mb-3 text-sm text-muted">
        <strong className="text-ink">Opportunity</strong> = demand pillar. <strong className="text-ink">Ease of entry</strong> = the other four pillars, re-weighted.
        Dashed lines are the medians of the 25 candidates. Bubble size = competitor crowding; the black diamond is the Las Vegas benchmark.
      </p>
      <div className="relative h-[560px] rounded-lg border border-line p-2">
        <div className={`${qLabel} left-20 top-3 text-muted`}>Build case</div>
        <div className={`${qLabel} right-6 top-3 text-accent`}>Launch next</div>
        <div className={`${qLabel} bottom-16 left-20 text-muted`}>Deprioritize</div>
        <div className={`${qLabel} bottom-16 right-6 text-muted`}>Opportunistic</div>
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 28, right: 90, bottom: 28, left: 8 }}>
            <CartesianGrid stroke="#eef0f3" />
            <XAxis type="number" dataKey="x" domain={dom('x')} ticks={ticks(dom('x'))} name="Ease of entry" tick={{ fontSize: 11, fill: '#6b7280' }}
              label={{ value: 'Ease of entry →', position: 'bottom', offset: 6, fill: '#6b7280', fontSize: 12 }} />
            <YAxis type="number" dataKey="y" domain={dom('y')} ticks={ticks(dom('y'))} name="Opportunity" tick={{ fontSize: 11, fill: '#6b7280' }}
              label={{ value: 'Opportunity (demand) →', angle: -90, position: 'insideLeft', fill: '#6b7280', fontSize: 12 }} />
            <ZAxis type="number" dataKey="z" range={[60, 600]} name="Crowding" />
            <ReferenceLine x={mx} stroke="#9ca3af" strokeDasharray="5 4" />
            <ReferenceLine y={my} stroke="#9ca3af" strokeDasharray="5 4" />
            <Tooltip
              cursor={{ strokeDasharray: '3 3' }}
              content={({ payload }) => {
                const p = payload?.[0]?.payload as Pt | undefined
                if (!p) return null
                return (
                  <div className="rounded border border-line bg-white p-2 text-xs shadow">
                    <div className="font-semibold">{p.name}</div>
                    <div>{p.q}</div>
                    <div>Opportunity {p.y.toFixed(0)} · Ease {p.x.toFixed(0)}</div>
                    <div>Crowding {(p.z - 0.5).toFixed(1)}</div>
                  </div>
                )
              }}
            />
            <Scatter data={pts} isAnimationActive={false} onClick={(d: unknown) => onOpen((d as Pt).name)} cursor="pointer">
              {pts.map(p => <Cell key={p.name} fill="#1d4ed8" fillOpacity={p.q === 'Launch next' ? 0.85 : 0.35} stroke="#ffffff" strokeWidth={1.5} />)}
              <LabelList dataKey="name" position="right" fontSize={11} fill="#111827" formatter={(n: unknown) => (launch.some(l => l.name === n) || pts.some(p => p.name === n && p.y >= 70) ? String(n) : '')} />
            </Scatter>
            <Scatter data={vegas} isAnimationActive={false} shape="diamond" fill="#111827">
              <LabelList dataKey="name" position="right" fontSize={11} fill="#111827" />
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>
      <p className="mt-3 text-sm">
        <span className="font-semibold">Launch-next quadrant: </span>{launch.map(p => p.name).join(', ') || 'none'}.
        <span className="text-muted"> The chart labels this quadrant plus the highest-demand metros; hover any bubble for details, click to open it.</span>
      </p>
    </div>
  )
}
