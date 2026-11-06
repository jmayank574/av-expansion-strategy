-- One raw feature row per metro (26): mirrors pipeline/build_features.py
with crowd as (
    select c.metro, round(sum(w.weight), 6) as crowding
    from {{ ref('stg_competitors') }} c
    join {{ ref('stg_status_weights') }} w on w.status = c.status
    where c.is_operator <> 'true'
    group by c.metro
)
select
    m.metro,
    m.state,
    m.benchmark,
    ln(a.metro_pop)               as log_metro_pop,
    g.density_per_sqmi            as city_density,
    a.taxi_ridehail_share,
    a.no_vehicle_share,
    f.enplanements_per_resident,
    w.rain_days,
    w.snow_days,
    w.heat_days,
    r.tier                        as reg_tier,
    case r.new_entrant_path when 'fast' then 2 when 'moderate' then 1 when 'slow' then 0 end as new_entrant_score,
    coalesce(c.crowding, 0)       as crowding,
    e.commercial_cents_kwh        as elec_cents_kwh
from {{ ref('stg_metros') }} m
join {{ ref('stg_acs') }} a on a.metro = m.metro
join {{ ref('stg_gazetteer') }} g on g.metro = m.metro
join {{ ref('stg_faa') }} f on f.metro = m.metro
join {{ ref('stg_weather') }} w on w.metro = m.metro
join {{ ref('stg_eia') }} e on e.state = m.state
join {{ ref('stg_regulation') }} r on r.state = m.state
left join crowd c on c.metro = m.metro
