export type Pillar = 'demand' | 'operating' | 'regulatory' | 'competition' | 'charging'
export const PILLARS: Pillar[] = ['demand', 'operating', 'regulatory', 'competition', 'charging']
export type Weights = Record<Pillar, number>

export interface SubSpec { weight: number; direction: number; label: string; unit: string }
export interface Competitor { competitor: string; status: string; platform_partner: string; first_public_date: string; source_url: string; source_title: string; as_of_date: string; confidence: string; is_operator: boolean }
export interface Regulation { tier: number; new_entrant_path: string; new_entrant_rationale: string; new_entrant_source_url: string; new_entrant_source_title: string; new_entrant_as_of_date: string; new_entrant_confidence: string; driverless_commercial_allowed: string; permit_body: string; key_law_or_rule: string; notes: string; source_url: string; source_title: string; as_of_date: string; confidence: string }

export interface Assumption { label: string; unit: string; value: number; low: number; high: number; higher_is_better: boolean; source_url: string; rationale: string }
export interface Econ {
  addressable_trips_per_day: number; fleet_vehicles: number; revenue_per_vehicle: number; miles_per_vehicle: number
  charging_cost_per_vehicle: number; opex_per_vehicle: number; contribution_per_vehicle: number; payback_years: number | null
  city_ride_hail_trips_year?: number
}
export interface Metro {
  metro: string; state: string; principal_city: string; benchmark: boolean
  raw: Record<string, number>
  sub_scores: Record<string, number>
  pillar_scores: Record<Pillar, number>
  total: number; totals: Record<string, number>; ranks: Record<string, number | null>
  opportunity: number; ease_of_entry: number; vegas_similarity: number
  demand_estimate?: { tpr_low: number; tpr_base: number; tpr_high: number; trips_low: number; trips_base: number; trips_high: number; city_pop: number }
  unit_economics?: { low: Econ; base: Econ; high: Econ }
  confidence?: number | null; median_rank?: number | null; wave?: number | null
  why: string[]; competitors: Competitor[]; regulation: Regulation
  nhtsa_incidents: { operating_entity: string; ads_incidents: number }[]
}

export interface Meta {
  assumptions?: Record<string, Assumption>
  demand_method?: { anchor_year: number; note: string }
  question: string; data_as_of: string; generated_at: string
  vintages: Record<string, string>
  weights: {
    scenarios: Record<string, Weights>; default_scenario: string
    pillars: Record<Pillar, { label: string; submetrics: Record<string, SubSpec> }>
    crowding_status_weights: Record<string, number>
  }
}
export interface Scored { meta: Meta; metros: Metro[] }
