select s.metro, s.benchmark, w.pillar,
       sum(s.sub_score * w.weight) / sum(w.weight) as pillar_score
from {{ ref('int_sub_scores') }} s
join {{ ref('stg_submetric_weights') }} w on w.submetric = s.submetric
group by s.metro, s.benchmark, w.pillar
