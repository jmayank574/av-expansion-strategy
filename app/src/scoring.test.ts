import { describe, it, expect } from 'vitest'
import { readFileSync } from 'node:fs'
import type { Scored } from './types'
import { scoreAll, setWeight } from './scoring'

const data: Scored = JSON.parse(readFileSync(new URL('../public/metros_scored.json', import.meta.url), 'utf-8'))
const w = data.meta.weights.scenarios[data.meta.weights.default_scenario]

describe('browser scoring matches Python (balanced)', () => {
  const rows = scoreAll(data.metros, data.meta, w)
  it('totals match to 2 decimals', () => {
    for (const r of rows) expect(r.total, r.m.metro).toBeCloseTo(r.m.total, 2)
  })
  it('pillar scores and ease of entry match', () => {
    for (const r of rows) {
      for (const p of Object.keys(r.pillars) as (keyof typeof r.pillars)[]) expect(r.pillars[p], r.m.metro + p).toBeCloseTo(r.m.pillar_scores[p], 2)
      expect(r.ease, r.m.metro).toBeCloseTo(r.m.ease_of_entry, 2)
    }
  })
  it('ranks match for every scenario', () => {
    for (const [name, sw] of Object.entries(data.meta.weights.scenarios)) {
      for (const r of scoreAll(data.metros, data.meta, sw)) expect(r.rank, name + r.m.metro).toBe(r.m.ranks[name])
    }
  })
})

describe('setWeight', () => {
  it('keeps weights summing to 100', () => {
    let cur = { ...w }
    for (const [k, v] of [['demand', 80], ['charging', 33], ['operating', 0], ['regulatory', 100], ['competition', 7]] as const) {
      cur = setWeight(cur, k, v)
      expect(Object.values(cur).reduce((a, b) => a + b, 0)).toBe(100)
      expect(cur[k]).toBe(v)
    }
  })
})
