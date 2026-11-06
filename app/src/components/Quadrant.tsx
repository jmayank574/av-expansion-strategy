import { useEffect, useRef, useState } from 'react'
import { CartesianGrid, Cell, LabelList, ReferenceLine, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis, ZAxis } from 'recharts'
import type { Row } from '../scoring'
import { median } from '../scoring'

interface Pt { name: string; x: number; y: number; z: number; q: string }
interface Place { dx: number; dy: number; anchor: 'start' | 'end' | 'middle' }

const CHAR_W = 6.1, LABEL_H = 13

/** Greedy label placement in approximate pixel space: try right, left, above, below (then diagonals) and keep the first spot that
 *  overlaps no bubble and no earlier label. Earlier names in `order` get first choice. */
function placeLabels(pts: Pt[], order: string[], plotW: number, plotH: number, dx: [number, number], dy: [number, number]): Record<string, Place> {
  const px = (p: Pt) => ((p.x - dx[0]) / (dx[1] - dx[0])) * plotW
  const py = (p: Pt) => plotH - ((p.y - dy[0]) / (dy[1] - dy[0])) * plotH
  const zs = pts.map(p => p.z), zmin = Math.min(...zs), zmax = Math.max(...zs)
  const radius = (p: Pt) => Math.sqrt((60 + ((p.z - zmin) / (zmax - zmin || 1)) * 540) / Math.PI)
  type Box = [number, number, number, number]                         // x0, y0, x1, y1
  const hit = (a: Box, b: Box) => a[0] < b[2] && a[2] > b[0] && a[1] < b[3] && a[3] > b[1]
  const bubbles: Box[] = pts.map(p => [px(p) - radius(p), py(p) - radius(p), px(p) + radius(p), py(p) + radius(p)])
  const placed: Box[] = []
  const out: Record<string, Place> = {}
  for (const name of order) {
    const p = pts.find(q => q.name === name)
    if (!p) continue
    const w = name.length * CHAR_W, r = radius(p), cx = px(p), cy = py(p)
    const cands: { pl: Place; box: Box }[] = [
      { pl: { dx: r + 4, dy: 4, anchor: 'start' }, box: [cx + r + 4, cy - LABEL_H / 2, cx + r + 4 + w, cy + LABEL_H / 2] },
      { pl: { dx: -r - 4, dy: 4, anchor: 'end' }, box: [cx - r - 4 - w, cy - LABEL_H / 2, cx - r - 4, cy + LABEL_H / 2] },
      { pl: { dx: 0, dy: -r - 5, anchor: 'middle' }, box: [cx - w / 2, cy - r - 5 - LABEL_H, cx + w / 2, cy - r - 5] },
      { pl: { dx: 0, dy: r + 14, anchor: 'middle' }, box: [cx - w / 2, cy + r + 2, cx + w / 2, cy + r + 2 + LABEL_H] },
      { pl: { dx: r + 2, dy: -r - 2, anchor: 'start' }, box: [cx + r + 2, cy - r - 2 - LABEL_H, cx + r + 2 + w, cy - r - 2] },
      { pl: { dx: r + 2, dy: r + 12, anchor: 'start' }, box: [cx + r + 2, cy + r, cx + r + 2 + w, cy + r + LABEL_H] },
      { pl: { dx: -r - 2, dy: -r - 2, anchor: 'end' }, box: [cx - r - 2 - w, cy - r - 2 - LABEL_H, cx - r - 2, cy - r - 2] },
      { pl: { dx: -r - 2, dy: r + 12, anchor: 'end' }, box: [cx - r - 2 - w, cy + r, cx - r - 2, cy + r + LABEL_H] },
    ]
    const inside = (b: Box) => b[0] >= -60 && b[2] <= plotW + 80 && b[1] >= 0 && b[3] <= plotH
    const free = (b: Box) => inside(b) && !bubbles.some((bb, i) => pts[i].name !== name && hit(b, bb)) && !placed.some(pb => hit(b, pb))
    const pick = cands.find(c => free(c.box)) ?? cands[0]
    out[name] = pick.pl
    placed.push(pick.box)
  }
  return out
}

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
  const box = useRef<HTMLDivElement>(null)
  const [width, setWidth] = useState(1000)
  useEffect(() => {
    const el = box.current
    if (!el) return
    const ro = new ResizeObserver(() => setWidth(el.clientWidth))
    ro.observe(el); setWidth(el.clientWidth)
    return () => ro.disconnect()
  }, [])
  const labelled = [...launch.map(p => p.name), ...pts.filter(p => p.y >= 70 && p.q !== 'Launch next').sort((a, b) => b.y - a.y).map(p => p.name)]
  const places = placeLabels([...pts, ...vegas], [...labelled, ...vegas.map(p => p.name)], Math.max(width - 98, 300), 560 - 16 - 56 - 40, dom('x'), dom('y'))
  // Recharts passes the symbol's top-left corner plus its width/height, so aim at the centre
  const renderLabel = (props: { x?: number | string; y?: number | string; width?: number | string; height?: number | string; value?: unknown }) => {
    const name = String(props.value ?? '')
    const pl = places[name]
    if (!pl) return null
    const cx = Number(props.x) + Number(props.width ?? 0) / 2, cy = Number(props.y) + Number(props.height ?? 0) / 2
    return <text x={cx + pl.dx} y={cy + pl.dy} fontSize={11} fill="#111827" textAnchor={pl.anchor} style={{ paintOrder: 'stroke', stroke: '#ffffff', strokeWidth: 3 }}>{name}</text>
  }
  const qLabel = 'pointer-events-none absolute text-xs font-semibold uppercase tracking-wide'
  return (
    <div>
      <p className="mb-3 text-sm text-muted">
        <strong className="text-ink">Opportunity</strong> = demand pillar. <strong className="text-ink">Ease of entry</strong> = the other four pillars, re-weighted.
        Dashed lines are the medians of the 25 candidates. Bubble size = competitor crowding; the black diamond is the Las Vegas benchmark.
      </p>
      <div ref={box} className="relative h-[560px] rounded-lg border border-line p-2">
        <div className={`${qLabel} left-24 top-9 text-muted`}>Build case</div>
        <div className={`${qLabel} right-28 top-9 text-accent`}>Launch next</div>
        <div className={`${qLabel} bottom-24 left-24 text-muted`}>Deprioritize</div>
        <div className={`${qLabel} bottom-24 right-28 text-muted`}>Opportunistic</div>
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
              <LabelList dataKey="name" content={renderLabel} />
            </Scatter>
            <Scatter data={vegas} isAnimationActive={false} shape="diamond" fill="#111827">
              <LabelList dataKey="name" content={renderLabel} />
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
