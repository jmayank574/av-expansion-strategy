{% set scenarios = ['balanced', 'fast_growth', 'low_risk', 'capital_light'] %}
with pillars as (
    select metro, benchmark,
           max(case when pillar = 'demand' then pillar_score end)      as demand,
           max(case when pillar = 'operating' then pillar_score end)   as operating,
           max(case when pillar = 'regulatory' then pillar_score end)  as regulatory,
           max(case when pillar = 'competition' then pillar_score end) as competition,
           max(case when pillar = 'charging' then pillar_score end)    as charging
    from {{ ref('int_pillar_scores') }}
    group by metro, benchmark
),
totals as (
    select p.metro, p.benchmark, p.demand, p.operating, p.regulatory, p.competition, p.charging,
    {% for s in scenarios %}
        (select sum(w.weight * case w.pillar when 'demand' then p.demand when 'operating' then p.operating
                                         when 'regulatory' then p.regulatory when 'competition' then p.competition
                                         else p.charging end) / sum(w.weight)
         from {{ ref('stg_scenario_weights') }} w where w.scenario = '{{ s }}') as total_{{ s }},
    {% endfor %}
        (select sum(w.weight * case w.pillar when 'operating' then p.operating when 'regulatory' then p.regulatory
                                         when 'competition' then p.competition else p.charging end) / sum(w.weight)
         from {{ ref('stg_scenario_weights') }} w where w.scenario = 'balanced' and w.pillar <> 'demand') as ease_of_entry
    from pillars p
)
select *, demand as opportunity,
{% for s in scenarios %}
    case when not benchmark then rank() over (partition by benchmark order by round(total_{{ s }}, 9) desc) end as rank_{{ s }}
    {% if not loop.last %},{% endif %}
{% endfor %}
from totals
