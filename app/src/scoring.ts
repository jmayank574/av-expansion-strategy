import type { Metro, Meta, Pillar, Weights } from './types'
import { PILLARS } from './types'

/** Pillar score = weighted mean of the pillar's normalized sub-scores. */
export function pillarScores(m: Metro, meta: Meta): Record<Pillar, number> {
  const out = {} as Record<Pillar, number>
  for (const p of PILLARS) {
    const subs = meta.weights.pillars[p].submetrics
    let num = 0, den = 0
    for (const [k, spec] of Object.entries(subs)) { num += spec.weight * m.sub_scores[k]; den += spec.weight }
    out[p] = num / den
  }
  return out
}

export function total(p: Record<Pillar, number>, w: Weights): number {
  let num = 0, den = 0
  for (const k of PILLARS) { num += w[k] * p[k]; den += w[k] }
  return den ? num / den : 0
}

/** Ease of entry = weighted mean of the four non-demand pillars, weights re-normalized. */
export function ease(p: Record<Pillar, number>, w: Weights): number {
  let num = 0, den = 0
  for (const k of PILLARS) if (k !== 'demand') { num += w[k] * p[k]; den += w[k] }
  return den ? num / den : 0
}

export interface Row { m: Metro; pillars: Record<Pillar, number>; total: number; ease: number; opportunity: number; rank: number | null }

export function scoreAll(metros: Metro[], meta: Meta, w: Weights): Row[] {
  const rows: Row[] = metros.map(m => {
    const pillars = pillarScores(m, meta)
    return { m, pillars, total: total(pillars, w), ease: ease(pillars, w), opportunity: pillars.demand, rank: null }
  })
  const cand = rows.filter(r => !r.m.benchmark)
  for (const r of cand) r.rank = 1 + cand.filter(o => o.total > r.total + 1e-9).length   // ties share the best rank (matches pandas 'min')
  return rows
}

export function median(xs: number[]): number {
  const s = [...xs].sort((a, b) => a - b), n = s.length
  return n % 2 ? s[(n - 1) / 2] : (s[n / 2 - 1] + s[n / 2]) / 2
}

/** Move one slider to v and rescale the others so the weights stay integers summing to 100. */
export function setWeight(w: Weights, key: Pillar, v: number): Weights {
  v = Math.max(0, Math.min(100, Math.round(v)))
  const others = PILLARS.filter(k => k !== key)
  const sumO = others.reduce((a, k) => a + w[k], 0)
  const raw = others.map(k => (sumO ? w[k] * (100 - v) / sumO : (100 - v) / others.length))
  const floor = raw.map(Math.floor)
  let left = 100 - v - floor.reduce((a, b) => a + b, 0)
  const order = raw.map((x, i) => [x - Math.floor(x), i] as const).sort((a, b) => b[0] - a[0])
  for (const [, i] of order) { if (left <= 0) break; floor[i]++; left-- }
  const out = { ...w, [key]: v } as Weights
  others.forEach((k, i) => { out[k] = floor[i] })
  return out
}
