-- Percentile rank across the 25 candidates (average rank for ties, min=0, max=100).
-- The benchmark (Las Vegas) is interpolated on the candidates' curve and never ranked.
with cand as (
    select submetric, value,
           rank() over (partition by submetric order by value)
             + (count(*) over (partition by submetric, value) - 1) / 2.0 as rank_avg,
           count(*) over (partition by submetric) as n
    from {{ ref('int_features_long') }}
    where not benchmark
),
curve as (
    select submetric, value, avg((rank_avg - 1) / (n - 1) * 100) as pct
    from cand
    group by submetric, value
),
bounds as (
    select l.metro, l.benchmark, l.submetric, l.value,
           (select max(c.value) from curve c where c.submetric = l.submetric and c.value <= l.value) as lo,
           (select min(c.value) from curve c where c.submetric = l.submetric and c.value >= l.value) as hi
    from {{ ref('int_features_long') }} l
),
interp as (
    select b.metro, b.benchmark, b.submetric, b.value, b.lo, b.hi, cl.pct as p_lo, ch.pct as p_hi
    from bounds b
    left join curve cl on cl.submetric = b.submetric and cl.value = b.lo
    left join curve ch on ch.submetric = b.submetric and ch.value = b.hi
)
select i.metro, i.benchmark, i.submetric,
       case when w.direction = 1 then pct else 100 - pct end as sub_score
from (
    select *,
           case when lo is null then p_hi
                when hi is null then p_lo
                when hi = lo then p_lo
                else p_lo + (value - lo) / (hi - lo) * (p_hi - p_lo) end as pct
    from interp
) i
join {{ ref('stg_submetric_weights') }} w on w.submetric = i.submetric
