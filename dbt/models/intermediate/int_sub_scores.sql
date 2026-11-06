-- Sub-metric scores, mirroring pipeline/score.py.
--   percentile (default): rank across the 25 candidates (average rank for ties, min=0, max=100); the benchmark (Las Vegas)
--                         is interpolated on the candidates' curve and never ranked.
--   minmax0 (crowding):   value / max over the candidates * 100, clipped to 0-100. Crowding has few distinct values, so a percentile
--                         rank jumps when one competitor's status changes; min-max moves in proportion to the change.
-- Direction -1 flips the score (100 - score).
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
mx as (
    select submetric, max(value) as max_value
    from {{ ref('int_features_long') }}
    where not benchmark
    group by submetric
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
),
scaled as (
    select i.metro, i.benchmark, i.submetric,
           case when w.normalization = 'minmax0'
                then least(greatest(i.value / mx.max_value * 100, 0), 100)
                when i.lo is null then i.p_hi
                when i.hi is null then i.p_lo
                when i.hi = i.lo then i.p_lo
                else i.p_lo + (i.value - i.lo) / (i.hi - i.lo) * (i.p_hi - i.p_lo) end as sc
    from interp i
    join {{ ref('stg_submetric_weights') }} w on w.submetric = i.submetric
    join mx on mx.submetric = i.submetric
)
select s.metro, s.benchmark, s.submetric,
       case when w.direction = 1 then s.sc else 100 - s.sc end as sub_score
from scaled s
join {{ ref('stg_submetric_weights') }} w on w.submetric = s.submetric
