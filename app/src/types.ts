export type Pillar = 'demand' | 'operating' | 'regulatory' | 'competition' | 'charging'
export const PILLARS: Pillar[] = ['demand', 'operating', 'regulatory', 'competition', 'charging']
export type Weights = Record<Pillar, number>

export interface SubSpec { weight: number; direction: number; label: string; unit: string }
export interface Competitor { competitor: string; status: string; platform_partner: string; first_public_date: string; source_url: string; source_title: string; as_of_date: string; confidence: string }
export interface Regulation { tier: number; driverless_commercial_allowed: string; permit_body: string; key_law_or_rule: string; notes: string; source_url: string; source_title: string; as_of_date: string; confidence: string }

export interface Metro {
  metro: string; state: string; principal_city: string; benchmark: boolean
  raw: Record<string, number>
  sub_scores: Record<string, number>
  pillar_scores: Record<Pillar, number>
  total: number; totals: Record<string, number>; ranks: Record<string, number | null>
  opportunity: number; ease_of_entry: number; vegas_similarity: number
  confidence?: number | null; median_rank?: number | null
  why: string[]; competitors: Competitor[]; regulation: Regulation
  nhtsa_incidents: { operating_entity: string; ads_incidents: number }[]
}

export interface Meta {
  question: string; data_as_of: string; generated_at: string
  vintages: Record<string, string>
  weights: {
    scenarios: Record<string, Weights>; default_scenario: string
    pillars: Record<Pillar, { label: string; submetrics: Record<string, SubSpec> }>
    crowding_status_weights: Record<string, number>
  }
}
export interface Scored { meta: Meta; metros: Metro[] }
